"""
Compile .po translation files to .mo files without requiring gettext tools.
This script manually compiles translation files using Python's struct module.
"""

import os
import struct
import array
from pathlib import Path

def parse_po_file(po_path):
    """Parse a .po file and return a dictionary of translations."""
    translations = {}
    current_msgid = None
    current_msgstr = None
    in_msgid = False
    in_msgstr = False
    
    with open(po_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            if line.startswith('#') or not line:
                continue
                
            if line.startswith('msgid "'):
                if current_msgid is not None and current_msgstr is not None:
                    translations[current_msgid] = current_msgstr
                current_msgid = line[7:-1]
                in_msgid = True
                in_msgstr = False
            elif line.startswith('msgstr "'):
                current_msgstr = line[8:-1]
                in_msgid = False
                in_msgstr = True
            elif line.startswith('"') and line.endswith('"'):
                text = line[1:-1]
                if in_msgid:
                    current_msgid += text
                elif in_msgstr:
                    current_msgstr += text
        
        # Add last translation
        if current_msgid is not None and current_msgstr is not None:
            translations[current_msgid] = current_msgstr
    
    return translations

def generate_mo_file(translations, mo_path):
    """
    Generate a .mo file from translations dictionary.
    Follows the GNU gettext MO file format specification.
    """
    # Remove empty msgid (metadata entry) as it causes issues
    if '' in translations:
        del translations['']
    
    # Encode keys and values
    keys = []
    values = []
    for k, v in sorted(translations.items()):
        if k:  # Skip empty keys
            keys.append(k.encode('utf-8'))
            values.append(v.encode('utf-8'))
    
    # Calculate offsets
    keyoffsets = []
    valueoffsets = []
    
    # Magic number and header size
    MAGIC = 0x950412de
    LE_MAGIC = 0xde120495  # Little endian magic
    
    # Use little-endian
    offsets = array.array("i")
    ids = array.array("i")
    strs = array.array("i")
    
    # Header: 7 integers
    # 0: magic, 1: version, 2: nstrings, 3: orig offset, 4: trans offset, 5: hash size, 6: hash offset
    header_size = 7 * 4
    
    # Each string table entry: 2 integers (length, offset)
    keys_index_size = len(keys) * 2 * 4
    values_index_size = len(values) * 2 * 4
    
    # Calculate where string data starts
    keys_start = header_size + keys_index_size + values_index_size
    
    # Build key offsets
    current_offset = keys_start
    for k in keys:
        keyoffsets.append((len(k), current_offset))
        current_offset += len(k)
    
    # Build value offsets
    values_start = current_offset
    current_offset = values_start
    for v in values:
        valueoffsets.append((len(v), current_offset))
        current_offset += len(v)
    
    # Build the file
    output = bytearray()
    
    # Write header
    output += struct.pack('I', MAGIC)           # Magic number
    output += struct.pack('I', 0)               # File format version
    output += struct.pack('I', len(keys))       # Number of strings
    output += struct.pack('I', header_size)     # Offset of key index
    output += struct.pack('I', header_size + keys_index_size)  # Offset of value index
    output += struct.pack('I', 0)               # Size of hash table (unused)
    output += struct.pack('I', 0)               # Offset of hash table (unused)
    
    # Write key index (length, offset pairs)
    for length, offset in keyoffsets:
        output += struct.pack('I', length)
        output += struct.pack('I', offset)
    
    # Write value index (length, offset pairs)
    for length, offset in valueoffsets:
        output += struct.pack('I', length)
        output += struct.pack('I', offset)
    
    # Write keys
    for k in keys:
        output += k
    
    # Write values
    for v in values:
        output += v
    
    # Write the .mo file
    with open(mo_path, 'wb') as f:
        f.write(output)

def main():
    """Compile all .po files to .mo files."""
    base_dir = Path(__file__).parent
    locale_dir = base_dir / 'locale'
    
    if not locale_dir.exists():
        print(f"Locale directory not found: {locale_dir}")
        return
    
    for po_file in locale_dir.rglob('*.po'):
        print(f"Compiling {po_file}...")
        try:
            translations = parse_po_file(po_file)
            mo_file = po_file.with_suffix('.mo')
            generate_mo_file(translations, mo_file)
            print(f"✓ Created {mo_file}")
        except Exception as e:
            print(f"✗ Error compiling {po_file}: {e}")

if __name__ == '__main__':
    main()
