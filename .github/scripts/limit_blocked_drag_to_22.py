from pathlib import Path

p=Path('blocked-drag.js')
s=p.read_text()

s=s.replace("const DAY_START=8*60;\nconst PX_PER_MINUTE=2;", "const DAY_START=8*60;\nconst DAY_END=22*60;\nconst PX_PER_MINUTE=2;")
s=s.replace("  const timelineEnd=DAY_START+scroll.scrollWidth/PX_PER_MINUTE;\n\n  if(start<DAY_START||duration<=0||start+duration>timelineEnd+SNAP_MINUTES)return null;", "  const timelineEnd=DAY_END;\n\n  if(start<DAY_START||duration<=0||duration>DAY_END-DAY_START)return null;")
s=s.replace("  const maxStart=s.timelineEnd-s.duration;", "  const maxStart=DAY_END-s.duration;")
s=s.replace("  const snapped=clamp(snapMinutes(s.newStart),DAY_START,s.timelineEnd-s.duration);", "  const snapped=clamp(snapMinutes(s.newStart),DAY_START,DAY_END-s.duration);")

# guard against accidental partial patch
required=["const DAY_END=22*60;","const timelineEnd=DAY_END;","const maxStart=DAY_END-s.duration;","DAY_END-s.duration);"]
for token in required:
    if token not in s:
        raise SystemExit(f'missing expected token: {token}')

p.write_text(s)
