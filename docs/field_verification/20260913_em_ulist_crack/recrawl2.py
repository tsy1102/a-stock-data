import sys, os, time
sys.path.insert(0, r"C:/Tencent/WorkBuddy/a-stock-data/docs/field_verification/20260913_em_ulist_crack")
from cdp_scrape import new_tab, get_text, eval_js, OUT

CODE, MKT = "000568", "SZ"
URL = f"https://emweb.securities.eastmoney.com/pc_hsf10/pages/index.html?type=web&code={MKT+CODE}#/cwfx"

def click_label(ws, label):
    expr = """
    (function(){
      var label=%r;
      var all=document.querySelectorAll('*');
      for(var i=0;i<all.length;i++){
        var e=all[i];
        if(e.childElementCount<=2 && e.textContent.trim()===label){ e.click(); return 'leaf:'+e.tagName; }
      }
      for(var i=0;i<all.length;i++){
        var e=all[i];
        if(e.childElementCount<=3 && e.textContent.trim().indexOf(label)>=0){ e.click(); return 'part:'+e.tagName; }
      }
      return 'nf';
    })()
    """ % label
    return eval_js(ws, expr)

b, tid, ws = new_tab(URL)
time.sleep(13)
UNIQUE = ["递延所得税资产","长期股权投资","应收票据","投资性房地产","商誉","盈余公积","资本公积","归属于母公司股东权益合计","少数股东权益","预计负债"]
def has_bs(txt):
    return [u for u in UNIQUE if u in (txt or "")]

r1 = click_label(ws, "财务报表")
time.sleep(5)
t1 = get_text(ws)
print("after 财务报表 click:", r1, "hasBS:", has_bs(t1))
r2 = click_label(ws, "资产负债表")
time.sleep(8)
t2 = get_text(ws)
print("after 资产负债表 click:", r2, "hasBS:", has_bs(t2))
if has_bs(t2):
    open(os.path.join(OUT, "bs_full2_000568.txt"), "w", encoding="utf-8").write(t2 or "")
    print("SAVED bs_full2_000568.txt len=", len(t2 or ""))
else:
    print("still no detailed BS; len=", len(t2 or ""))
    # also try clicking 利润表 to confirm mechanism
    r3 = click_label(ws, "利润表")
    time.sleep(6)
    t3 = get_text(ws)
    print("after 利润表 click:", r3, "has 营业总收入:", "营业总收入" in (t3 or ""), "len=", len(t3 or ""))
ws.close(); b.close()
print("DONE")
