import re
with open(r'C:\Projekty\Jadzia\agent\agent.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '        log_error(str(e))\n        return await handle_error'
new = '        print(f"[MAIN ERROR] {type(e).__name__}: {e}")\n        log_error(str(e))\n        return await handle_error'
content = content.replace(old, new, 1)

with open(r'C:\Projekty\Jadzia\agent\agent.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
