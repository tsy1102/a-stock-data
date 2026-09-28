"""CDP 抓行情中心个股排行页(含5日/20日/60日/年初至今列头)，抽取锚股行值。"""
import sys, os, json, time, urllib.request, websocket

CDP = "http://localhost:9333"
OUT = os.path.dirname(os.path.abspath(__file__)) + "/raw"
os.makedirs(OUT, exist_ok=True)

def http_get(url, timeout=15):
    return json.loads(urllib.request.urlopen(url, timeout=timeout).read())

def ws_call(ws, method, params=None, _id=1):
    ws.send(json.dumps({"id": _id, "method": method, "params": params or {}}))
    while True:
        r = json.loads(ws.recv())
        if r.get("id") == _id:
            return r

def new_tab(url):
    bws = http_get(f"{CDP}/json/version")["webSocketDebuggerUrl"]
    b = websocket.create_connection(bws, timeout=20)
    r = ws_call(b, "Target.createTarget", {"url": url})
    tid = r["result"]["targetId"]
    for _ in range(40):
        try:
            for t in http_get(f"{CDP}/json"):
                if t.get("id") == tid and t.get("webSocketDebuggerUrl"):
                    return b, tid, websocket.create_connection(t["webSocketDebuggerUrl"], timeout=20)
        except Exception:
            pass
        time.sleep(0.5)
    raise RuntimeError("target ws not found " + tid)

def eval_js(ws, expr):
    r = ws_call(ws, "Runtime.evaluate", {"expression": expr, "returnByValue": True})
    res = r.get("result", {}).get("result", {})
    if "exceptionDetails" in r.get("result", {}):
        return "EXC:" + str(r["result"]["exceptionDetails"].get("text"))
    return res.get("value")

def fetch_ranklist():
    url = "https://quote.eastmoney.com/center/ranklist.html"
    print("===== ranklist =====")
    b, tid, ws = new_tab(url)
    time.sleep(18)
    txt = eval_js(ws, "document.body.innerText") or ""
    ws.close(); b.close()
    open(f"{OUT}/ranklist.txt", "w", encoding="utf-8").write(txt)
    print("text_len=", len(txt))
    # headers
    for ln in txt.splitlines():
        if any(k in ln for k in ["5日涨跌幅","20日涨跌幅","60日涨跌幅","年初至今","一年涨跌幅","10日涨跌幅"]):
            print("  HDR:", ln)
    # anchor rows
    for code in ["000568","002827","300788","600309"]:
        idx = txt.find(code)
        if idx>=0:
            seg = txt[idx-30:idx+260]
            print(f"  ROW {code}: ...{seg}...")
        else:
            print(f"  ROW {code}: NOT FOUND")

if __name__ == "__main__":
    fetch_ranklist()
    print("\nDONE")
