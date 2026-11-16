import sqlite3, sys, datetime

db = sys.argv[1]
con = sqlite3.connect(f"file:{db}?mode=ro&immutable=1", uri=True)
cur = con.cursor()
cols = [r[1] for r in cur.execute("PRAGMA table_info(downloads)")]
want = [c for c in ["id", "guid", "current_path", "target_path", "start_time", "received_bytes",
                    "total_bytes", "state", "danger_type", "interrupt_reason", "end_time",
                    "mime_type", "original_mime_type", "tab_url", "site_url"] if c in cols]


def t(us):
    if not us:
        return ''
    return (datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=us)).strftime('%Y-%m-%d %H:%M:%S UTC')


rows = cur.execute(f"SELECT {','.join(want)} FROM downloads ORDER BY id DESC LIMIT 4").fetchall()
for r in rows:
    d = dict(zip(want, r))
    for k in ("start_time", "end_time"):
        if k in d:
            d[k] = t(d[k])
    for k in ("tab_url", "site_url"):
        if k in d and d[k]:
            d[k] = d[k][:90]
    print(d)
    for (u,) in cur.execute("SELECT url FROM downloads_url_chains WHERE id=? ORDER BY chain_index", (d['id'],)):
        print("   chain:", u[:110])
    print()
