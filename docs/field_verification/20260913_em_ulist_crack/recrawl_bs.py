import sys, os, time
sys.path.insert(0, r"C:/Tencent/WorkBuddy/a-stock-data/docs/field_verification/20260913_em_ulist_crack")
from cdp_scrape import new_tab, get_text, eval_js, OUT

CODE, MKT = "000568", "SZ"
MC = MKT + CODE
URL = f"https://emweb.securities.eastmoney.com/pc_hsf10/pages/index.html?type=web&code={MC}#/cwfx"
OUTFILE = os.path.join(OUT, "bs_full_000568.txt")

def click_tab(ws, label):
    expr = """
    (function(){
      var label=%r;
      var all=document.querySelectorAll('*');
      for(var i=0;i<all.length;i++){
        var e=all[i];
        if(e.childElementCount<=2 && e.textContent.trim()===label){
          e.click(); return 'clicked-leaf:'+e.tagName;
        }
      }
      for(var i=0;i<all.length;i++){
        var e=all[i];
        if(e.textContent.trim().indexOf(label)>=0 && e.childElementCount<=3){
          e.click(); return 'clicked-partial:'+e.tagName;
        }
      }
      return 'nf';
    })()
    """ % label
    return eval_js(ws, expr)

b, tid, ws = new_tab(URL)
time.sleep(14)
txt0 = get_text(ws)
print("before click len=", len(txt0 or ""), "has 资产总计:", "资产总计" in (txt0 or ""))
# try several candidate labels for the balance-sheet tab
for lab in ["资产负债表", "资产负载表", "资产债表"]:
    r = click_tab(ws, lab)
    time.sleep(7)
    txt = get_text(ws)
    has = "资产总计" in (txt or "") or "货币资金" in (txt or "")
    print(f"click {lab!r} -> {r} len={len(txt or '')} hasBS={has}")
    if has:
        open(OUTFILE, "w", encoding="utf-8").write(txt or "")
        print("SAVED bs_full_000568.txt")
        break
else:
    # dump whatever we have for inspection
    open(OUTFILE, "w", encoding="utf-8").write(txt0 or "")
    print("SAVED fallback (no BS switch)")
ws.close(); b.close()
print("DONE")
