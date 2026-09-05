from pathlib import Path

p=Path('admin.html')
s=p.read_text(encoding='utf-8')

repls=[
("30分単位で受付可否を変更できます。","15分単位で受付可否を変更できます。"),
("""for(
  let minutes=DAY_START;
  minutes<DAY_END;
  minutes+=30
){""","""for(
  let minutes=DAY_START;
  minutes<DAY_END;
  minutes+=15
){"""),
("""  for(
    let min=DAY_START;
    min<=DAY_END;
    min+=30
  ){

    const time=""","""  for(
    let min=DAY_START;
    min<DAY_END;
    min+=15
  ){

    const time="""),
("""    cell.style.width=
      `${30*PX_PER_MINUTE}px`;

    cell.style.cursor='pointer';
    cell.onclick=event=>{
      event.stopPropagation();
      const quarter=event.offsetX >= (15*PX_PER_MINUTE) ? 15 : 0;
      openTimelineQuickAdd(min+quarter);
    };""","""    cell.style.width=
      `${15*PX_PER_MINUTE}px`;

    cell.style.cursor='pointer';
    cell.onclick=event=>{
      event.stopPropagation();
      openTimelineQuickAdd(min);
    };"""),
("""      const slotEnd=
        slotStart+30;""","""      const slotEnd=
        slotStart+15;""")
]
for old,new in repls:
    if old not in s:
        raise SystemExit('anchor missing: '+old[:80].replace('\n',' '))
    s=s.replace(old,new,1)

s=s.replace('<meta name="nakano-admin-build" content="2026-09-05-manual-booking-v2">','<meta name="nakano-admin-build" content="2026-09-05-manual-booking-v3-15min">',1)

p.write_text(s,encoding='utf-8')
print('native 15-minute admin patched')
