from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

head_tags='''\n<link rel="manifest" href="./manifest.webmanifest">\n<meta name="theme-color" content="#741b16">\n<meta name="apple-mobile-web-app-capable" content="yes">\n<meta name="apple-mobile-web-app-status-bar-style" content="default">\n<meta name="apple-mobile-web-app-title" content="整体なかの">\n<link rel="apple-touch-icon" href="./assets/app-icon-192.png">\n'''
if 'rel="manifest"' not in s:
    marker='<title>整体なかの｜オンライン予約</title>'
    if marker not in s:
        raise SystemExit('title marker not found')
    s=s.replace(marker, marker+head_tags, 1)

script='<script src="./pwa-register.js?v=20260908-2" defer></script>'
if 'pwa-register.js' not in s:
    if '</body>' not in s:
        raise SystemExit('body close not found')
    s=s.replace('</body>', script+'\n</body>', 1)
else:
    import re
    s=re.sub(r'<script[^>]+src=["\']\./pwa-register\.js[^"\']*["\'][^>]*></script>', script, s, count=1)

p.write_text(s,encoding='utf-8')
print('patched index.html')
