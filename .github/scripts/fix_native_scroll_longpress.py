from pathlib import Path

p=Path('blocked-drag.js')
s=p.read_text()

s=s.replace(".blockedSchedule,.blockedBlock{-webkit-touch-callout:none;touch-action:pan-y;cursor:grab;-webkit-user-select:none;user-select:none}",
            ".blockedSchedule,.blockedBlock{-webkit-touch-callout:none;touch-action:pan-x;cursor:grab;-webkit-user-select:none;user-select:none}")

old="""    // Before long press activates, a real horizontal swipe means schedule scrolling.\n    // Keep the same touch alive instead of dropping it, so the red block itself\n    // can be used as a reliable horizontal-scroll surface on iPhone.\n    if(!s.scrolling && Math.abs(dx)>=LONG_PRESS_CANCEL_DISTANCE && Math.abs(dx)>=Math.abs(dy)){\n      clearTimeout(pressTimer);pressTimer=null;\n      s.scrolling=true;\n    }\n    if(s.scrolling){\n      e.preventDefault();\n      e.stopPropagation();\n      const maxScroll=Math.max(0,s.scroll.scrollWidth-s.scroll.clientWidth);\n      s.scroll.scrollLeft=Math.max(0,Math.min(maxScroll,s.startScrollLeft-dx));\n      return;\n    }\n    // Vertical motion belongs to the page; cancel only the pending long press.\n    if(Math.abs(dy)>=LONG_PRESS_CANCEL_DISTANCE && Math.abs(dy)>Math.abs(dx)){\n      clearTimeout(pressTimer);pressTimer=null;\n    }\n    return;"""
new="""    // Before long press activates, let Safari handle horizontal scrolling natively.\n    // We only cancel the pending long press; we do not preventDefault here.\n    if(!s.scrolling && Math.abs(dx)>=LONG_PRESS_CANCEL_DISTANCE && Math.abs(dx)>=Math.abs(dy)){\n      clearTimeout(pressTimer);pressTimer=null;\n      s.scrolling=true;\n    }\n    if(s.scrolling)return;\n    if(Math.abs(dy)>=LONG_PRESS_CANCEL_DISTANCE && Math.abs(dy)>Math.abs(dx)){\n      clearTimeout(pressTimer);pressTimer=null;\n    }\n    return;"""
if old not in s:
    raise SystemExit('touchmove anchor not found')
s=s.replace(old,new)

s=s.replace("""  if(s.scrolling){\n    // Prevent the post-swipe synthetic click from opening the editor.\n    suppressClickUntil=Date.now()+450;\n    e.preventDefault();\n    return;\n  }""",
            """  if(s.scrolling){\n    // Native Safari scroll already happened; only suppress the synthetic click.\n    suppressClickUntil=Date.now()+450;\n    return;\n  }""")

s=s.replace("el.style.touchAction='none';","el.style.touchAction='pan-x';")
s=s.replace("横スワイプでスクロール・長押ししてから左右に動かして移動","横スワイプでスクロール・0.5秒長押し後に左右へ移動")

p.write_text(s)
print('patched blocked-drag.js for native Safari scroll + long press drag')
