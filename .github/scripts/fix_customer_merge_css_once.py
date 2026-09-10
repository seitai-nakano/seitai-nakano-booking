from pathlib import Path
p=Path('customers.html')
s=p.read_text(encoding='utf-8')
old='@media(max-width:480px){.mergeCompare{grid-template-columns:1fr}{.row,.topActions{grid-template-columns:1fr}'
new='@media(max-width:480px){.mergeCompare{grid-template-columns:1fr}.row,.topActions{grid-template-columns:1fr}'
if old not in s: raise SystemExit('CSS fix anchor not found')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
print('fixed')
