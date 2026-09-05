from pathlib import Path
p=Path('index.html')
s=p.read_text()
old="""    head:{
      short:['head','m60h','m90h'],
      standard:['m60h','m90h','head'],
      deep:['m90h','m120h','m60h']
    },
    part:{
      short:['m30','m60','m90'],
      standard:['m60','m90','m30'],
      deep:['m90','m120','m60']
    },
    whole:{
      short:['m60','m90','m120'],
      standard:['m90','m120','m60'],
      deep:['m120','m90','m60']
    },
    unsure:{
      short:['m60','m90','m30'],
      standard:['m90','m60','m120'],
      deep:['m120','m90','m60']
    }
"""
new="""    head:{
      short:['head','m60h','m90h'],
      standard:['m60h','m90h','m120h'],
      deep:['m90h','m120h','m60h']
    },
    part:{
      short:['m30','m60','m90'],
      standard:['m60h','m90h','m120h'],
      deep:['m90','m120','m60']
    },
    whole:{
      short:['m60','m90','m120'],
      standard:['m90h','m120h','m60h'],
      deep:['m120','m90','m60']
    },
    unsure:{
      short:['m60','m90','m30'],
      standard:['m90h','m60h','m120h'],
      deep:['m120','m90','m60']
    }
"""
if old not in s:
    raise SystemExit('target recommendation table not found')
s=s.replace(old,new,1)
p.write_text(s)
