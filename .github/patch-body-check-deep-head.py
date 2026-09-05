from pathlib import Path
import re
p=Path('index.html')
s=p.read_text()
# When the user chooses "じっくり", always recommend head-included courses,
# with 120分+ヘッド first, regardless of the concern selected.
pattern=r"(\bdeep:\s*)\[[^\]]*\]"
parts=s.split("function bodyCheckRecommendations(){",1)
if len(parts)!=2:
    raise SystemExit('bodyCheckRecommendations not found')
head,rest=parts
func,tail=rest.split("function chooseBodyCheckMenu",1)
new_func,count=re.subn(pattern,r"\1['m120h','m90h','m60h']",func)
if count < 4:
    raise SystemExit(f'expected at least 4 deep mappings, got {count}')
p.write_text(head+"function bodyCheckRecommendations(){"+new_func+"function chooseBodyCheckMenu"+tail)
print('updated deep recommendation rows:',count)
