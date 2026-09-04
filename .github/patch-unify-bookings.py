from pathlib import Path

# admin.html: pass selected existing customer id into admin booking RPC payload.
p=Path('admin.html')
s=p.read_text()
old="""    p_memo:\n      $('memo')\n        .value\n        .trim()\n      ||\n      null\n\n  };\n"""
new="""    p_memo:\n      $('memo')\n        .value\n        .trim()\n      ||\n      null,\n\n    p_customer_id:\n      $('customerSelect').value\n      ||\n      null\n\n  };\n"""
marker="$('addBooking').onclick="
pos=s.find(marker)
if pos<0:
    raise SystemExit('addBooking marker not found')
head=s[:pos]
tail=s[pos:]
if old not in tail:
    raise SystemExit('admin booking payload target not found')
tail=tail.replace(old,new,1)
p.write_text(head+tail)

# customers.html: load standalone manual-booking unify helper beside staff sync helper.
p=Path('customers.html')
s=p.read_text()
tag='<script type="module" src="./staff-edit-sync.js?v=20260816-1"></script>'
newtag=tag+'\n<script type="module" src="./customer-booking-unify.js?v=20260904-1"></script>'
if 'customer-booking-unify.js' not in s:
    if tag not in s:
        raise SystemExit('staff sync script tag not found')
    s=s.replace(tag,newtag,1)
p.write_text(s)
