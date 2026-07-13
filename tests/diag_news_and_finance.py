#!/usr/bin/env python3
"""东财新闻和新浪财报测试"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from stock_common import _quick_request, UA


def test_eastmoney_news():
    """测试东财新闻接口"""
    print("="*60)
    print("测试1: 东财新闻接口")
    print("="*60)
    
    code = "600519"
    
    # 尝试不同的东财新闻API
    apis = [
        {
            "name": "东财搜索API v1",
            "url": "https://search-api-web.eastmoney.com/search/getSearchResult",
            "params": {"keyword": code, "pageIndex": 1, "pageSize": 10, "type": 1},
            "headers": {"User-Agent": UA, "Referer": "https://so.eastmoney.com/"}
        },
        {
            "name": "东财搜索API v2",
            "url": "https://search-api-web.eastmoney.com/search/getSearchResult",
            "params": {"keyword": code, "pageIndex": 1, "pageSize": 10, "type": 0},
            "headers": {"User-Agent": UA, "Referer": "https://so.eastmoney.com/"}
        },
        {
            "name": "东财个股新闻API",
            "url": "https://push2.eastmoney.com/api/qt/stock/get",
            "params": {"fields": "f57,f58,f116,f117,f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f53,f54", "secid": f"1.{code}" if code.startswith("6") else f"0.{code}"},
            "headers": {"User-Agent": UA}
        },
        {
            "name": "东财资讯API",
            "url": "https://api.eastmoney.com/news/getNewsList",
            "params": {"type": "stock", "code": code, "pageIndex": 1, "pageSize": 10},
            "headers": {"User-Agent": UA}
        },
        {
            "name": "东财滚动新闻",
            "url": "https://www.eastmoney.com/api/rollnews",
            "params": {"type": 0, "pageIndex": 1, "pageSize": 20},
            "headers": {"User-Agent": UA, "Referer": "https://www.eastmoney.com/"}
        }
    ]
    
    for api in apis:
        print(f"\n测试: {api['name']}")
        try:
            r = _quick_request(api['url'], params=api['params'], headers=api['headers'], timeout=15)
            if r:
                try:
                    d = r.json()
                    print(f"  状态码: {r.status_code}")
                    print(f"  返回类型: {type(d).__name__}")
                    
                    if isinstance(d, dict):
                        print(f"  顶层键: {list(d.keys())}")
                        
                        # 检查常见的新闻数据路径
                        for key in ['data', 'result', 'list', 'newsList', 'cmsArticleWebOld', 'cmsArticle']:
                            if key in d:
                                val = d[key]
                                print(f"  {key}: {type(val).__name__}")
                                if isinstance(val, dict):
                                    print(f"    子键: {list(val.keys())[:10]}...")
                                elif isinstance(val, list) and len(val) > 0:
                                    print(f"    长度: {len(val)}")
                                    if isinstance(val[0], dict):
                                        print(f"    第一条键: {list(val[0].keys())[:10]}...")
                                        if 'title' in val[0]:
                                            print(f"    第一条标题: {val[0].get('title', '')[:50]}...")
                except json.JSONDecodeError:
                    print(f"  非JSON响应，内容前200字符: {r.text[:200]}")
            else:
                print("  请求失败")
        except Exception as e:
            print(f"  异常: {e}")


def test_sina_cash_flow():
    """测试新浪现金流量表API"""
    print("\n" + "="*60)
    print("测试2: 新浪现金流量表API")
    print("="*60)
    
    code = "600519"
    prefix = "sh" if code.startswith("6") else "sz"
    paper_code = f"{prefix}{code}"
    
    # 利润表(lrb)、资产负债表(fzb)、现金流量表(xjllb)
    sources = {
        "利润表": "lrb",
        "资产负债表": "fzb",
        "现金流量表": "xjllb",
    }
    
    url = "https://quotes.sina.cn/cn/api/openapi.php/CompanyFinanceService.getFinanceReport2022"
    
    for name, source in sources.items():
        print(f"\n测试 {name} (source={source})...")
        try:
            params = {"paperCode": paper_code, "source": source, "type": "0", "page": "1", "num": "5"}
            r = _quick_request(url, params=params, headers={"User-Agent": UA}, timeout=15)
            if r:
                d = r.json()
                result = (d.get("result") or {}).get("data", {}).get("report_list", {})
                print(f"  返回期次数: {len(result)}")
                
                if result:
                    first_period = list(result.values())[0]
                    items = first_period.get("data", [])
                    print(f"  第一个期次字段数: {len(items)}")
                    
                    titles = [item.get("item_title", "") for item in items]
                    print(f"  字段名: {titles[:20]}...")
                    
                    # 检查关键字段
                    key_fields = ['经营活动产生的现金流量净额', '投资活动产生的现金流量净额', '筹资活动产生的现金流量净额', '现金及现金等价物净增加额']
                    for field in key_fields:
                        if field in titles:
                            print(f"  ✅ 包含字段: {field}")
                        else:
                            print(f"  ❌ 缺少字段: {field}")
            else:
                print("  请求失败")
        except Exception as e:
            print(f"  异常: {e}")


if __name__ == "__main__":
    test_eastmoney_news()
    test_sina_cash_flow()
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)