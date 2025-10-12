# Multi-Language Support

The Wedding Video Portal supports multiple languages (English and Romanian). Users can switch between languages using the language switcher in the navigation bar.

## Available Languages

- **English (EN)** - Default language
- **Română (RO)** - Romanian

## How to Use

### For Users

1. Look for the language switcher in the top navigation bar (flag icon with EN/RO indicator)
2. Click the language dropdown
3. Select your preferred language (English or Română)
4. The page will reload in the selected language

The language preference is saved in the session, so it persists across pages during your visit.

## For Developers

### Adding New Translations

1. **Mark strings for translation** in templates:
   ```django
   {% load i18n %}
   {% trans "Text to translate" %}
   ```

2. **Update the translation file**:
   Edit `locale/ro/LC_MESSAGES/django.po` and add new translations:
   ```po
   msgid "Your English text"
   msgstr "Textul tău în română"
   ```

3. **Compile translations**:
   ```bash
   # Install polib if not already installed
   pip install polib
   
   # Compile the translations
   python compile_translations_polib.py
   ```

### Translation File Structure

```
locale/
└── ro/
    └── LC_MESSAGES/
        ├── django.po  # Translation source file (edit this)
        └── django.mo  # Compiled translations (generated)
```

### Current Translation Coverage

The following areas have been translated:

- ✅ **Navigation Menu**: Dashboard, New Project, Login, Logout
- ✅ **Login Page**: All fields and labels
- ✅ **Base Template**: Language switcher
- ⏳ **Dashboard**: Partially translated (needs more work)
- ⏳ **Project Detail**: Not yet translated
- ⏳ **Forms**: Not yet translated

### Adding a New Language

1. **Create language directory**:
   ```bash
   mkdir -p locale/[lang_code]/LC_MESSAGES
   ```

2. **Copy the Romanian .po file as template**:
   ```bash
   copy locale\ro\LC_MESSAGES\django.po locale\[lang_code]\LC_MESSAGES\django.po
   ```

3. **Update settings.py**:
   ```python
   LANGUAGES = [
       ('en', 'English'),
       ('ro', 'Română'),
       ('[lang_code]', 'Language Name'),
   ]
   ```

4. **Translate strings** in the new .po file

5. **Compile translations**:
   ```bash
   pip install polib
   python compile_translations_polib.py
   ```

6. **Update base.html** language switcher to include new language flag

### Translation Best Practices

1. **Keep it concise**: Translations should be clear and concise
2. **Context matters**: Provide context for ambiguous strings
3. **Consistent terminology**: Use the same translation for the same term throughout
4. **Test thoroughly**: Check all translated pages for proper display
5. **Special characters**: Ensure Romanian diacritics (ă, â, î, ș, ț) display correctly

### Common Romanian Translations

| English | Romanian |
|---------|----------|
| Dashboard | Tablou de Bord |
| New Project | Proiect Nou |
| Login | Autentificare |
| Logout | Deconectare |
| Email | Email / Adresa de Email |
| Password | Parolă |
| Save | Salvează |
| Cancel | Anulează |
| Edit | Editează |
| Delete | Șterge |
| Search | Caută |
| Filter | Filtrează |
| Wedding | Nuntă |
| Baptism | Botez |
| Client | Client |
| Admin | Admin |
| Project | Proiect |
| Status | Status |
| Date | Dată |
| Time | Oră |
| Files | Fișiere |
| Upload | Încarcă |
| Download | Descarcă |

### Technical Details

**Django i18n Configuration:**
- `LANGUAGE_CODE = 'en'` - Default language
- `USE_I18N = True` - Enable internationalization
- `LocaleMiddleware` - Handles language switching
- `i18n_patterns` - URL routing with language prefix support

**Translation Files:**
- `.po` files are human-readable translation sources
- `.mo` files are compiled binary files used by Django
- `compile_translations_polib.py` - Uses polib library for reliable compilation
- `polib` - Python library for handling .po/.mo files (install with `pip install polib`)

### Troubleshooting

**Translations not showing:**
1. Check if .mo file exists and is up-to-date
2. Run `pip install polib` then `python compile_translations_polib.py`
3. Restart Django development server
4. Clear browser cache

**Language switcher not working:**
1. Verify `LocaleMiddleware` is in `MIDDLEWARE` settings
2. Check if `i18n` URLs are included in `urls.py`
3. Ensure `{% load i18n %}` is at the top of templates

**Missing translations:**
1. Add the missing string to `django.po`
2. Recompile with `python compile_translations_polib.py`
3. Restart the server
4. Refresh the page

## Future Enhancements

- [ ] Translate dashboard completely
- [ ] Translate project detail page
- [ ] Translate all forms
- [ ] Add JavaScript string translations
- [ ] Translate email templates
- [ ] Add more languages (French, German, Spanish)
- [ ] Add language detection based on browser settings
- [ ] Make language preference persistent in user profile

## Notes

- The language preference is session-based, not user-profile based
- URLs can optionally include language prefix (e.g., `/ro/dashboard/`)
- `prefix_default_language=False` means English URLs don't have `/en/` prefix
- Romanian uses specific diacritics that must be properly encoded (UTF-8)
