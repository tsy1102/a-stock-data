import sys, time, os
sys.path.insert(0, r"C:/Tencent/WorkBuddy/a-stock-data/docs/field_verification/20260913_em_ulist_crack")
from cdp_scrape import new_tab, get_text, OUT

CODE = "SZ000568"
urls = {
    "main": f"https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/MainTargetAjax?code={CODE}",
    "bs":   f"https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/BalanceSheetAjax?code={CODE}",
    "is":   f"https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/ProfitStatementAjax?code={CODE}",
}
for k, u in urls.items():
    try:
        b, tid, ws = new_tab(u)
        time.sleep(6)
        txt = get_text(ws)
        fn = os.path.join(OUT, f"f10ajax_{k}_000568.txt")
        open(fn, "w", encoding="utf-8").write(txt or "")
        print(f"{k}: len={len(txt or '')} saved {fn}")
        ws.close(); b.close()
    except Exception as e:
        print(k, "ERR", e)
print("DONE")
