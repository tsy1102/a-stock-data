#!/usr/bin/env python3
"""使用SKILL.md中的正确接口重新测试4、5、6"""

import sys, os, json, hashlib, urllib.request, ssl
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stock_common import _quick_request, UA

print("=" * 70)
print("使用SKILL.md正确接口重新测试")
print("=" * 70)

# ═══════════════════════════════════════
# 测试1：财联社快讯 - V3.4复活版
# ═══════════════════════════════════════
print("\n\n【测试1】财联社快讯 (SKILL.md V3.4复活版)")
print("-" * 70)

try:
    params = {"appName": "CailianpressWeb", "os": "web", "sv": "7.7.5",
              "last_time": "", "refresh_type": "1", "rn": "50"}
    qs = "&".join(f"{k}={params[k]}" for k in sorted(params))
    sign = hashlib.md5(hashlib.sha1(qs.encode()).hexdigest().encode()).hexdigest()
    url = f"https://www.cls.cn/v1/roll/get_roll_list?{qs}&sign={sign}"
    headers = {"User-Agent": UA, "Referer": "https://www.cls.cn/"}
    
    r = _quick_request(url, headers=headers, timeout=10)
    if r:
        d = r.json()
        print(f"errno: {d.get('errno')}")
        print(f"errmsg: {d.get('errmsg', '')}")
        data = d.get("data", {})
        roll_data = data.get("roll_data", [])
        print(f"快讯数量: {len(roll_data)}")
        if roll_data:
            print(f"\n前5条快讯:")
            for item in roll_data[:5]:
                ts = item.get("ctime")
                import datetime
                t = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S") if ts else ""
                title = item.get("title", "") or item.get("brief", "")
                print(f"  {t} | {title[:60]}")
            print(f"\n字段示例: {list(roll_data[0].keys())[:10]}...")
        else:
            print("roll_data为空")
    else:
        print("❌ 请求失败")
except Exception as e:
    print(f"❌ 异常: {e}")
    import traceback
    traceback.print_exc()


# ═══════════════════════════════════════
# 测试2：互动易问答 - 巨潮cninfo
# ═══════════════════════════════════════
print("\n\n【测试2】互动易问答 (巨潮cninfo)")
print("-" * 70)

try:
    # 第一步：获取orgId
    r1 = _quick_request("https://irm.cninfo.com.cn/newircs/index/queryKeyboardInfo", 
                        method="POST", data={"keyWord": "600519"}, 
                        headers={"User-Agent": UA}, timeout=10)
    if r1:
        d1 = r1.json()
        data1 = d1.get("data", [])
        print(f"第一步返回: {len(data1)}条")
        if data1:
            org_id = data1[0].get("secid")
            print(f"orgId: {org_id}")
            
            # 第二步：获取问答列表（参数放query string）
            import requests
            params = {"_t": 1, "stockcode": "600519", "orgId": org_id, 
                      "pageSize": 10, "pageNum": 1, "keyWord": "", 
                      "startDay": "", "endDay": ""}
            r2 = requests.post("https://irm.cninfo.com.cn/newircs/company/question",
                              params=params, headers={"User-Agent": UA}, timeout=10)
            d2 = r2.json()
            rows = d2.get("rows", [])
            print(f"第二步返回: {len(rows)}条问答")
            if rows:
                print(f"\n前5条问答:")
                for item in rows[:5]:
                    pd = item.get("pubDate")
                    import datetime
                    t = datetime.datetime.fromtimestamp(pd / 1000).strftime("%Y-%m-%d %H:%M") if pd else ""
                    q = item.get("mainContent", "")[:50]
                    a = item.get("attachedContent", "")[:50] if item.get("attachedContent") else "(未回复)"
                    print(f"  [{t}] Q: {q}\n     A: {a}")
                print(f"\n字段示例: {list(rows[0].keys())[:10]}...")
        else:
            print("第一步无数据")
    else:
        print("❌ 第一步请求失败")
except Exception as e:
    print(f"❌ 异常: {e}")
    import traceback
    traceback.print_exc()


# ═══════════════════════════════════════
# 测试3：龙虎榜官方备胎 - 上交所+深交所
# ═══════════════════════════════════════
print("\n\n【测试3】龙虎榜官方备胎 (上交所+深交所)")
print("-" * 70)

today = "2026-07-13"
_ctx = ssl._create_unverified_context()

# 深交所龙虎榜
print("\n--- 深交所龙虎榜 ---")
try:
    su = (f"https://www.szse.cn/api/report/ShowReport/data?SHOWTYPE=JSON"
          f"&CATALOGID=1842_xxpl&TABKEY=tab1&txtStart={today}&txtEnd={today}&random=0.9")
    req = urllib.request.Request(su, headers={"User-Agent": UA,
          "Referer": "https://www.szse.cn/disclosure/supervision/dealinfo/index.html"})
    with urllib.request.urlopen(req, timeout=15, context=_ctx) as r:
        d = json.loads(r.read())
    print(f"返回类型: {type(d).__name__}")
    if isinstance(d, list) and d:
        data = d[0].get("data", [])
        print(f"深交所龙虎榜: {len(data)}条")
        if data:
            print(f"字段示例: {list(data[0].keys())[:10]}...")
            for item in data[:3]:
                print(f"  {item.get('zqdm', '')} {item.get('zqjc', '')} 成交额:{item.get('cjje', '')}")
except Exception as e:
    print(f"❌ 深交所异常: {e}")

# 上交所龙虎榜
print("\n--- 上交所龙虎榜 ---")
try:
    eu = (f"https://query.sse.com.cn/infodisplay/showTradePublicFile.do?"
          f"jsonCallBack=cb&isPagination=false&dateTx={today}")
    req = urllib.request.Request(eu, headers={"User-Agent": UA,
          "Referer": "https://www.sse.com.cn/disclosure/diclosure/public/"})
    with urllib.request.urlopen(req, timeout=15) as r:
        t = r.read().decode("utf-8", "ignore")
    # 解析JSONP
    if "(" in t and ")" in t:
        json_str = t[t.index("(")+1:t.rindex(")")]
        d = json.loads(json_str)
        file_contents = d.get("fileContents", [])
        print(f"上交所龙虎榜文件数: {len(file_contents)}")
        if file_contents:
            print(f"第一条文件内容(前200字符): {file_contents[0][:200]}...")
except Exception as e:
    print(f"❌ 上交所异常: {e}")


# ═══════════════════════════════════════
# 测试4：新浪资金流备胎
# ═══════════════════════════════════════
print("\n\n【测试4】新浪资金流备胎")
print("-" * 70)

try:
    url = "https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/MoneyFlow.ssl_bkzj_bk"
    params = {"page": "1", "num": "20", "sort": "netamount", "asc": "0", "fenlei": "1"}
    r = _quick_request(url, params=params, headers={"User-Agent": UA}, timeout=10)
    if r:
        d = r.json()
        print(f"返回类型: {type(d).__name__}")
        if isinstance(d, list):
            print(f"新浪板块资金流: {len(d)}条")
            if d:
                print(f"字段示例: {list(d[0].keys())[:10]}...")
                for item in d[:5]:
                    print(f"  {item.get('name', '')} 净流入:{item.get('netamount', '')}万元")
except Exception as e:
    print(f"❌ 异常: {e}")


print("\n\n" + "=" * 70)
print("测试完成")
print("=" * 70)
