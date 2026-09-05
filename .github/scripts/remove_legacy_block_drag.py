from pathlib import Path
import re

for name in ['admin.html','bookings.html']:
    p=Path(name)
    s=p.read_text()
    # Remove any legacy visible move handle from red blocked cards.
    s=re.sub(r'\n\s*<span\s+[^>]*class="blockedMoveHandle"[\s\S]*?>\s*↔\s*</span>\s*', '\n', s)
    # Tighten card padding now that the handle is gone.
    s=s.replace('padding:8px 38px 8px 8px;', 'padding:8px;')
    s=s.replace('padding:8px 42px 8px 8px;', 'padding:8px;')
    if name=='admin.html':
        # Stop the old direct-handle drag path. The shared blocked-drag.js is the sole controller.
        s=re.sub(r'\n\s*bindDirectBlockedMove\(\s*block,\s*item,\s*start,\s*end\s*\);\s*', '\n', s)
    p.write_text(s)
    print('cleaned', name)
