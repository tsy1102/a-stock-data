import os, json, time, urllib.request, websocket

CDP = "http://localhost:9333"


def http_get(u, t=15):
    return json.loads(urllib.request.urlopen(u, timeout=t).read())


def ws_call(ws, m, p=None, i=1):
    ws.send(json.dumps({"id": i, "method": m, "params": p or {}}))
    while True:
        r = json.loads(ws.recv())
        if r.get("id") == i:
            return r


def new_tab(url):
    bws = http_get(f"{CDP}/json/version")["webSocketDebuggerUrl"]
    b = websocket.create_connection(bws, timeout=20)
    tid = ws_call(b, "Target.createTarget", {"url": url})["result"]["targetId"]
    for _ in range(20):
        try:
            for t in http_get(f"{CDP}/json"):
                if t.get("id") == tid and t.get("webSocketDebuggerUrl"):
                    return (
                        b,
                        tid,
                        websocket.create_connection(t["webSocketDebuggerUrl"], timeout=20),
                    )
        except Exception:
            pass
        time.sleep(0.5)
    raise RuntimeError("no target")


def ev(ws, expr):
    r = ws_call(ws, "Runtime.evaluate", {"expression": expr, "returnByValue": True})
    return r.get("result", {}).get("result", {}).get("value")


code = "600519"
mkt = "SH"
mcode = mkt + code
url = (
    f"https://emweb.securities.eastmoney.com/pc_hsf10/pages/index.html?type=web&code={mcode}#/cwfx"
)
b, tid, w = new_tab(url)
time.sleep(14)
# enumerate tab-like elements
diag = ev(
    w,
    r"""
(function(){
  var out=[];
  var els=document.querySelectorAll('*');
  for(var i=0;i<els.length;i++){
    var e=els[i];
    var cls=(e.className||'')+'';
    var role=e.getAttribute&&e.getAttribute('role')||'';
    var txt=e.textContent.trim();
    if((/tab/i.test(cls)||role==='tab') && txt && txt.length<20 && e.childElementCount<=2){
      out.push(txt);
    }
  }
  // also collect short texts that look like financial statement names
  var names=['资产负债表','利润表','现金流量表','主要指标','业绩预告','杜邦分析'];
  var found={};
  for(var j=0;j<names.length;j++){
    found[names[j]]=document.body.innerText.indexOf(names[j])>=0;
  }
  return JSON.stringify({tabs:out.slice(0,40), found:found, bodylen:document.body.innerText.length});
})()
""",
)
print("DIAG:", diag)
# try click 资产负债表
clk = ev(
    w,
    r"""
(function(){
  var names=['资产负债表','利润表','现金流量表'];
  for(var n=0;n<names.length;n++){
    var all=document.querySelectorAll('*');
    for(var i=0;i<all.length;i++){
      var e=all[i];
      if(e.childElementCount===0 && e.textContent.trim()===names[n]){
        var p=e; while(p&&p!==document.body){var tag=p.tagName;if(p.getAttribute('role')==='tab'||tag==='A'||tag==='BUTTON'||p.style.cursor==='pointer'||p.onclick){p.click();return 'clicked '+names[n]+' as '+tag;}p=p.parentElement;}
        e.click(); return 'clicked '+names[n]+' leaf';
      }
    }
  }
  return 'nf';
})()
""",
)
time.sleep(6)
txt = ev(w, "document.body.innerText")
has = any(
    k in (txt or '') for k in ['货币资金', '应收账款', '流动资产合计', '资产总计', '未分配利润']
)
print("click result:", clk, "after text_len:", len(txt or ''), "has_bs_items:", has)
# print a snippet around 货币资金 if present
if has:
    idx = txt.find('货币资金')
    print("SNIPPET:", txt[idx - 50 : idx + 200])
b.close()
w.close()
