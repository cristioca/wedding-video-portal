#!/usr/bin/env python
"""
Compile .po files to .mo files using polib library.
This is a more reliable alternative to manual compilation.
"""

import polib
from pathlib import Path

def compile_po_to_mo():
    """Compile all .po files to .mo files using polib."""
    base_dir = Path(__file__).parent
    locale_dir = base_dir / 'locale'
    
    if not locale_dir.exists():
        print(f"Locale directory not found: {locale_dir}")
        return
    
    for po_file in locale_dir.rglob('*.po'):
        print(f"Compiling {po_file}...")
        try:
            # Load the .po file
            po = polib.pofile(str(po_file))
            
            # Save as .mo file
            mo_file = po_file.with_suffix('.mo')
            po.save_as_mofile(str(mo_file))
            
            print(f"✓ Created {mo_file}")
            print(f"  Entries: {len(po)}")
            print(f"  Translated: {len(po.translated_entries())}")
            
        except Exception as e:
            print(f"✗ Error compiling {po_file}: {e}")

if __name__ == '__main__':
    compile_po_to_mo()
