"""CDP: 1) 抓行情中心个股页全文(含阶段涨幅标签) 2) 页内 fetch push2 stock/get 全字段(绕过沙箱网络)。"""
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
    r = ws_call(ws, "Runtime.evaluate", {"expression": expr, "returnByValue": True, "awaitPromise": True})
    res = r.get("result", {}).get("result", {})
    if "exceptionDetails" in r.get("result", {}):
        return "EXC:" + str(r["result"]["exceptionDetails"].get("text"))
    return res.get("value")

def fetch_quote(code, market):
    mkt_l = market.lower()
    url = f"https://quote.eastmoney.com/{mkt_l}{code}.html"
    print(f"\n===== {code} quote =====")
    b, tid, ws = new_tab(url)
    time.sleep(16)
    txt = eval_js(ws, "document.body.innerText") or ""
    open(f"{OUT}/quote_full_{code}.txt", "w", encoding="utf-8").write(txt)
    print("  quote text_len=", len(txt))
    # search stage-return keywords
    hits=[l for l in txt.splitlines() if any(k in l for k in ["阶段涨幅","5日","10日","20日","60日","年初至今","一年涨","近三月","近六月"])]
    print("  stage-return hint lines:", len(hits))
    for h in hits[:30]:
        print("   |", h)
    ws.close(); b.close()

def inpage_push2(code, market):
    secid = ("1." if market=="SH" else "0.") + code
    fields = ",".join(f"f{i}" for i in range(1,251))
    url = f"https://push2.eastmoney.com/api/qt/stock/get?secid={secid}&fields={fields}&fltt=2&invt=2"
    expr = f"(async()=>{{try{{const r=await fetch('{url}',{{headers:{{Referer:'https://quote.eastmoney.com/'}}}});const t=await r.text();return t;}}catch(e){{return 'ERR:'+e;}}}})()"
    print(f"\n===== {code} inpage push2 =====")
    b, tid, ws = new_tab("https://quote.eastmoney.com/")
    time.sleep(3)
    res = eval_js(ws, expr)
    ws.close(); b.close()
    if isinstance(res, str) and res.startswith("ERR:"):
        print("  inpage fetch failed:", res)
        return
    try:
        d = json.loads(res)
        sd = d.get("data", {})
        out = {f"f{i}": sd.get(f"f{i}") for i in range(1,251) if sd.get(f"f{i}") not in (None,0,"0","")}
        open(f"{OUT}/push2_{code}.json", "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))
        print("  push2 rc=", d.get("rc"), "nonnull fields:", len(out))
        # print period-return candidates (non-null in f100-f200)
        for i in range(100,201):
            v=sd.get(f"f{i}")
            if v not in (None,0,"0",""):
                print(f"    f{i}={v}")
    except Exception as e:
        print("  parse err:", e, "raw head:", str(res)[:200])

if __name__ == "__main__":
    targets=[("000568","SZ"),("600309","SH")]
    if len(sys.argv)>1:
        cs=sys.argv[1:]
        targets=[(c,"SH" if c.startswith("6") else "SZ") for c in cs]
    for code,mkt in targets:
        inpage_push2(code, mkt)
    for code,mkt in targets:
        fetch_quote(code, mkt)
    print("\nDONE")
