# fix_dump.py
import os

# 1. Read the file using 'utf-8-sig' (This handles/removes the BOM automatically)
try:
    with open('datadump.json', 'r', encoding='utf-8-sig') as f:
        content = f.read()

    # 2. Write it back as pure 'utf-8' (No BOM)
    with open('datadump.json', 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ Success: BOM removed. File saved as Pure UTF-8.")

except FileNotFoundError:
    print("❌ Error: datadump.json not found in this folder.")
except Exception as e:
    print(f"❌ Error: {e}")