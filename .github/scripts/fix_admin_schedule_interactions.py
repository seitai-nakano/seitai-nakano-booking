from pathlib import Path

booking = Path('booking-drag.js')
s = booking.read_text()

# The current admin UI already contains tap edit/delete and the "new booking from this time" action.
required = [
    'blockedInlineBook',
    'bookBlockedAsBooking',
    'nakano-admin-prefill-booking',
    'タップで編集・左右ドラッグで移動',
]
for token in required:
    if token not in s:
        raise SystemExit(f'booking-drag required feature missing: {token}')

# Keep the four editor actions in a stable 2-column layout on small screens as well.
s = s.replace(
    '@media(max-width:500px){.blockedEditorRow{grid-template-columns:1fr 1fr}.blockedEditorActions{grid-template-columns:1fr 1fr 1fr}}',
    '@media(max-width:500px){.blockedEditorRow{grid-template-columns:1fr 1fr}.blockedEditorActions{grid-template-columns:repeat(2,minmax(0,1fr))}}'
)
booking.write_text(s)

blocked = Path('blocked-drag.js')
b = blocked.read_text()

# A planned item itself owns horizontal drag. Blank schedule space remains horizontally scrollable.
if 'touch-action:pan-y;cursor:grab' in b:
    b = b.replace('touch-action:pan-y;cursor:grab', 'touch-action:none;cursor:grab', 1)
elif 'touch-action:none;cursor:grab' not in b:
    raise SystemExit('blocked drag touch-action rule not found')

old = """    originalWidth:parseFloat(el.style.width)||Math.max(36,r.duration*PX_PER_MINUTE),
    interacting:false,ghost:null
  };
}"""
new = """    originalWidth:parseFloat(el.style.width)||Math.max(36,r.duration*PX_PER_MINUTE),
    interacting:false,ghost:null
  };
  // Capture immediately so iPhone/Android/desktop keep sending the same pointer
  // even when the finger or mouse moves across the horizontally scrollable schedule.
  try{el.setPointerCapture(e.pointerId)}catch{}
}"""
if old in b:
    b = b.replace(old, new, 1)
elif 'Capture immediately so iPhone/Android/desktop' not in b:
    raise SystemExit('blocked onDown capture anchor not found')

# Make the interaction contract explicit on every hydrated planned item.
anchor = "  el.dataset.blockedLongDrag='1';\n"
if anchor in b and "el.style.touchAction='none';" not in b:
    b = b.replace(anchor, anchor + "  el.style.touchAction='none';\n", 1)

blocked.write_text(b)
