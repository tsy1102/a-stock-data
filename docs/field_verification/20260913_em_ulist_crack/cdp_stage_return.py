"""CDP 抓取东财 F10 /cpbd/zxzb 最新指标页，抽取带标签的 阶段涨幅。"""
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

def get_text(ws):
    return eval_js(ws, "document.body.innerText")

def fetch_zxzb(code, market):
    mcode = market + code
    url = f"https://emweb.securities.eastmoney.com/pc_hsf10/pages/index.html?type=web&code={mcode}&color=b#/cpbd/zxzb"
    print(f"\n===== {code} zxzb =====")
    b, tid, ws = new_tab(url)
    time.sleep(16)
    txt = get_text(ws)
    ws.close(); b.close()
    txt = txt or ""
    open(f"{OUT}/zxzb_{code}.txt", "w", encoding="utf-8").write(txt)
    # extract 阶段涨幅 context
    lines = txt.splitlines()
    out=[]
    capture=False
    for ln in lines:
        if "阶段涨幅" in ln or "涨跌幅" in ln:
            capture=True
        if capture:
            out.append(ln)
        if len(out)>40:
            break
    print("text_len=", len(txt), "stage_ctx_lines=", len(out))
    for l in out[:40]:
        print("  |", l)
    return txt

if __name__ == "__main__":
    targets=[("000568","SZ"),("600309","SH"),("002827","SZ"),("300788","SZ")]
    if len(sys.argv)>1:
        cs=sys.argv[1:]
        targets=[(c,"SH" if c.startswith("6") else "SZ") for c in cs]
    for code,mkt in targets:
        fetch_zxzb(code,mkt)
    print("\nDONE")
