"""
SSH Connector z obsługą bulk download.

Optymalizacja: zamiast wielu operacji cat, pobiera cały folder
jako tar.gz i rozpakowuje lokalnie.

Author: Jadzia Architect Team
Version: 1.1
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys
import shutil
import tarfile
import time
import uuid
from pathlib import Path
from typing import Optional

import paramiko

from .config import ExplorerConfig, get_config
from .models import CommandResult, DownloadResult

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def _force_wp_explorer_logging() -> None:
    """
    Force WPExplorer logs to stdout (systemd StandardOutput) and to a dedicated file.
    This bypasses any global INFO-only logging configuration in the main app and makes
    diagnostics visible in /root/jadzia/logs/jadzia.log and /root/jadzia/logs/wp_explorer.log.
    """
    try:
        root = logging.getLogger()
        if not getattr(root, "_wp_explorer_forced", False):
            # Only configure root if it has no handlers yet (avoid duplicate output).
            if not root.handlers:
                logging.basicConfig(
                    level=logging.DEBUG,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                )
            setattr(root, "_wp_explorer_forced", True)

        log_file = os.getenv("WP_EXPLORER_LOG_FILE")
        if not log_file:
            log_file = "/root/jadzia/logs/wp_explorer.log" if os.name != "nt" else "logs/wp_explorer.log"

        try:
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass

        fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        # stdout handler (captured by systemd StandardOutput -> logs/jadzia.log)
        if not any(isinstance(h, logging.StreamHandler) and getattr(h, "stream", None) is sys.stdout for h in logger.handlers):
            sh = logging.StreamHandler(sys.stdout)
            sh.setLevel(logging.DEBUG)
            sh.setFormatter(fmt)
            logger.addHandler(sh)

        # file handler
        if log_file:
            abs_log_file = os.path.abspath(log_file)
            if not any(isinstance(h, logging.FileHandler) and getattr(h, "baseFilename", None) == abs_log_file for h in logger.handlers):
                fh = logging.FileHandler(log_file)
                fh.setLevel(logging.DEBUG)
                fh.setFormatter(fmt)
                logger.addHandler(fh)

        # Avoid double-logging via root handlers.
        logger.propagate = False
        logger.debug("[WP_EXPLORER] Forced logging initialized (ssh_connector)")
    except Exception:
        # Never fail import due to logging diagnostics
        pass


_force_wp_explorer_logging()


def _sh_quote(value: str) -> str:
    """
    Quote a string for POSIX shell using single-quotes.
    Safe for paths/filenames (prevents spaces and metacharacters from breaking command).
    """
    if value is None:
        return "''"
    return "'" + value.replace("'", "'\"'\"'") + "'"


class SSHConnectionError(Exception):
    """Błąd połączenia SSH."""
    pass


class SSHTimeoutError(Exception):
    """Timeout operacji SSH."""
    pass


class SecurityError(Exception):
    """Naruszenie bezpieczeństwa."""
    pass


class SSHConnector:
    """
    SSH Connector z obsługą bulk download.
    
    Używa Paramiko do połączenia SSH i optymalizuje transfer
    przez pobieranie całych katalogów jako tar.gz.
    
    Attributes:
        config: Konfiguracja połączenia
        _client: Instancja SSHClient (lazy init)
        
    Example:
        connector = SSHConnector()
        result = await connector.download_directory_as_tar(
            "/path/to/theme",
            Path("/tmp/scan_123")
        )
    """
    
    # Dozwolone ścieżki bazowe (security)
    ALLOWED_BASE_PATHS = [
        "/home/uhqsycwpjz/domains/",
        "/var/www/",
    ]
    
    # Zabronione wzorce w ścieżkach
    FORBIDDEN_PATTERNS = [
        "..",           # Path traversal
        "~",            # Home directory
        "$(",           # Command substitution
        "`",            # Backtick execution
        ";",            # Command chaining
        "|",            # Pipe
        "&",            # Background/AND
        ">",            # Redirect
        "<",            # Redirect
    ]
    
    def __init__(self, config: Optional[ExplorerConfig] = None):
        """
        Inicjalizuje connector.
        
        Args:
            config: Konfiguracja (opcjonalna, używa domyślnej jeśli brak)
        """
        self.config = config or get_config()
        self._client: Optional[paramiko.SSHClient] = None
        self._sftp: Optional[paramiko.SFTPClient] = None

    async def _reset_connection(self) -> None:
        """Hard reset SSH/SFTP connection (used after transport-level failures)."""
        try:
            await self.disconnect()
        except Exception:
            logger.exception("Failed to disconnect cleanly during reset")
        self._client = None
        self._sftp = None

    async def _ensure_sftp(self) -> None:
        """Ensure SFTP channel is open (reopens if missing)."""
        await self.connect()
        if self._client is None:
            raise SSHConnectionError("SSH client is not connected")
        if self._sftp is None:
            logger.debug("Opening new SFTP session")
            self._sftp = self._client.open_sftp()
    
    def _validate_path(self, path: str) -> bool:
        """
        Sprawdza czy ścieżka jest bezpieczna.
        
        Args:
            path: Ścieżka do walidacji
            
        Returns:
            True jeśli bezpieczna
            
        Raises:
            SecurityError: Gdy ścieżka jest niebezpieczna
        """
        # Check for forbidden patterns
        for pattern in self.FORBIDDEN_PATTERNS:
            if pattern in path:
                raise SecurityError(f"Forbidden pattern '{pattern}' in path: {path}")
        
        # Check base path
        if not any(path.startswith(base) for base in self.ALLOWED_BASE_PATHS):
            raise SecurityError(f"Path not in allowed base paths: {path}")
        
        return True
    
    async def connect(self) -> None:
        """
        Nawiązuje połączenie SSH.
        
        Raises:
            SSHConnectionError: Gdy nie można połączyć
        """
        if self._client is not None:
            return

        key_path = os.path.abspath(os.path.expanduser(self.config.ssh_key_path))
        if not os.path.isfile(key_path):
            raise SSHConnectionError(
                f"SSH key not found: {key_path}. Cannot connect to {self.config.ssh_host} without key. "
                "Add the key file or set SSH_KEY_PATH / CYBERFOLKS_KEY_PATH. Recommended: chmod 600 for the key."
            )

        for attempt in range(1, self.config.ssh_retry_count + 1):
            try:
                logger.info(
                    "SSH connecting to %s:%s (attempt %d/%d)",
                    self.config.ssh_host, self.config.ssh_port,
                    attempt, self.config.ssh_retry_count,
                )
                
                self._client = paramiko.SSHClient()
                self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                
                # Load private key (support RSA / ED25519 / ECDSA)
                private_key = None
                key_errors = []
                for key_cls in (
                    paramiko.RSAKey,
                    getattr(paramiko, "Ed25519Key", None),
                    paramiko.ECDSAKey,
                ):
                    if key_cls is None:
                        continue
                    try:
                        private_key = key_cls.from_private_key_file(self.config.ssh_key_path)
                        break
                    except Exception as e:
                        key_errors.append(f"{getattr(key_cls, '__name__', str(key_cls))}: {e}")
                if private_key is None:
                    raise SSHConnectionError(
                        f"Failed to load private key from {self.config.ssh_key_path}. Errors: "
                        + "; ".join(key_errors)
                    )
                
                # Connect
                self._client.connect(
                    hostname=self.config.ssh_host,
                    port=self.config.ssh_port,
                    username=self.config.ssh_user,
                    pkey=private_key,
                    timeout=self.config.ssh_timeout,
                    allow_agent=False,
                    look_for_keys=False,
                )

                # Transport keepalive reduces risk of silent disconnects mid-transfer.
                try:
                    transport = self._client.get_transport()
                    if transport:
                        transport.set_keepalive(30)
                except Exception:
                    logger.exception("Failed to set SSH keepalive")
                
                logger.info("SSH connected successfully")
                return
                
            except paramiko.AuthenticationException as e:
                logger.error("SSH authentication failed: %s", e)
                raise SSHConnectionError(f"Authentication failed: {e}")
                
            except paramiko.SSHException as e:
                logger.exception("SSH connection attempt %d failed", attempt)
                
                if attempt < self.config.ssh_retry_count:
                    delay = self.config.ssh_retry_delay * attempt
                    logger.info("Retrying in %ss...", delay)
                    await asyncio.sleep(delay)
                else:
                    raise SSHConnectionError(f"Failed after {attempt} attempts: {e}")
                    
            except Exception as e:
                logger.exception("Unexpected SSH error")
                raise SSHConnectionError(f"Unexpected error: {e}")
    
    async def disconnect(self) -> None:
        """Zamyka połączenie SSH."""
        if self._sftp:
            try:
                self._sftp.close()
            except Exception:
                logger.exception("Failed to close SFTP session cleanly")
            self._sftp = None
            
        if self._client:
            try:
                self._client.close()
            except Exception:
                logger.exception("Failed to close SSH client cleanly")
            self._client = None
            logger.info("SSH disconnected")
    
    async def execute_command(self, command: str) -> CommandResult:
        """
        Wykonuje komendę SSH.
        
        Args:
            command: Komenda do wykonania
            
        Returns:
            CommandResult z stdout, stderr, exit_code
        """
        await self.connect()
        
        start_time = time.time()
        
        try:
            logger.debug("[SSH] exec_command: %s", command)
            stdin, stdout, stderr = self._client.exec_command(
                command,
                timeout=self.config.ssh_timeout
            )
            
            # Read output
            stdout_data = stdout.read().decode('utf-8', errors='ignore')
            stderr_data = stderr.read().decode('utf-8', errors='ignore')
            exit_code = stdout.channel.recv_exit_status()
            
            duration = time.time() - start_time

            logger.debug(
                "[SSH] exec_command completed (exit_code=%s, stdout_len=%d, stderr_len=%d, duration=%.2fs)",
                exit_code, len(stdout_data), len(stderr_data), duration,
            )
            
            return CommandResult(
                stdout=stdout_data,
                stderr=stderr_data,
                exit_code=exit_code,
                duration_seconds=duration
            )
            
        except Exception as e:
            logger.exception("Command execution failed: %s", command)
            raise SSHTimeoutError(f"Command failed: {e}")
    
    async def download_directory_as_tar(
        self,
        remote_path: str,
        local_path: Path
    ) -> DownloadResult:
        """
        Pobiera cały katalog jako tar.gz i rozpakowuje lokalnie.
        
        Ta metoda jest ~10x szybsza niż pobieranie plików pojedynczo
        przez wiele połączeń SSH.
        
        Args:
            remote_path: Ścieżka katalogu na serwerze
            local_path: Lokalna ścieżka do rozpakowania
            
        Returns:
            DownloadResult z informacjami o pobraniu
            
        Raises:
            SecurityError: Gdy ścieżka jest niebezpieczna
            SSHConnectionError: Gdy nie można połączyć
        """
        # Security check
        self._validate_path(remote_path)

        logger.info("[WP_EXPLORER] Starting download: %s", remote_path)
        
        start_time = time.time()
        tar_filename = f"theme_scan_{uuid.uuid4().hex[:8]}.tar.gz"
        local_tar_path = local_path / tar_filename
        
        try:
            # Ensure local directory exists
            local_path.mkdir(parents=True, exist_ok=True)
            
            await self._ensure_sftp()
            
            # Create tar on remote server
            remote_parent = str(Path(remote_path).parent)
            remote_name = Path(remote_path).name
            
            # Create tar.gz on remote
            # Do NOT redirect stderr: we want diagnostics in logs.
            tar_command = (
                f"tar -czf {_sh_quote(f'/tmp/{tar_filename}')} "
                f"-C {_sh_quote(remote_parent)} {_sh_quote(remote_name)}"
            )
            
            logger.info("Creating tar archive on remote: %s", tar_command)
            result = await self.execute_command(tar_command)
            logger.debug("[WP_EXPLORER] Tar result: exit=%s, stderr=%s", result.exit_code, result.stderr[:200])
            
            if result.exit_code != 0:
                return DownloadResult(
                    success=False,
                    error=f"Failed to create tar (exit={result.exit_code}): {result.stderr or result.stdout}"
                )
            
            # Download tar file
            remote_tar = f"/tmp/{tar_filename}"
            try:
                remote_stat = self._sftp.stat(remote_tar)
                remote_size = int(getattr(remote_stat, "st_size", 0) or 0)
            except Exception:
                logger.exception("Failed to stat remote tar: %s", remote_tar)
                remote_size = 0

            logger.info(
                "Downloading %s to %s (remote_size=%d bytes)",
                remote_tar, local_tar_path, remote_size,
            )

            # Retry download if transport drops mid-stream.
            download_ok = False
            last_exc: Optional[Exception] = None
            for attempt in range(1, self.config.ssh_retry_count + 1):
                try:
                    await self._ensure_sftp()
                    self._sftp.get(remote_tar, str(local_tar_path))
                    local_size = local_tar_path.stat().st_size if local_tar_path.exists() else 0
                    if remote_size and local_size != remote_size:
                        raise IOError(
                            f"Downloaded size mismatch (local={local_size}, remote={remote_size})"
                        )
                    download_ok = True
                    break
                except Exception as e:
                    last_exc = e
                    logger.exception(
                        "SFTP download attempt %d/%d failed", attempt, self.config.ssh_retry_count,
                    )
                    # reset connection and retry
                    await self._reset_connection()
                    await asyncio.sleep(self.config.ssh_retry_delay * attempt)

            if not download_ok:
                return DownloadResult(
                    success=False,
                    error=f"Failed after {self.config.ssh_retry_count} attempts: {last_exc}",
                    duration_seconds=time.time() - start_time,
                )
            
            # Cleanup remote tar
            try:
                await self.execute_command(f"rm -f {_sh_quote(remote_tar)}")
            except Exception:
                logger.exception("Failed to cleanup remote tar: %s", remote_tar)
            
            # Extract locally
            logger.info("Extracting to %s", local_path)
            try:
                with tarfile.open(local_tar_path, 'r:gz') as tar:
                    tar.extractall(local_path)
            except Exception:
                local_size = local_tar_path.stat().st_size if local_tar_path.exists() else 0
                logger.exception(
                    "Extraction failed (local_tar=%s, local_size=%d, remote_size=%d)",
                    local_tar_path, local_size, remote_size,
                )
                raise
            
            # Count files and size
            extracted_path = local_path / remote_name
            file_count = 0
            total_size = 0
            
            for file_path in extracted_path.rglob('*'):
                if file_path.is_file():
                    file_count += 1
                    total_size += file_path.stat().st_size
            
            duration = time.time() - start_time
            
            logger.info(
                "Download completed: %d files, %.1f KB in %.1fs",
                file_count, total_size / 1024, duration,
            )
            
            return DownloadResult(
                success=True,
                local_path=str(extracted_path),
                file_count=file_count,
                size_bytes=total_size,
                duration_seconds=duration
            )
            
        except Exception as e:
            logger.exception("Download failed for remote_path=%s", remote_path)
            return DownloadResult(
                success=False,
                error=str(e),
                duration_seconds=time.time() - start_time
            )
            
        finally:
            # Cleanup local tar file
            if local_tar_path.exists():
                local_tar_path.unlink()
    
    async def file_exists(self, path: str) -> bool:
        """Sprawdza czy plik istnieje na serwerze."""
        self._validate_path(path)
        
        result = await self.execute_command(f"test -f {path} && echo 'exists'")
        return result.stdout.strip() == 'exists'
    
    async def read_file(self, path: str) -> str:
        """
        Czyta zawartość pliku z serwera.
        
        Args:
            path: Ścieżka do pliku
            
        Returns:
            Zawartość pliku jako string
        """
        self._validate_path(path)
        
        result = await self.execute_command(f"cat {path}")
        
        if result.exit_code != 0:
            raise FileNotFoundError(f"Cannot read file: {path}")
        
        return result.stdout
    
    def cleanup_local(self, local_path: Path) -> None:
        """
        Usuwa tymczasowe pliki lokalne po skanowaniu.
        
        Args:
            local_path: Ścieżka do usunięcia
        """
        if local_path.exists() and str(local_path).startswith('/tmp/'):
            shutil.rmtree(local_path)
            logger.info("Cleaned up %s", local_path)