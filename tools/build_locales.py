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
css = '''\n.language-picker{position:relative;font-size:14px}.language-picker summary{display:flex;align-items:center;gap:8px;min-height:42px;padding:8px 10px;border:1px solid var(--line);border-radius:5px;list-style:none;cursor:pointer;background:var(--paper)}.language-picker summary::-webkit-details-marker{display:none}.language-flag{display:block;flex-shrink:0;border-radius:2px;box-shadow:0 0 0 1px #243b2d26}.language-chevron{font-size:18px;line-height:1}.language-picker[open] .language-chevron{transform:rotate(180deg)}.language-options{position:absolute;right:0;top:calc(100% + 8px);min-width:185px;max-width:calc(100vw - 44px);margin:0;padding:6px;list-style:none;background:#fffdf7;border:1px solid var(--line);border-radius:8px;box-shadow:0 12px 30px #243b2d24;z-index:10}.language-options a{display:flex;align-items:center;gap:12px;padding:10px 12px;min-height:44px;text-decoration:none;border-radius:4px}.language-options a:hover,.language-options a:focus-visible{background:#e9ecdf}.language-options a[aria-current="page"]{font-weight:750;background:#e9ecdf}.navlinks{gap:16px;justify-content:flex-end}.navlinks .button{text-align:center}h1,h2,h3,p,a,summary{overflow-wrap:anywhere}body:lang(ja){line-break:strict}body:lang(ja) h1,body:lang(ja) h2,body:lang(ja) h3{letter-spacing:0;line-height:1.35}.notebook p{background:none}.feature h3{font-size:clamp(24px,2.4vw,29px)}@media(max-width:760px){nav{gap:12px}.brand{min-width:0}.brand-logo{width:40px;height:40px}.navlinks{flex-shrink:0}.navlinks{gap:8px}.language-picker .selected-language{display:none}.language-picker summary{padding:8px}.language-options a{font-size:14px}.notebook p{font-size:18px}.hero h1{font-size:clamp(37px,10vw,56px)}}\n'''

