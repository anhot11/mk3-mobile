#!/usr/bin/env python3
import os
import sys
import zipfile

def extract_ipa(ipa_path):
    print(f"Extracting {ipa_path}...")
    with zipfile.ZipFile(ipa_path, 'r') as z:
        # 1. Extract binary
        for name in z.namelist():
            if name.endswith('/UMK3') and name.startswith('Payload/'):
                z.extract(name, '.')
                print(f"Extracted binary: {name}")
                break

        # 2. Extract res and Info.plist
        os.makedirs('res', exist_ok=True)
        prefix = 'Payload/UMK3.app/res/'
        count = 0
        for item in z.infolist():
            if item.filename.startswith(prefix) and not item.is_dir():
                rel = item.filename[len(prefix):]
                target = os.path.join('res', rel)
                os.makedirs(os.path.dirname(target), exist_ok=True)
                with z.open(item) as src, open(target, 'wb') as dst:
                    dst.write(src.read())
                count += 1
            elif item.filename == 'Payload/UMK3.app/Info.plist':
                with z.open(item) as src, open('Info.plist', 'wb') as dst:
                    dst.write(src.read())
        print(f"Extracted {count} resource files and Info.plist.")

if __name__ == '__main__':
    ipa = sys.argv[1] if len(sys.argv) > 1 else 'umk3.ipa'
    extract_ipa(ipa)
