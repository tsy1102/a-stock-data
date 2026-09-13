"""
CDP 自驱抓取东方财富网页(端口9333 已登录 Chrome)。
emweb F10 为 SPA：新标签哈希路由不切换内容，须用 Runtime.evaluate 在已开页内
element.click() 真实点击标签页(主要指标/资产负债表/利润表/现金流量表)才露出报表行项目。
用法: py -3.12 cdp_scrape.py [stock...]
"""
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
    # locate target ws url
    for _ in range(20):
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

def click_by_text(ws, label):
    expr = """
    (function(){
      var label=%r;
      var all=document.querySelectorAll('*');
      for(var i=0;i<all.length;i++){
        var e=all[i];
        if(e.childElementCount===0 && e.textContent.trim()===label){
          var p=e;
          while(p && p!==document.body){
            var tag=p.tagName;
            if(p.getAttribute('role')==='tab'||tag==='A'||tag==='BUTTON'||p.style.cursor==='pointer'||p.onclick){
              p.click(); return 'clicked:'+tag;
            }
            p=p.parentElement;
          }
          e.click(); return 'clicked:leaf';
        }
      }
      // fallback: any element containing label text
      for(var i=0;i<all.length;i++){
        var e=all[i];
        if(e.childElementCount<=2 && e.textContent.trim().indexOf(label)>=0){
          e.click(); return 'clicked:partial';
        }
      }
      return 'nf';
    })()
    """ % label
    return eval_js(ws, expr)

def scrape_stock(code, market):
    mcode = market + code  # SH600519 / SZ000568
    print(f"\n===== {code} ({market}) =====")
    # ---- quote page ----
    qurl = f"https://quote.eastmoney.com/{market.lower()}{code}.html"
    try:
        b, tid, wsq = new_tab(qurl)
        time.sleep(9)
        txt = get_text(wsq)
        open(f"{OUT}/quote_{code}.txt", "w", encoding="utf-8").write(txt or "")
        print(f"  quote text_len={len(txt or '')}")
        wsq.close(); b.close()
    except Exception as e:
        print("  quote ERR", e)
    # ---- F10 财务分析(cwfx) 视图，含 主要指标 + 三大报表子标签 ----
    furl = f"https://emweb.securities.eastmoney.com/pc_hsf10/pages/index.html?type=web&code={mcode}#/cwfx"
    try:
        b, tid, wsf = new_tab(furl)
        time.sleep(13)
        txt0 = get_text(wsf)
        open(f"{OUT}/f10_main_{code}.txt", "w", encoding="utf-8").write(txt0 or "")
        print(f"  f10_main(主要指标) text_len={len(txt0 or '')}")
        for tab in ["资产负债表", "利润表", "现金流量表"]:
            r = click_by_text(wsf, tab)
            time.sleep(6)
            txt = get_text(wsf)
            open(f"{OUT}/f10_{tab}_{code}.txt", "w", encoding="utf-8").write(txt or "")
            has_items = any(k in (txt or "") for k in ["货币资金", "营业收入", "经营活动", "未分配利润", "资产总计"])
            print(f"    click {tab} -> {r} text_len={len(txt or '')} has_items={has_items}")
        wsf.close(); b.close()
    except Exception as e:
        print("  f10 ERR", e)

if __name__ == "__main__":
    stocks = [("600519","SH"),("601288","SH"),("000568","SZ")]
    if len(sys.argv) > 1:
        codes = sys.argv[1:]
        stocks = [(c, "SH" if c.startswith("6") else "SZ") for c in codes]
    for code, mkt in stocks:
        scrape_stock(code, mkt)
    print("\nDONE")