def flag(code):
    shapes = {
        'en':'<path fill="#012169" d="M0 0h60v40H0z"/><path stroke="#fff" stroke-width="9" d="m0 0 60 40m0-40L0 40"/><path stroke="#c8102e" stroke-width="3" d="m0 0 60 40m0-40L0 40"/><path stroke="#fff" stroke-width="14" d="M30 0v40M0 20h60"/><path stroke="#c8102e" stroke-width="8" d="M30 0v40M0 20h60"/>',
        'fr':'<path fill="#fff" d="M0 0h60v40H0z"/><path fill="#002395" d="M0 0h20v40H0z"/><path fill="#ed2939" d="M40 0h20v40H40z"/>',
        'es':'<path fill="#aa151b" d="M0 0h60v40H0z"/><path fill="#f1bf00" d="M0 10h60v20H0z"/>',
        'de':'<path d="M0 0h60v14H0z"/><path fill="#d00" d="M0 13.33h60v13.34H0z"/><path fill="#ffce00" d="M0 26.67h60V40H0z"/>',
        'ja':'<path fill="#fff" d="M0 0h60v40H0z"/><circle cx="30" cy="20" r="12" fill="#bc002d"/>',
        'el':'<path fill="#0d5eaf" d="M0 0h60v40H0z"/><path stroke="#fff" stroke-width="4.444" d="M0 6.667h60M0 15.556h60M0 24.444h60M0 33.333h60"/><path fill="#0d5eaf" d="M0 0h22.222v22.222H0z"/><path stroke="#fff" stroke-width="4.444" d="M11.111 0v22.222M0 11.111h22.222"/>',
        'gd':'<path fill="#0065bd" d="M0 0h60v40H0z"/><path stroke="#fff" stroke-width="8" d="m0 0 60 40m0-40L0 40"/>',
    }
    return '<svg class="language-flag" viewBox="0 0 60 40" width="24" height="16" aria-hidden="true" focusable="false">'+shapes[code]+'</svg>'

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
    head=head.replace('</style>',css+'.journal-screenshot{margin:24px 0 0;transform:rotate(2deg)}.journal-screenshot img{width:100%;height:auto;display:block;border-radius:5px}.journal-screenshot figcaption{font:12px/1.4 system-ui,sans-serif;color:var(--muted);margin-top:8px}.about-grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:65px;align-items:center}.about-grid img{display:block;width:100%;height:auto;max-height:620px;object-fit:cover;object-position:center;border-radius:8px}.about-grid p{color:var(--muted)}@media(max-width:760px){.about-grid{grid-template-columns:1fr;gap:30px}.about-grid img{max-height:520px}}'+'</style>')
    alternates=''.join(f'<link rel="alternate" hreflang="{code}" href="{url(code)}">' for code in labels)
    head=head.replace('</head>',alternates+f'<link rel="alternate" hreflang="x-default" href="{url("en")}"></head>')
    # Localized, crawlable structured data rather than English-only copy.
    structured={'@context':'https://schema.org','@type':'WebSite','name':'Garden Journal: Planner','url':url(lang),'description':meta[1],'inLanguage':lang}
    head=re.sub(r'<script type="application/ld\+json">.*?</script>','<script type="application/ld+json">'+json.dumps(structured,ensure_ascii=False)+'</script>',head)
    organization={'@context':'https://schema.org','@type':'Organization','name':'Garden Shed Clay','url':'https://gardenshedclay.com/'}
    head=head.replace('</head>','<script type="application/ld+json">'+json.dumps(organization,ensure_ascii=False)+'</script></head>')
    body=body.replace('aria-label="Main navigation"','aria-label="'+html.escape(meta[3],quote=True)+'"')
    body=re.sub(r'alt="Garden Journal dashboard[^"]*"','alt="'+html.escape(meta[4],quote=True)+'"',body)
    menu = '<details class="language-picker"><summary aria-label="'+html.escape(meta[2]+': '+labels[lang],quote=True)+'">'+flag(lang)+'<span class="selected-language">'+labels[lang]+'</span><span class="language-chevron" aria-hidden="true">⌄</span></summary><ul class="language-options">'+''.join('<li><a href="'+url(code)+'" lang="'+code+'" hreflang="'+code+'"'+(' aria-current="page"' if code==lang else '')+'>'+flag(code)+'<span>'+label+'</span></a></li>' for code,label in labels.items())+'</ul></details>'
    body=body.replace('</div></nav></header>',menu+'</div></nav></header>')
    about = {
        'en':['About the gardener','Hello, I’m Lester.','I’m a self-taught gardener. Every season brings something new to learn. I created Garden Journal: Planner to bring garden plans, plant records, and the little discoveries we make along the way into one place.','Whether you’re growing vegetables, flowers, herbs, or a little of everything, I hope it helps you enjoy your garden and carry what you learn into the next season.','Lester in his garden with his dogs'],
        'fr':['À propos du jardinier','Bonjour, je suis Lester.','Je suis un jardinier autodidacte. Chaque saison apporte son lot de découvertes. J’ai créé Garden Journal: Planner pour réunir les plans, les fiches de plantes et les petites découvertes du jardin au même endroit.','Que vous cultiviez des légumes, des fleurs, des herbes ou un peu de tout, j’espère que cet outil vous aidera à profiter de votre jardin et à préparer la saison suivante.','Lester dans son jardin avec ses chiens'],
        'es':['Sobre el jardinero','Hola, soy Lester.','Soy un jardinero autodidacta. Cada temporada trae algo nuevo que aprender. Creé Garden Journal: Planner para reunir en un solo lugar los planes, los registros de plantas y los pequeños descubrimientos del jardín.','Ya cultives verduras, flores, hierbas o un poco de todo, espero que te ayude a disfrutar de tu jardín y a aprovechar lo aprendido en la próxima temporada.','Lester en su jardín con sus perros'],
        'de':['Über den Gärtner','Hallo, ich bin Lester.','Ich bin ein autodidaktischer Gärtner. Jede Saison bringt etwas Neues, das man lernen kann. Ich habe Garden Journal: Planner geschaffen, um Gartenpläne, Pflanzenaufzeichnungen und kleine Entdeckungen an einem Ort zu sammeln.','Ob du Gemüse, Blumen, Kräuter oder von allem etwas anbaust: Ich hoffe, die App hilft dir, deinen Garten zu genießen und deine Erfahrungen in die nächste Saison mitzunehmen.','Lester mit seinen Hunden im Garten'],
        'ja':['庭師について','こんにちは、レスターです。','私は独学のガーデナーです。季節ごとに新しい学びがあります。庭の計画、植物の記録、日々の小さな発見を一か所にまとめるため、Garden Journal: Plannerを作りました。','野菜、花、ハーブなど、何を育てていても、庭を楽しみ、学んだことを次の季節に生かすお手伝いができれば幸いです。','犬たちと庭にいるレスター'],
        'el':['Σχετικά με τον κηπουρό','Γεια σας, είμαι ο Lester.','Είμαι αυτοδίδακτος κηπουρός. Κάθε εποχή φέρνει κάτι νέο για να μάθουμε. Δημιούργησα το Garden Journal: Planner για να συγκεντρώνει τα σχέδια, τα αρχεία φυτών και τις μικρές ανακαλύψεις του κήπου σε ένα μέρος.','Είτε καλλιεργείτε λαχανικά, λουλούδια, βότανα ή λίγο απ’ όλα, ελπίζω να σας βοηθήσει να χαρείτε τον κήπο σας και να αξιοποιήσετε όσα μάθατε την επόμενη εποχή.','Ο Lester στον κήπο με τους σκύλους του'],
        'gd':['Mun ghàirnealair','Halò, is mise Lester.','Tha mi nam ghàirnealair fèin-ionnsaichte. Bheir gach ràith rudeigin ùr ri ionnsachadh. Chruthaich mi Garden Journal: Planner gus planaichean gàrraidh, clàran lusan agus na rudan beaga a lorgas sinn a chumail còmhla.','Ge bith an fhàs thu glasraich, flùraichean, luibhean no beagan de gach nì, tha mi an dòchas gun cuidich e thu gus do ghàrradh a mhealtainn agus na dh’ionnsaich thu a chleachdadh san ath ràith.','Lester sa ghàrradh còmhla ris na coin aige']
    }[lang]
    a,h,p1,p2,alt = (html.escape(x) for x in about)
    section = f'<section class="wrap section about-gardener" id="about"><div class="about-grid"><img src="/gardener-lester.jpg" width="1050" height="1400" loading="lazy" alt="{alt}"><div><div class="eyebrow">{a}</div><h2>{h}</h2><p>{p1}</p><p>{p2}</p></div></div></section>'
    body=body.replace('<section class="wrap section faq" id="questions">', section+'<section class="wrap section faq" id="questions">')
    journal_label={'en':'A journal entry in the app, with notes, weather and photos.','fr':'Une entrée du journal dans l’application, avec notes, météo et photos.','es':'Una entrada del diario en la aplicación, con notas, tiempo y fotos.','de':'Ein Tagebucheintrag in der App mit Notizen, Wetter und Fotos.','ja':'メモ、天気、写真を含むアプリ内の庭日記。','el':'Μια καταχώριση ημερολογίου στην εφαρμογή, με σημειώσεις, καιρό και φωτογραφίες.','gd':'Nòt san aplacaid le notaichean, sìde agus dealbhan.'}[lang]
    journal_image='<figure class="journal-screenshot"><img src="/journal-screenshot.webp" width="1400" height="760" loading="lazy" alt="'+html.escape(journal_label,quote=True)+'"><figcaption>'+html.escape(journal_label)+'</figcaption></figure>'
    body=body.replace('<section class="journal section">','<section class="journal section">',1)
    start=body.index('<section class="journal section">'); end=body.index('</section>',start)
    segment=body[start:end]; marker='</div><div><div class="eyebrow">'; assert marker in segment
    segment=segment.replace(marker,journal_image+marker,1);body=body[:start]+segment+body[end:]
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
