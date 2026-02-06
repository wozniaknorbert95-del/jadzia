"""
Telegram Message Formatter
===========================

Handles:
- MarkdownV2 escaping
- Message splitting (Telegram 4096 char limit)
- Diff formatting for mobile readability
- User-friendly error messages
"""

import re
from typing import List, Dict, Any


# ═══════════════════════════════════════════════════════════════
# MARKDOWN V2 ESCAPING
# ═══════════════════════════════════════════════════════════════

# Characters that need escaping in Telegram MarkdownV2
# Source: https://core.telegram.org/bots/api#markdownv2-style
ESCAPE_CHARS = r'_*[]()~`>#+=|{}.!'


def escape_markdown_v2(text: str, preserve_code_blocks: bool = True) -> str:
    """
    Escape special characters for Telegram MarkdownV2.
    
    Args:
        text: Raw text to escape
        preserve_code_blocks: If True, don't escape content inside ``` blocks
    
    Returns:
        Escaped text safe for MarkdownV2
    
    Example:
        >>> escape_markdown_v2("Hello (world)!")
        'Hello \\(world\\)\\!'
    """
    if not text:
        return ""
    
    if preserve_code_blocks:
        # Split on code blocks (``` ... ```)
        parts = re.split(r'(```[\s\S]*?```|`[^`]+`)', text)
        escaped_parts = []
        
        for i, part in enumerate(parts):
            if part.startswith('```') or part.startswith('`'):
                # Code block - keep as is
                escaped_parts.append(part)
            else:
                # Regular text - escape special chars
                escaped = re.sub(
                    f'([{re.escape(ESCAPE_CHARS)}])',
                    r'\\\1',
                    part
                )
                escaped_parts.append(escaped)
        
        return ''.join(escaped_parts)
    else:
        # Escape all special chars
        return re.sub(
            f'([{re.escape(ESCAPE_CHARS)}])',
            r'\\\1',
            text
        )


# ═══════════════════════════════════════════════════════════════
# DIFF FORMATTING
# ═══════════════════════════════════════════════════════════════

def format_diff_for_telegram(diff: str, filename: str) -> str:
    """
    Format unified diff for Telegram display.
    Uses plain code blocks for maximum compatibility.
    
    Args:
        diff: Unified diff string
        filename: Name of file being modified
    
    Returns:
        Telegram-formatted diff in code block
    
    Note:
        We use plain ``` blocks instead of trying to colorize because:
        - Telegram doesn't support syntax highlighting
        - Emoji colorization (✅/❌) is hard to read on mobile
        - Simple is better for diffs
    """
    # Truncate very long diffs
    MAX_DIFF_LENGTH = 3000
    if len(diff) > MAX_DIFF_LENGTH:
        lines = diff.split('\n')
        truncated_lines = lines[:50]  # First 50 lines
        diff = '\n'.join(truncated_lines)
        diff += f"\n\n... (truncated, {len(lines) - 50} more lines)"
    
    # Plain code block with filename header
    return f"**{escape_markdown_v2(filename)}**\n```\n{diff}\n```"


# ═══════════════════════════════════════════════════════════════
# MESSAGE SPLITTING
# ═══════════════════════════════════════════════════════════════

TELEGRAM_MAX_LENGTH = 4096


