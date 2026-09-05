from pathlib import Path

p=Path('booking-drag.js')
s=p.read_text()
old="""async function validateBlockedRange(item,start,end){
  const date=item.blocked_date||selectedDate(),s=timeToMinutes(start),e=end==='23:59'?24*60:timeToMinutes(end);if(!Number.isFinite(s)||!Number.isFinite(e)||e<=s)return'終了時間は開始時間より後にしてください。';
  const{data,error}=await supabase.from('nakano_bookings').select('id,start_time,minutes,customer_name').eq('booking_date',date).eq('status','confirmed');if(error)return'予約状況を確認できませんでした。';
  const hit=(data||[]).find(b=>overlaps(s,e,timeToMinutes(b.start_time),timeToMinutes(b.start_time)+(Number(b.minutes)||30)));if(hit)return`${String(hit.start_time).slice(0,5)}の予約と重なります。先に予約時間を調整してください。`;
  return'';
}
"""
new="""async function validateBlockedRange(item,start,end){
  const date=item.blocked_date||selectedDate(),s=timeToMinutes(start),e=end==='23:59'?24*60:timeToMinutes(end);
  if(!Number.isFinite(s)||!Number.isFinite(e)||e<=s)return'終了時間は開始時間より後にしてください。';

  const bookingResult=await supabase.from('nakano_bookings').select('id,start_time,minutes,customer_name').eq('booking_date',date).eq('status','confirmed');
  if(bookingResult.error)return'予約状況を確認できませんでした。';
  const bookingHit=(bookingResult.data||[]).find(b=>overlaps(s,e,timeToMinutes(b.start_time),timeToMinutes(b.start_time)+(Number(b.minutes)||30)));
  if(bookingHit)return`${String(bookingHit.start_time).slice(0,5)}の予約と重なります。先に予約時間を調整してください。`;

  const blockedResult=await supabase.from('nakano_blocked_times').select('id,start_time,end_time,memo').eq('blocked_date',date).neq('id',item.id);
  if(blockedResult.error)return'他の予定を確認できませんでした。';
  const blockedHit=(blockedResult.data||[]).find(x=>overlaps(s,e,timeToMinutes(x.start_time),blockEndMinutes(x.end_time)));
  if(blockedHit){
    const bs=String(blockedHit.start_time).slice(0,5),be=displayEndTime(blockedHit.end_time);
    return`別の予定（${bs}〜${be}）と重なります。重ならない時間に変更してください。`;
  }
  return'';
}
"""
if old not in s:
    raise SystemExit('validateBlockedRange anchor not found')
s=s.replace(old,new,1)
p.write_text(s)
