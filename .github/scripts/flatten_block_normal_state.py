from pathlib import Path
p=Path('blocked-drag.js')
s=p.read_text()
old="""${blockedSelector}{
  -webkit-touch-callout:none!important;
  -webkit-user-select:none!important;
  user-select:none!important;
  touch-action:none!important;
  cursor:grab!important;
}
${blockedSelector}.blockedDragging{
  z-index:160!important;
  opacity:.98!important;
  transform:translateY(6px) scale(1.035)!important;
  box-shadow:0 0 0 4px rgba(138,74,66,.24),0 12px 30px rgba(0,0,0,.24)!important;
  transition:none!important;
  will-change:left,transform!important;
  cursor:grabbing!important;
}
"""
new="""${blockedSelector}{
  -webkit-touch-callout:none!important;
  -webkit-user-select:none!important;
  user-select:none!important;
  touch-action:none!important;
  cursor:grab!important;
  transform:none!important;
  box-shadow:none!important;
  opacity:1!important;
  filter:none!important;
  transition:transform .10s ease,box-shadow .10s ease,opacity .10s ease!important;
}
${blockedSelector}.blockedDragging{
  z-index:160!important;
  opacity:.98!important;
  transform:translateY(-4px) scale(1.025)!important;
  box-shadow:0 3px 0 rgba(138,74,66,.18),0 12px 28px rgba(0,0,0,.24)!important;
  transition:none!important;
  will-change:left,transform!important;
  cursor:grabbing!important;
}
"""
if old not in s:
    raise SystemExit('target CSS not found')
p.write_text(s.replace(old,new,1))
