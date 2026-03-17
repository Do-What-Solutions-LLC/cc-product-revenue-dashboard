"""
Product Revenue Dashboard - Data Refresh Script
Pulls ALL master formula revenue data from NetSuite via SuiteQL REST API
Outputs: product_revenue_all.json
"""
import requests, json, re, os
from datetime import datetime
from requests_oauthlib import OAuth1

NETSUITE_ACCOUNT_ID = os.environ.get("NETSUITE_ACCOUNT_ID", "8469825")
CONSUMER_KEY = os.environ.get("NETSUITE_CONSUMER_KEY", "")
CONSUMER_SECRET = os.environ.get("NETSUITE_CONSUMER_SECRET", "")
TOKEN_ID = os.environ.get("NETSUITE_TOKEN_ID", "")
TOKEN_SECRET = os.environ.get("NETSUITE_TOKEN_SECRET", "")

BASE_URL = f"https://{NETSUITE_ACCOUNT_ID}.suitetalk.api.netsuite.com"
SUITEQL_URL = f"{BASE_URL}/services/rest/query/v1/suiteql"

SUITEQL_QUERY = """SELECT bf.id AS master_id, bf.custitem_formula_code AS formula_code,
    bf.custitem_formula_name AS formula_name, c.companyname AS customer_name,
    c.entityid AS customer_num, i.itemid AS item_name,
    i.custitem_blend_is_formula AS is_bulk, i.custitem_blend_is_multipack AS is_multi,
    ct.displayname AS container_name, NVL(i.custitem_blend_net_weight_lbs, 0) AS net_wt,
    SUM(ABS(tl.amount)) AS revenue, SUM(ABS(tl.quantity)) AS qty,
    TO_CHAR(t.trandate, 'YYYY-MM-DD') AS order_date
FROM transactionline tl
INNER JOIN transaction t ON tl.transaction = t.id
INNER JOIN item i ON tl.item = i.id
INNER JOIN item bf ON i.custitem_blend_base_formula = bf.id
LEFT JOIN customer c ON t.entity = c.id
LEFT JOIN item ct ON i.custitem_blend_container = ct.id
WHERE t.type = 'SalesOrd' AND t.trandate >= TO_DATE('2024-01-01', 'YYYY-MM-DD')
    AND tl.mainline = 'F' AND tl.amount IS NOT NULL AND tl.amount != 0
GROUP BY bf.id, bf.custitem_formula_code, bf.custitem_formula_name,
    c.companyname, c.entityid, i.itemid, i.custitem_blend_is_formula,
    i.custitem_blend_is_multipack, ct.displayname,
    NVL(i.custitem_blend_net_weight_lbs, 0), TO_CHAR(t.trandate, 'YYYY-MM-DD')
ORDER BY bf.id, revenue DESC"""

def create_oauth():
    return OAuth1(client_key=CONSUMER_KEY, client_secret=CONSUMER_SECRET,
        resource_owner_key=TOKEN_ID, resource_owner_secret=TOKEN_SECRET,
        realm=NETSUITE_ACCOUNT_ID, signature_method='HMAC-SHA256')

def fetch_all_pages():
    oauth = create_oauth()
    headers = {"Content-Type": "application/json", "Prefer": "transient"}
    all_items, offset, page_size = [], 0, 1000
    while True:
        url = f"{SUITEQL_URL}?limit={page_size}&offset={offset}"
        print(f"  Fetching offset {offset}...")
        resp = requests.post(url, auth=oauth, headers=headers, json={"q": SUITEQL_QUERY})
        if resp.status_code != 200:
            print(f"  ERROR: {resp.status_code} - {resp.text[:500]}"); break
        items = resp.json().get('items', [])
        all_items.extend(items)
        print(f"  Got {len(items)} records (total: {len(all_items)})")
        if len(items) < page_size: break
        offset += page_size
    return all_items

def derive_pack_size(r):
    if r.get('is_bulk') == 'T': return 'Bulk'
    if r.get('is_multi') == 'T':
        m = re.search(r'(\d+)\s*Pack', r.get('item_name',''), re.IGNORECASE)
        return f'{m.group(1)}x1 Gal' if m else '4x1 Gal'
    cn = r.get('container_name') or ''; name = r.get('item_name','')
    if '330' in cn and 'Tote' in cn: return '330 Gal Tote'
    if '275' in cn and ('Tote' in cn or 'IBC' in cn): return '275 Gal Tote'
    if '200' in cn and 'drum' in cn.lower(): return '200 lb Drum'
    if '55G' in cn: return '55 Gal Drum'
    if '30 GALLON' in cn or '30G' in cn: return '30 Gal Drum'
    if '15G' in cn: return '15 Gal Drum'
    if '5G' in cn or '5-GALLON' in cn or '5 Gallon' in cn or '5GAL' in cn: return '5 Gal Pail'
    if '2.5G' in cn: return '2.5 Gal'
    if '1G' in cn: return '1 Gal'
    m = re.search(r'-(\d+\\.?\d*)G', name)
    if m:
        g = float(m.group(1))
        if g >= 275: return f'{int(g)} Gal Tote'
        if g >= 55: return f'{int(g)} Gal Drum'
        if g >= 15: return f'{int(g)} Gal Drum'
        return f'{int(g)} Gal'
    return 'Other'

def process_data(raw_data):
    compact = []
    for r in raw_data:
        ps = derive_pack_size(r)
        nw = float(r.get('net_wt') or 0); qty = float(r.get('qty') or 0)
        is_bulk = r.get('is_bulk') == 'T'
        true_lbs = qty if is_bulk else (qty * nw if nw > 0 else 0)
        compact.append({'mid':r['master_id'],'fc':r['formula_code'],'fn':r['formula_name'],
            'cn':r.get('customer_name') or 'Unknown','cnum':r.get('customer_num') or '',
            'it':r.get('item_name') or '','ps':ps,'nw':nw,'qty':qty,
            'lbs':round(true_lbs,1),'rev':float(r.get('revenue') or 0),'dt':r.get('order_date') or ''})
    return compact

def main():
    print("="*60); print("Product Revenue Dashboard - Data Refresh (ALL Formulas)")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Account: {NETSUITE_ACCOUNT_ID}"); print("="*60)
    print("\n[1/3] Fetching data from NetSuite...")
    raw = fetch_all_pages()
    if not raw: print("ERROR: No data"); exit(1)
    print(f"  Raw records: {len(raw)}")
    print("\n[2/3] Processing...")
    compact = process_data(raw)
    print(f"  Records: {len(compact)}")
    print(f"  Formulas: {len(set(r['mid'] for r in compact))}")
    print(f"  Revenue: ${sum(r['rev'] for r in compact):,.0f}")
    print("\n[3/3] Saving...")
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'product_revenue_all.json')
    with open(out,'w') as f: json.dump(compact, f, separators=(',',':'))
    print(f"  Saved: {os.path.getsize(out):,} bytes")
    print("\n" + "="*60 + "\nDONE!\n" + "="*60)

if __name__ == "__main__": main()
