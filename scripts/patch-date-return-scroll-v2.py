from pathlib import Path

# Remove the hash jump from body-check links so only the controlled scroll determines position.
p = Path('body-check.html')
s = p.read_text()
s2 = s.replace('&fromcheck=1#date', '&fromcheck=1')
if s2 == s:
    raise SystemExit('body-check link pattern not found')
p.write_text(s2)

# Make the booking page scroll after menu selection/layout settles, and reinforce once.
p = Path('index.html')
s = p.read_text()
old = """    setTimeout(()=>{\n      if(fromCheck){\n        const dateCard=$('date').closest('.card');\n        const target=dateCard||$('date');\n        const top=target.getBoundingClientRect().top+window.scrollY-12;\n        window.scrollTo({top,behavior:'smooth'});\n      }else{\n        button.scrollIntoView({behavior:'smooth',block:'center'});\n      }\n    },160);"""
new = """    if(fromCheck){\n      const scrollToDateCard=()=>{\n        const dateCard=$('date').closest('.card');\n        const target=dateCard||$('date');\n        const top=target.getBoundingClientRect().top+window.scrollY-18;\n        window.scrollTo({top,behavior:'smooth'});\n      };\n      setTimeout(scrollToDateCard,320);\n      setTimeout(scrollToDateCard,820);\n    }else{\n      setTimeout(()=>button.scrollIntoView({behavior:'smooth',block:'center'}),160);\n    }"""
if old not in s:
    raise SystemExit('index scroll block not found')
p.write_text(s.replace(old,new))
