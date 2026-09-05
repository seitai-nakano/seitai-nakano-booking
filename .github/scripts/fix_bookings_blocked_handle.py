from pathlib import Path

p=Path('bookings.html')
s=p.read_text(encoding='utf-8')

old='''.blockedBlock{\n  position:absolute;\n  top:9px;\n  height:91px;\n  border-radius:10px;\n  background:#f3deda;\n  border:1px solid #dca9a2;\n  padding:8px;\n  overflow:hidden;\n  font-size:11px;\n  color:#884e47;\n  z-index:3\n}\n'''
new='''.blockedBlock{\n  position:absolute;\n  top:9px;\n  height:91px;\n  border-radius:10px;\n  background:#f3deda;\n  border:1px solid #dca9a2;\n  padding:8px 42px 8px 8px;\n  overflow:hidden;\n  font-size:11px;\n  color:#884e47;\n  z-index:3;\n  touch-action:pan-x\n}\n\n.blockedMoveHandle{\n  position:absolute;\n  right:4px;\n  top:50%;\n  transform:translateY(-50%);\n  z-index:40;\n  width:34px;\n  height:44px;\n  border:1px solid rgba(120,70,64,.38);\n  border-radius:10px;\n  background:#fff;\n  display:flex;\n  align-items:center;\n  justify-content:center;\n  color:#884e47;\n  font-size:18px;\n  font-weight:900;\n  line-height:1;\n  touch-action:none!important;\n  -webkit-user-select:none;\n  user-select:none;\n  -webkit-touch-callout:none;\n  box-shadow:0 1px 5px rgba(0,0,0,.12)\n}\n'''
if old not in s:
    raise SystemExit('blocked css anchor not found')
s=s.replace(old,new,1)

# Change only the timeline background grid from 30-minute to 15-minute cells.
marker='function renderTimeline(){'
pos=s.find(marker)
if pos<0:
    raise SystemExit('renderTimeline marker not found')
head,tail=s[:pos],s[pos:]
old_loop='''  for(\n    let minute=DAY_START;\n    minute<=DAY_END;\n    minute+=30\n  ){'''
new_loop='''  for(\n    let minute=DAY_START;\n    minute<=DAY_END;\n    minute+=15\n  ){'''
if old_loop not in tail:
    raise SystemExit('timeline loop anchor not found')
tail=tail.replace(old_loop,new_loop,1)
old_width='''    cell.style.width=\n      `${\n        30\n        *\n        PX_PER_MINUTE\n      }px`;'''
new_width='''    cell.style.width=\n      `${\n        15\n        *\n        PX_PER_MINUTE\n      }px`;'''
if old_width not in tail:
    raise SystemExit('timeline width anchor not found')
tail=tail.replace(old_width,new_width,1)
s=head+tail

old_class="""      block.className=\n        'blockedBlock';\n\n\n      block.style.left="""
new_class="""      block.className=\n        'blockedBlock';\n\n      block.dataset.blockedId=\n        String(item.id);\n\n\n      block.style.left="""
if old_class not in s:
    raise SystemExit('blocked id anchor not found')
s=s.replace(old_class,new_class,1)

old_html='''        ${esc(\n          item.memo\n          ||\n          ''\n        )}\n\n      `;'''
new_html='''        ${esc(\n          item.memo\n          ||\n          ''\n        )}\n\n        <span\n          class="blockedMoveHandle"\n          role="button"\n          aria-label="予定時間を左右に移動"\n        >↔</span>\n\n      `;'''
if old_html not in s:
    raise SystemExit('blocked html anchor not found')
s=s.replace(old_html,new_html,1)

old_script='''<script type="module">import(`./booking-drag.js?_v=${Date.now()}`);</script>'''
new_script='''<script type="module">import(`./booking-drag.js?_v=${Date.now()}`);</script>\n<script type="module">import(`./blocked-drag.js?_v=${Date.now()}`);</script>'''
if old_script not in s:
    raise SystemExit('script import anchor not found')
s=s.replace(old_script,new_script,1)

p.write_text(s,encoding='utf-8')
print('patched bookings blocked handle and 15-minute grid')
