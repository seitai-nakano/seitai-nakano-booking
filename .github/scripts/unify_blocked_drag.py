from pathlib import Path

admin = Path('admin.html')
s = admin.read_text(encoding='utf-8')

# Let the shared blocked-drag module own the move handle on admin.html too.
s = s.replace('''          class="blockedMoveHandle"\n          data-bound-move="1"\n          role="button"''', '''          class="blockedMoveHandle"\n          role="button"''')

old_call = '''      bindDirectBlockedMove(\n        block,\n        item,\n        start,\n        end\n      );\n\n'''
if old_call in s:
    s = s.replace(old_call, '', 1)

# Ensure the shared pointer-tracking module is loaded on admin.html.
needle = '''<script type="module">import(`./booking-drag.js?_v=${Date.now()}`);</script>'''
insert = '''<script type="module">import(`./booking-drag.js?_v=${Date.now()}`);</script>\n<script type="module">import(`./blocked-drag.js?_v=${Date.now()}`);</script>'''
if needle in s and 'blocked-drag.js?_v=' not in s:
    s = s.replace(needle, insert, 1)

s = s.replace('↔で移動（画面端で自動スクロール）', '↔で移動（指を追跡して横スクロール）')
admin.write_text(s, encoding='utf-8')

# Strengthen shared drag behavior for iPhone/Safari.
p = Path('blocked-drag.js')
j = p.read_text(encoding='utf-8')
j = j.replace('const EDGE_ZONE=72;', 'const EDGE_ZONE=110;')
j = j.replace('const MAX_AUTO_SPEED=13;', 'const MAX_AUTO_SPEED=22;')

# Do not rely on pointer capture for continued tracking; window listeners already track the active pointer.
j = j.replace("  try{s.el.setPointerCapture(s.pointerId)}catch{}\n", "")

# Add immediate edge scroll on pointermove in addition to the RAF loop.
old = '''  e.preventDefault();updateVisual();\n}'''
new = '''  e.preventDefault();\n  // iPhone/Safari: scroll immediately while the finger is near either edge.\n  // The RAF loop below continues scrolling even when the finger is held still.\n  const rect=s.scroll.getBoundingClientRect();\n  let immediate=0;\n  if(s.currentX<rect.left+EDGE_ZONE){\n    const p=Math.max(0,Math.min(1,(rect.left+EDGE_ZONE-s.currentX)/EDGE_ZONE));\n    immediate=-(6+p*16);\n  }else if(s.currentX>rect.right-EDGE_ZONE){\n    const p=Math.max(0,Math.min(1,(s.currentX-(rect.right-EDGE_ZONE))/EDGE_ZONE));\n    immediate=6+p*16;\n  }\n  if(immediate){\n    s.scroll.scrollLeft+=immediate;\n  }\n  updateVisual();\n}'''
if old not in j:
    raise SystemExit('blocked-drag onMove anchor not found')
j = j.replace(old, new, 1)

# Make pointerup/cancel non-passive at window level and keep all tracking global.
j = j.replace("  window.addEventListener('pointerup',onUp);", "  window.addEventListener('pointerup',onUp,{passive:false});")
j = j.replace("  window.addEventListener('pointercancel',onCancel);", "  window.addEventListener('pointercancel',onCancel,{passive:false});")

p.write_text(j, encoding='utf-8')
print('unified blocked drag and strengthened iPhone edge scrolling')