def split_long_message(text: str, max_length: int = TELEGRAM_MAX_LENGTH) -> List[str]:
    """
    Split long message into chunks respecting Telegram limits.
    
    Strategy:
    1. Try to split on paragraph boundaries (\\n\\n)
    2. If paragraph too long, split on sentence boundaries (\\n)
    3. If sentence too long, split on word boundaries
    4. Preserve code blocks (don't split inside ```)
    
    Args:
        text: Text to split
        max_length: Maximum length per chunk (default 4096)
    
    Returns:
        List of message chunks
    """
    if len(text) <= max_length:
        return [text]
    
    chunks = []
    current_chunk = ""
    
    # Split on paragraphs first
    paragraphs = text.split('\n\n')
    
    for para in paragraphs:
        # Check if adding this paragraph exceeds limit
        test_chunk = current_chunk + ('\n\n' if current_chunk else '') + para
        
        if len(test_chunk) <= max_length:
            current_chunk = test_chunk
        else:
            # Current chunk is full, save it
            if current_chunk:
                chunks.append(current_chunk)
            
            # If paragraph itself is too long, split it further
            if len(para) > max_length:
                # Split on sentences (lines)
                lines = para.split('\n')
                temp_chunk = ""
                
                for line in lines:
                    test_line = temp_chunk + ('\n' if temp_chunk else '') + line
                    
                    if len(test_line) <= max_length:
                        temp_chunk = test_line
                    else:
                        if temp_chunk:
                            chunks.append(temp_chunk)
                        
                        # If single line is too long, split on words
                        if len(line) > max_length:
                            words = line.split(' ')
                            word_chunk = ""
                            
                            for word in words:
                                test_word = word_chunk + (' ' if word_chunk else '') + word
                                
                                if len(test_word) <= max_length:
                                    word_chunk = test_word
                                else:
                                    if word_chunk:
                                        chunks.append(word_chunk)
                                    word_chunk = word
                            
                            if word_chunk:
                                temp_chunk = word_chunk
                        else:
                            temp_chunk = line
                
                if temp_chunk:
                    current_chunk = temp_chunk
            else:
                current_chunk = para
    
    # Add remaining chunk
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks


def add_part_indicators(chunks: List[str]) -> List[str]:
    """
    Add "Part X/Y" indicators to chunks.
    
    Args:
        chunks: List of message chunks
    
    Returns:
        Chunks with part indicators
    """
    if len(chunks) <= 1:
        return chunks
    
    total = len(chunks)
    numbered_chunks = []
    
    for i, chunk in enumerate(chunks, start=1):
        # Add part indicator at the beginning
        indicator = f"*\\[Część {i}/{total}\\]*\n\n"
        numbered_chunks.append(indicator + chunk)
    
    return numbered_chunks


# ═══════════════════════════════════════════════════════════════
# ERROR MESSAGES
# ═══════════════════════════════════════════════════════════════

ERROR_MESSAGES = {
    "unauthorized": "🔒 Błąd autoryzacji webhoka\\. Skontaktuj się z administratorem\\.",
    "forbidden": "⛔ Nie masz dostępu do JADZIA\\. Twój User ID: `{user_id}`",
    "locked": "⏳ Agent jest zajęty inną operacją\\. Spróbuj ponownie za {retry_after} sekund\\.",
    "llm_error": "❌ Błąd komunikacji z Claude API\\. Spróbuj ponownie za moment\\.",
    "ssh_error": "🔌 Nie mogę połączyć się z serwerem\\. Sprawdzam status\\.\\.\\.",
    "internal": "💥 Wystąpił niespodziewany błąd\\.\n\nKod operacji: `{operation_id}`",
    "timeout": "⏱️ Operacja przekroczyła limit czasu\\. Spróbuj ponownie z prostszym zadaniem\\.",
    "invalid_input": "❓ Nie rozumiem polecenia\\. Napisz `/help` aby zobaczyć dostępne komendy\\.",
}


def format_error_for_telegram(error_type: str, **kwargs) -> str:
    """
    Generate user-friendly error message for Telegram.
    
    Args:
        error_type: Error type key from ERROR_MESSAGES
        **kwargs: Variables to format into message
    
    Returns:
        Formatted error message with MarkdownV2 escaping
    
    Example:
        >>> format_error_for_telegram("forbidden", user_id="123456")
        '⛔ Nie masz dostępu do JADZIA\\. Twój User ID: `123456`'
    """
    template = ERROR_MESSAGES.get(error_type, ERROR_MESSAGES["internal"])
    
    # Format with kwargs (escape values that aren't in code blocks)
    try:
        # Escape kwargs that will be inserted into non-code parts
        escaped_kwargs = {}
        for key, value in kwargs.items():
            # Don't escape values that go inside backticks (like operation_id, user_id)
            # The backticks already protect them
            escaped_kwargs[key] = str(value)
        
        message = template.format(**escaped_kwargs)
        return message
    
    except KeyError as e:
        # Missing required kwarg
        return f"💥 Błąd formatowania wiadomości: brakujący parametr {e}"


