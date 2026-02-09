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
        
        for attempt in range(1, self.config.ssh_retry_count + 1):
            try:
                logger.info(
                    f"SSH connecting to {self.config.ssh_host}:{self.config.ssh_port} "
                    f"(attempt {attempt}/{self.config.ssh_retry_count})"
                )
                
                self._client = paramiko.SSHClient()
                self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                
                # Load private key
                private_key = paramiko.RSAKey.from_private_key_file(
                    self.config.ssh_key_path
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
                
                logger.info("SSH connected successfully")
                return
                
            except paramiko.AuthenticationException as e:
                logger.error(f"SSH authentication failed: {e}")
                raise SSHConnectionError(f"Authentication failed: {e}")
                
            except paramiko.SSHException as e:
                logger.warning(f"SSH connection attempt {attempt} failed: {e}")
                
                if attempt < self.config.ssh_retry_count:
                    delay = self.config.ssh_retry_delay * attempt
                    logger.info(f"Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                else:
                    raise SSHConnectionError(f"Failed after {attempt} attempts: {e}")
                    
            except Exception as e:
                logger.error(f"Unexpected SSH error: {e}")
                raise SSHConnectionError(f"Unexpected error: {e}")
    
    async def disconnect(self) -> None:
        """Zamyka połączenie SSH."""
        if self._sftp:
            self._sftp.close()
            self._sftp = None
            
        if self._client:
            self._client.close()
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
            stdin, stdout, stderr = self._client.exec_command(
                command,
                timeout=self.config.ssh_timeout
            )
            
            # Read output
            stdout_data = stdout.read().decode('utf-8', errors='ignore')
            stderr_data = stderr.read().decode('utf-8', errors='ignore')
            exit_code = stdout.channel.recv_exit_status()
            
            duration = time.time() - start_time
            
            return CommandResult(
                stdout=stdout_data,
                stderr=stderr_data,
                exit_code=exit_code,
                duration_seconds=duration
            )
            
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
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
        
        start_time = time.time()
        tar_filename = f"theme_scan_{uuid.uuid4().hex[:8]}.tar.gz"
        local_tar_path = local_path / tar_filename
        
        try:
            # Ensure local directory exists
            local_path.mkdir(parents=True, exist_ok=True)
            
            await self.connect()
            
            # Get SFTP client
            if self._sftp is None:
                self._sftp = self._client.open_sftp()
            
            # Create tar on remote server
            remote_parent = str(Path(remote_path).parent)
            remote_name = Path(remote_path).name
            
            # Create tar.gz on remote
            tar_command = (
                f"cd {remote_parent} && "
                f"tar czf /tmp/{tar_filename} {remote_name} 2>/dev/null"
            )
            
            logger.info(f"Creating tar archive on remote: {tar_command}")
            result = await self.execute_command(tar_command)
            
            if result.exit_code != 0:
                return DownloadResult(
                    success=False,
                    error=f"Failed to create tar: {result.stderr}"
                )
            
            # Download tar file
            remote_tar = f"/tmp/{tar_filename}"
            logger.info(f"Downloading {remote_tar} to {local_tar_path}")
            self._sftp.get(remote_tar, str(local_tar_path))
            
            # Cleanup remote tar
            await self.execute_command(f"rm -f {remote_tar}")
            
            # Extract locally
            logger.info(f"Extracting to {local_path}")
            with tarfile.open(local_tar_path, 'r:gz') as tar:
                tar.extractall(local_path)
            
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
                f"Download completed: {file_count} files, "
                f"{total_size / 1024:.1f} KB in {duration:.1f}s"
            )
            
            return DownloadResult(
                success=True,
                local_path=str(extracted_path),
                file_count=file_count,
                size_bytes=total_size,
                duration_seconds=duration
            )
            
        except Exception as e:
            logger.error(f"Download failed: {e}")
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
            logger.info(f"Cleaned up {local_path}")