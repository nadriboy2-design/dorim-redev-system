import sys, os, csv, urllib.request, urllib.parse
import xml.etree.ElementTree as ET
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
KEY = os.environ["DATA_GO_KR_KEY"]
BASE = "https://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev"
def fetch(lawd, ymd):
    rows, page = [], 1
    while True:
        q = urllib.parse.urlencode({"LAWD_CD": lawd, "DEAL_YMD": ymd, "pageNo": page, "numOfRows": 1000})
        url = f"{BASE}?serviceKey={KEY}&{q}"
        with urllib.request.urlopen(url, timeout=30) as r:
            data = r.read()
        root = ET.fromstring(data)
        code = root.findtext(".//resultCode")
        if code not in (None, "00", "000"):
            raise RuntimeError(f"API {code}: {root.findtext('.//resultMsg')}")
        total = int(root.findtext(".//totalCount") or 0)
        got = [{c.tag: (c.text or "").strip() for c in it} for it in root.iter("item")]
        rows += got
        if len(rows) >= total or not got:
            return rows
        page += 1
if __name__ == "__main__":
    lawd = sys.argv[1]; a, b = sys.argv[2], sys.argv[3]; out = sys.argv[4]
    y, m = int(a[:4]), int(a[4:]); ey, em = int(b[:4]), int(b[4:])
    allr, fails = [], []
    while (y, m) <= (ey, em):
        ymd = f"{y}{m:02d}"
        try:
            r = fetch(lawd, ymd); allr += r; print(ymd, len(r))
        except Exception as e:
            fails.append(ymd); print(ymd, "FAIL", str(e)[:80])
        m += 1
        if m > 12: y, m = y + 1, 1
    keys = sorted({k for r in allr for k in r})
    with open(out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(allr)
    print("total", len(allr), "fails", fails)
