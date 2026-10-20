"""Generate the static language pages from the approved English copy.
Run: python3 tools/build_locales.py (no third-party dependencies).
"""
import html, json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parent
if ROOT.name == 'tools':
    ROOT = ROOT.parent
    source_path = ROOT / 'translations/source.html'
    locales_path = ROOT / 'translations/locales.json'
else:
    source_path = ROOT / 'source.html'
    locales_path = ROOT / 'locales.json'
source = source_path.read_text()
locales = json.loads(locales_path.read_text())
labels = {'en':'English', 'fr':'Français', 'es':'Español', 'de':'Deutsch', 'ja':'日本語', 'el':'Ελληνικά', 'gd':'Gàidhlig'}
english_faq = [
 'Can I choose metric or imperial measurements?',
 'Yes. In the app’s settings, choose metric (meters and centimeters) or imperial (feet and inches) for supported garden measurements.',
 'Can I set my hardiness zone and hemisphere?',
 'Yes. Settings include USDA, Canadian, UK (RHS), European, Japanese, Australian, and New Zealand zone systems. Choose your zone and the Northern or Southern Hemisphere to adjust seasonal guidance. You can also save your average first and last frost dates.',
 'Which languages are available?',
 'The website and app offer English, French, Spanish, German, Japanese, Greek, and Scottish Gaelic. Choose the website language above; set the app language separately in its settings. Screenshots and external pages may remain in their original language.'
]
english_meta = ['Plan, Grow & Remember','Plan your garden beds, keep plant records, capture photos and journal entries, and organize recurring care with Garden Journal: Planner.','Languages','Main navigation','Garden Journal dashboard showing daily plant care, USDA Zone 7b, a garden check-in, and seasonal gardening tips.']
base = 'https://gardenjournalplanner.com'
def url(lang):return base + ('/' if lang == 'en' else f'/{lang}/')
css = '''\n.language-bar{display:flex;align-items:center;justify-content:flex-end;gap:8px 16px;flex-wrap:wrap;padding-top:10px;padding-bottom:10px;font-size:13px}.language-bar a{white-space:nowrap;text-decoration:none;padding:3px 2px}.language-bar a[aria-current="page"]{font-weight:750;text-decoration:underline;text-underline-offset:5px}.language-label{font-weight:650;margin-right:4px}.navlinks{flex-wrap:wrap;justify-content:flex-end}.navlinks .button{text-align:center}h1,h2,h3,p,a,summary{overflow-wrap:anywhere}body:lang(ja){line-break:strict}body:lang(ja) h1,body:lang(ja) h2,body:lang(ja) h3{letter-spacing:0;line-height:1.35}.notebook p{background:none}.feature h3{font-size:clamp(24px,2.4vw,29px)}@media(max-width:760px){nav{gap:12px}.brand{min-width:0}.brand-logo{width:40px;height:40px}.navlinks{flex-shrink:0}.language-bar{justify-content:flex-start;gap:6px 13px}.language-label{flex-basis:100%}.notebook p{font-size:18px}.hero h1{font-size:clamp(37px,10vw,56px)}}\n'''
outputs=[]
for lang in labels:
    tr = locales.get(lang,{})
    head,body = source.split('<body>',1)
    if lang != 'en':
        count=[-1]
        def translate(match):
            count[0]+=1
            text=match.group(1)
            if str(count[0]) in tr:text=html.escape(tr[str(count[0])],quote=False)
            elif text.strip() and count[0] not in [1,10,11,80]:
                raise ValueError(f'Missing translation {lang}:{count[0]} {text}')
            return '>'+text+'<'
        body=re.sub(r'>([^<>]+)<',translate,'>'+body)[1:]
    meta=tr.get('meta',english_meta)
    head=head.replace('<html lang="en">',f'<html lang="{lang}">')
    head=re.sub(r'<title>.*?</title>',f'<title>Garden Journal: Planner | {html.escape(meta[0])}</title>',head)
    head=re.sub(r'<meta name="description" content="[^"]*">',f'<meta name="description" content="{html.escape(meta[1],quote=True)}">',head)
    head=re.sub(r'<link rel="canonical" href="[^"]*">',f'<link rel="canonical" href="{url(lang)}">',head)
    for prop,value in [('og:title','Garden Journal: Planner — '+meta[0]),('og:description',meta[1]),('og:url',url(lang))]:
        head=re.sub(r'<meta property="'+prop+r'" content="[^"]*">',f'<meta property="{prop}" content="{html.escape(value,quote=True)}">',head)
    head=head.replace('</style>',css+'</style>')
    alternates=''.join(f'<link rel="alternate" hreflang="{code}" href="{url(code)}">' for code in labels)
    head=head.replace('</head>',alternates+f'<link rel="alternate" hreflang="x-default" href="{url("en")}"></head>')
    # Localized, crawlable structured data rather than English-only copy.
    structured={'@context':'https://schema.org','@type':'WebSite','name':'Garden Journal: Planner','url':url(lang),'description':meta[1],'inLanguage':lang}
    head=re.sub(r'<script type="application/ld\+json">.*?</script>','<script type="application/ld+json">'+json.dumps(structured,ensure_ascii=False)+'</script>',head)
    body=body.replace('aria-label="Main navigation"','aria-label="'+html.escape(meta[3],quote=True)+'"')
    body=re.sub(r'alt="Garden Journal dashboard[^"]*"','alt="'+html.escape(meta[4],quote=True)+'"',body)
    body=body.replace('</nav></header>','</nav><div class="wrap language-bar" role="navigation" aria-label="'+html.escape(meta[2],quote=True)+'"><span class="language-label">'+meta[2]+'</span>'+''.join(f'<a href="{url(code)}" lang="{code}" hreflang="{code}"'+(' aria-current="page"' if code==lang else '')+'>'+label+'</a>' for code,label in labels.items())+'</div></header>')
    faq=tr.get('faq',english_faq)
    details=''.join('<details><summary>'+html.escape(faq[i])+'</summary><p>'+html.escape(faq[i+1])+'</p></details>' for i in range(0,len(faq),2))
    marker='</details></section>\n<section class="cta">'
    assert marker in body
    body=body.replace(marker,'</details>'+details+'</section>\n<section class="cta">')
    # Root-relative assets work on every language path.
    result=head+'<body>'+body
    for asset in ['garden-journal-logo.png','garden-dashboard.png']:
        result=result.replace('src="'+asset+'"','src="/'+asset+'"').replace('href="'+asset+'"','href="/'+asset+'"')
    target=ROOT/('index.html' if lang=='en' else f'{lang}/index.html')
    target.parent.mkdir(parents=True,exist_ok=True);target.write_text(result)
    outputs.append(str(target.relative_to(ROOT)))
# Include every localized canonical URL, with reciprocal language annotations.
xml=['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
for lang in labels:
    xml.append('<url><loc>'+url(lang)+'</loc>')
    xml.extend(f'<xhtml:link rel="alternate" hreflang="{code}" href="{url(code)}" />' for code in labels)
    xml.append(f'<xhtml:link rel="alternate" hreflang="x-default" href="{url("en")}" /></url>')
xml.append('</urlset>');(ROOT/'sitemap.xml').write_text('\n'.join(xml)+'\n')
print('Generated '+', '.join(outputs)+', sitemap.xml')
