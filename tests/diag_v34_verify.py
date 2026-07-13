#!/usr/bin/env python3
"""V3.4.0 接口验证测试脚本

验证源仓库 V3.4.0 中提到的几个关键问题在本地代码中的状态：
1. 解禁接口字段（able_shares）
2. 行业排名排序（fid=f3）
3. 北向资金（sgt数据可靠性）
4. 东财个股新闻解析
5. 新浪财报三表解析
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, timedelta
from stock_common import (
    eastmoney_datacenter, _request_with_retry, _quick_request, UA,
    get_eastmoney_stock_news, get_sina_balance_sheet, get_sina_financial_report,
    _debug_log,
)


def test_lockup_expiry_fields():
    """测试解禁接口字段是否有 able_shares"""
    print("\n" + "="*60)
    print("测试1: 解禁接口字段（able_shares）")
    print("="*60)
    
    code = "600519"
    today = date.today().strftime("%Y-%m-%d")
    end_date = (date.today() + timedelta(days=90)).strftime("%Y-%m-%d")
    
    filter_str = f"(SECURITY_CODE=\"{code}\")(FREE_DATE>='{today}')(FREE_DATE<='{end_date}')"
    
    try:
        data = eastmoney_datacenter(code, "RPT_LIFT_STAGE",
                                   filter_str=filter_str,
                                   page_size=20,
                                   sort_columns="FREE_DATE",
                                   sort_types="1")
        print(f"返回数据条数: {len(data)}")
        
        if data:
            first = data[0]
            print("\n第一条数据的所有字段:")
            for k, v in sorted(first.items()):
                print(f"  {k}: {v!r}")
            
            print("\n关键字段检查:")
            has_free_shares = "FREE_SHARES" in first
            has_type = "FREE_SHARES_TYPE" in first
            has_able = "ABLE_FREE_SHARES" in first
            
            print(f"  FREE_SHARES (解禁股数): {'✅存在' if has_free_shares else '❌缺失'}")
            print(f"  FREE_SHARES_TYPE (解禁类型): {'✅存在' if has_type else '❌缺失'}")
            print(f"  ABLE_FREE_SHARES (实际可流通股数): {'✅存在' if has_able else '❌缺失'}")
            
            if has_able:
                print(f"  ABLE_FREE_SHARES 值: {first['ABLE_FREE_SHARES']}")
                if first.get("ABLE_FREE_SHARES") != first.get("FREE_SHARES"):
                    print(f"  ⚠️ 注意: ABLE_FREE_SHARES != FREE_SHARES，说明存在限售承诺")
        
    except Exception as e:
        print(f"测试失败: {e}")


def test_industry_ranking_sort():
    """测试行业排名接口是否缺 fid=f3"""
    print("\n" + "="*60)
    print("测试2: 行业排名排序（fid=f3）")
    print("="*60)
    
    url = "https://push2.eastmoney.com/api/qt/clist/get"
    
    # 当前代码（不带 fid=f3）
    params_old = {
        "pn": "1",
        "pz": "100",
        "po": "1",
        "np": "1",
        "fltt": "2",
        "invt": "2",
        "fs": "m:90+t:2",
        "fields": "f2,f3,f4,f12,f13,f14,f104,f105,f128,f136,f140,f141,f207",
    }
    
    # V3.4.0 建议（带 fid=f3）
    params_new = {
        "pn": "1",
        "pz": "100",
        "po": "1",
        "np": "1",
        "fltt": "2",
        "invt": "2",
        "fs": "m:90+t:2",
        "fields": "f2,f3,f4,f12,f13,f14,f104,f105,f128,f136,f140,f141,f207",
        "fid": "f3",  # V3.4.0 新增
    }
    
    headers = {"User-Agent": UA}
    
    try:
        print("测试当前代码（不带 fid=f3）...")
        r_old = _quick_request(url, params=params_old, headers=headers, timeout=15)
        if r_old:
            d_old = r_old.json()
            items_old = d_old.get("data", {}).get("diff", [])
            print(f"  返回条数: {len(items_old)}")
            if items_old:
                print(f"  TOP5 涨跌幅:")
                for i, item in enumerate(items_old[:5]):
                    print(f"    {i+1}. {item.get('f14','')}: {item.get('f3',0)}%")
        
        print("\n测试 V3.4.0 建议（带 fid=f3）...")
        r_new = _quick_request(url, params=params_new, headers=headers, timeout=15)
        if r_new:
            d_new = r_new.json()
            items_new = d_new.get("data", {}).get("diff", [])
            print(f"  返回条数: {len(items_new)}")
            if items_new:
                print(f"  TOP5 涨跌幅:")
                for i, item in enumerate(items_new[:5]):
                    print(f"    {i+1}. {item.get('f14','')}: {item.get('f3',0)}%")
                
                # 对比排序是否一致
                if items_old and items_new:
                    old_names = [i.get('f14','') for i in items_old[:10]]
                    new_names = [i.get('f14','') for i in items_new[:10]]
                    if old_names == new_names:
                        print("\n  ✅ 排序一致，当前代码可能已经正确")
                    else:
                        print("\n  ⚠️ 排序不一致，建议添加 fid=f3")
                        print(f"    当前 TOP10: {old_names}")
                        print(f"    带fid TOP10: {new_names}")
    
    except Exception as e:
        print(f"测试失败: {e}")


def test_northbound_data():
    """测试北向资金数据（sgt可靠性）"""
    print("\n" + "="*60)
    print("测试3: 北向资金数据（sgt可靠性）")
    print("="*60)
    
    url = "https://data.hexin.cn/market/hsgtApi/method/dayChart/"
    headers = {"User-Agent": UA, "Host": "data.hexin.cn", "Referer": "https://data.hexin.cn/"}
    
    try:
        r = _quick_request(url, headers=headers, timeout=10)
        if r:
            d = r.json()
            hgt = d.get("hgt", [])
            sgt = d.get("sgt", [])
            
            print(f"沪股通(hgt)数据点: {len(hgt)}")
            print(f"深股通(sgt)数据点: {len(sgt)}")
            
            if hgt:
                print(f"hgt 最近10个值: {hgt[-10:]}")
            if sgt:
                print(f"sgt 最近10个值: {sgt[-10:]}")
            
            # 检查sgt是否异常
            if len(sgt) < 10 and len(hgt) >= 10:
                print("\n  ⚠️ sgt数据点远少于hgt，符合V3.4.0警示：深股通盘中数据不可靠")
            elif len(sgt) >= len(hgt) * 0.8:
                print("\n  ✅ sgt数据点与hgt相当，当前数据正常")
            
            # 检查末值量级
            if hgt and sgt:
                hgt_last = abs(hgt[-1]) if hgt[-1] else 0
                sgt_last = abs(sgt[-1]) if sgt[-1] else 0
                
                if hgt_last > 0 and sgt_last > 0:
                    ratio = sgt_last / hgt_last
                    print(f"\n  sgt/hgt 末值比例: {ratio:.2f}")
                    if ratio > 3 or ratio < 0.3:
                        print(f"  ⚠️ sgt末值与hgt差异较大，建议谨慎使用")
    
    except Exception as e:
        print(f"测试失败: {e}")


def test_eastmoney_stock_news():
    """测试东财个股新闻解析"""
    print("\n" + "="*60)
    print("测试4: 东财个股新闻解析")
    print("="*60)
    
    code = "600519"
    
    try:
        news = get_eastmoney_stock_news(code, page_size=5)
        print(f"返回新闻条数: {len(news)}")
        
        if news:
            print("\n第一条新闻:")
            for k, v in news[0].items():
                print(f"  {k}: {v!r}")
            
            print("\n所有新闻的关键字段:")
            for i, item in enumerate(news[:3]):
                print(f"  {i+1}. date={item.get('date','')} title={item.get('title','')[:40]}")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()


def test_sina_financial_reports():
    """测试新浪财报三表解析"""
    print("\n" + "="*60)
    print("测试5: 新浪财报三表解析")
    print("="*60)
    
    code = "600519"
    
    try:
        print("测试资产负债表...")
        bs = get_sina_balance_sheet(code)
        print(f"  返回期次: {len(bs)}")
        if bs:
            print(f"  字段: {list(bs[0].keys())[:10]}...")
        
        print("\n测试统一财报接口...")
        fr = get_sina_financial_report(code)
        print(f"  返回类型: {type(fr).__name__}")
        if isinstance(fr, dict):
            print(f"  键: {list(fr.keys())}")
            for k, v in fr.items():
                if isinstance(v, list):
                    print(f"    {k}: {len(v)} 条记录")
                    if v:
                        print(f"      第一条字段: {list(v[0].keys())[:5]}...")
        
        # 检查是否有数据
        if bs:
            print("\n  ✅ 资产负债表有数据")
        else:
            print("\n  ⚠️ 资产负债表无数据，建议核查解析逻辑")
    
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("="*60)
    print("V3.4.0 接口验证测试")
    print("="*60)
    
    test_lockup_expiry_fields()
    test_industry_ranking_sort()
    test_northbound_data()
    test_eastmoney_stock_news()
    test_sina_financial_reports()
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)