# ═══════════════════════════════════════════════════════════════
# RESPONSE FORMATTING
# ═══════════════════════════════════════════════════════════════

def format_response_for_telegram(
    text: str,
    awaiting_input: bool = False,
    diffs: Dict[str, str] = None
) -> List[Dict[str, Any]]:
    """
    Format complete response for Telegram.
    
    Args:
        text: Main response text
        awaiting_input: Whether system is awaiting user input
        diffs: Optional dict of filename -> diff content
    
    Returns:
        List of message dicts ready for n8n:
        [
            {"text": "...", "parse_mode": "MarkdownV2"},
            {"text": "...", "parse_mode": "MarkdownV2"},
        ]
    """
    messages = []
    
    # Main text message
    escaped_text = escape_markdown_v2(text)
    
    # Split if too long
    text_chunks = split_long_message(escaped_text)
    
    if len(text_chunks) > 1:
        text_chunks = add_part_indicators(text_chunks)
    
    for chunk in text_chunks:
        messages.append({
            "text": chunk,
            "parse_mode": "MarkdownV2"
        })
    
    # Add diffs if provided
    if diffs:
        for filename, diff in diffs.items():
            formatted_diff = format_diff_for_telegram(diff, filename)
            
            # Split diff if too long
            diff_chunks = split_long_message(formatted_diff)
            
            if len(diff_chunks) > 1:
                diff_chunks = add_part_indicators(diff_chunks)
            
            for chunk in diff_chunks:
                messages.append({
                    "text": chunk,
                    "parse_mode": "MarkdownV2"
                })
    
    # Add confirmation prompt if awaiting input
    if awaiting_input:
        prompt = "\n\nPotwierdzasz? (Norbi?)"
        
        # Append to last message if it's short enough
        if messages and len(messages[-1]["text"]) + len(prompt) < TELEGRAM_MAX_LENGTH:
            messages[-1]["text"] += prompt
        else:
            # Create new message
            messages.append({
                "text": prompt,
                "parse_mode": "MarkdownV2"
            })
    
    return messages


# ═══════════════════════════════════════════════════════════════
# HELP & INFO MESSAGES
# ═══════════════════════════════════════════════════════════════

def get_help_message() -> str:
    """Generate help message for Telegram users (Transfer Protocol V4)."""
    help_text = """
**JADZIA Bot \\- Pomoc**

🤖 **Dostępne komendy:**
• `/zadanie` \\- nowe zadanie \\(np\\. /zadanie zmień kolor przycisku\\)
• `/status` \\- sprawdź bieżącą operację
• `/cofnij` \\- cofnij ostatnie zmiany
• `/pomoc` \\- wyświetl tę pomoc

💬 **Jak używać:**
Użyj /zadanie i treść polecenia, np:
• "Dodaj komentarz w style\\.css"
• "Zmień kolor tła na niebieski"
• "Napraw błąd w functions\\.php"

✅ **Zatwierdzanie zmian:**
Po wygenerowaniu diffu użyj przycisków Tak/Nie lub napisz:
• `T` / `tak` / `yes` \\- zatwierdź
• `N` / `nie` / `no` \\- odrzuć
"""
    return help_text.strip()


def get_status_message(operation_id: str, status: str, awaiting_type: str = None) -> str:
    """
    Generate status message.
    
    Args:
        operation_id: Current operation ID
        status: Operation status
        awaiting_type: Type of input being awaited
    
    Returns:
        Formatted status message
    """
    status_emoji = {
        "planning": "🧠",
        "reading_files": "📖",
        "generating_code": "⚙️",
        "diff_ready": "📝",
        "approved": "✅",
        "writing_files": "💾",
        "completed": "🎉",
        "failed": "❌",
    }
    
    emoji = status_emoji.get(status, "❓")
    
    message = f"{emoji} **Status operacji**\n\n"
    message += f"ID: `{operation_id}`\n"
    message += f"Status: {escape_markdown_v2(status)}\n"
    
    if awaiting_type:
        message += f"\n⏳ Oczekuję na: {escape_markdown_v2(awaiting_type)}"
    
    return message
