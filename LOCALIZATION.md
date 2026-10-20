# Website languages

The website mirrors the app's Settings language choices: en, fr, es, de, ja, el, gd.
English is at `/`; other languages have static `/{language}/` pages. Each page contains
its complete translated text without JavaScript and offers reciprocal language links,
a localized canonical URL, hreflang annotations, metadata, and structured data.
The sitemap lists all seven pages. Screenshot text is preserved from the original app capture.
Website language selection does not change the signed-in app's language preference.

## Editing copy

- English template: `translations/source.html`.
- Translations, FAQ answers and localized metadata: `translations/locales.json`.
- Generator: `tools/build_locales.py` (Python standard library only).
- Run `python3 tools/build_locales.py` from the repository root and commit generated pages and sitemap.

Translated text keys refer to the template's text-node positions. The generator fails on
missing translated nodes; update all language mappings when changing template structure.
The three regional/language FAQs are stored separately in the generator (English) and
translation data (other languages). Match claims to the live app's settings.

Translations are initial translations; native-speaker editorial review has not been completed.
The no-card trial FAQ is intentionally absent until the app behavior is released and verified.
