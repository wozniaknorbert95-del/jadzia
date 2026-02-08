## MarkdownV2 Escaping Fix

### Verification (telegram_formatter.py)

- **ESCAPE_CHARS** (line 23): `ESCAPE_CHARS = r'_*[]()~`>#+-=|{}.!'` — `(` and `)` are included (inside the `[]()` group).
- **escape_markdown_v2()** (lines 26–68): Defined in [agent/telegram_formatter.py](agent/telegram_formatter.py); escapes all characters in ESCAPE_CHARS (including parentheses) for Telegram MarkdownV2.

### Why "(Norbi?)" was not escaped

- In **format_response_for_telegram()** (lines 327–334) the confirmation prompt was hardcoded and appended without escaping:
  ```python
  prompt = "\n\nPotwierdzasz? (Norbi?)"
  # ...
  messages[-1]["text"] += prompt   # or messages.append({"text": prompt, ...})
  ```
- The main response body is escaped at line 298 (`escaped_text = escape_markdown_v2(text)`), but the **prompt** string was added raw. With `parse_mode: "MarkdownV2"`, `(` and `)` must be sent as `\\(` and `\\)`, so the unescaped prompt caused Telegram parse errors or broken display.

### Root cause

**format_response_for_telegram()** in [agent/telegram_formatter.py](agent/telegram_formatter.py) (around line 331) built the confirmation text `"Potwierdzasz? (Norbi?)"` and appended it to the message list without passing it through **escape_markdown_v2()**. Only the main `text` argument was escaped; the hardcoded prompt was not.

### Fix

**File:** [agent/telegram_formatter.py](agent/telegram_formatter.py)  
**Change (line 331):** Build the prompt from an escaped string so all MarkdownV2 special characters (including parentheses) are escaped before sendMessage:

```python
# Before:
prompt = "\n\nPotwierdzasz? (Norbi?)"

# After:
prompt = "\n\n" + escape_markdown_v2("Potwierdzasz? (Norbi?)")
```

All messages sent with `parse_mode: "MarkdownV2"` from this function (including the appended prompt) now contain only properly escaped text.

### Verification

- **Before:** Telegram received `Potwierdzasz? (Norbi?)` → parentheses break MarkdownV2.
- **After:** Telegram receives `Potwierdzasz? \\(Norbi?\\)` → valid MarkdownV2, displays as: Potwierdzasz? (Norbi?).

No other call sites needed changes: the main response body was already escaped (line 298); only the hardcoded confirmation prompt was missing escaping and is now fixed.
