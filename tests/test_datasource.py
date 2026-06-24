#!/usr/bin/env python3
"""数据源诊断脚本 - 测试各接口是否正常响应

V2.1 2026-06-24 - 新增TDX TCP测试/修复东财reportName

V2.0 修复：
- 东财数据中心改为HTTPS（与实际脚本一致）
- 巨潮资讯使用正确的orgId
- 增加请求间隔防止触发限流
- 百度股市通标记为deprecated
"""
import requests
import time
import json
from datetime import date, timedelta

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/117.0.0.0 Safari/537.36"

# 请求间隔（秒），防止过快请求触发限流
REQUEST_INTERVAL = 1.0


def test_tencent_quote():
    """测试腾讯行情接口"""
    try:
        url = "https://qt.gtimg.cn/q=sh000001"
        r = requests.get(url, headers={"User-Agent": UA}, timeout=10)
        r.encoding = "gbk"
        data = r.text
        if data and "~" in data:
            parts = data.split('"')[1].split("~")
            if len(parts) > 3:
                return {"status": "success", "data": f"上证指数: {parts[3]}"}
        return {"status": "failed", "error": f"返回数据异常: {data[:50]}"}
    except Exception as e:
        return {"status": "failed", "error": str(e)}


def test_eastmoney_datacenter():
    """测试东财数据中心接口（HTTPS版本，与实际脚本一致）
    
    使用实际脚本中真正用到的 reportName: RPT_DAILYBILLBOARD_DETAILSNEW（龙虎榜明细）
    """
    try:
        # 注意：与stock_common.py保持一致，使用HTTPS
        url = "https://datacenter-web.eastmoney.com/api/data/v1/get"
        params = {
            "reportName": "RPT_DAILYBILLBOARD_DETAILSNEW",  # 龙虎榜明细，实际脚本在用
            "columns": "SECURITY_CODE,SECURITY_NAME_ABBR,TRADE_DATE",
            "pageNumber": "1",
            "pageSize": "10",
            "sortColumns": "TRADE_DATE",
            "sortTypes": "-1",
        }
        headers = {
            "User-Agent": UA,
            "Referer": "https://data.eastmoney.com/",
        }
        r = requests.get(url, params=params, headers=headers, timeout=15)
        
        if r.status_code != 200:
            return {"status": "failed", "error": f"HTTP {r.status_code}"}
        
        data = r.json()
        
        if data.get("success") is False:
            return {"status": "failed", "error": f"业务错误: {data.get('message', '未知')}"}
        
        result_data = data.get("result", {})
        if result_data and result_data.get("data"):
            return {"status": "success", "data": f"返回 {len(result_data['data'])} 条龙虎榜数据"}
        
        if result_data and result_data.get("count") == 0:
            return {"status": "success", "data": "接口正常（今日无数据）"}
        
        return {"status": "failed", "error": f"返回格式异常: {str(data)[:100]}"}
    except Exception as e:
        return {"status": "failed", "error": str(e)}


def test_push2_eastmoney():
    """测试东财push2接口"""
    try:
        url = "http://83.push2.eastmoney.com/api/qt/clist/get"
        params = {
            "pn": "1",
            "pz": "10",
            "po": "1",
            "np": "1",
            "fltt": "2",
            "invt": "2",
            "fs": "m:0 t:6,m:0 t:80",
            "fields": "f12,f14,f2,f3"
        }
        r = requests.get(url, params=params, headers={"User-Agent": UA}, timeout=15)
        data = r.json()
        if data.get("data") and data["data"].get("diff"):
            return {"status": "success", "data": f"返回 {len(data['data']['diff'])} 条股票"}
        return {"status": "failed", "error": "返回数据为空"}
    except Exception as e:
        return {"status": "failed", "error": str(e)}


def test_ths_hot_pool():
    """测试同花顺强势股接口"""
    try:
        today_str = date.today().strftime("%Y-%m-%d")
        url = f"http://zx.10jqka.com.cn/event/api/getharden/date/{today_str}/orderby/date/orderway/desc/charset/GBK/"
        r = requests.get(url, headers={"User-Agent": UA}, timeout=10)
        try:
            data = r.json()
        except:
            r.encoding = "GBK"
            data = r.json()
        if str(data.get("errocode", 0)) == "0" and data.get("data"):
            return {"status": "success", "data": f"返回 {len(data['data'])} 条强势股"}
        return {"status": "failed", "error": f"errocode={data.get('errocode')}, 数据量={len(data.get('data', []))}"}
    except Exception as e:
        return {"status": "failed", "error": str(e)}


def test_sina_finance():
    """测试新浪财报接口"""
    try:
        url = "https://quotes.sina.cn/cn/api/openapi.php/CompanyFinanceService.getFinanceReport2022"
        params = {"paperCode": "sh600519", "source": "lrb", "type": "0", "page": "1", "num": "3"}
        r = requests.get(url, params=params, headers={"User-Agent": UA}, timeout=15)
        data = r.json()
        if data.get("result"):
            return {"status": "success", "data": "财报数据正常"}
        return {"status": "failed", "error": "返回数据异常"}
    except Exception as e:
        return {"status": "failed", "error": str(e)}


def test_baidu_finance():
    """测试百度股市通接口（已标记为deprecated）
    
    注意：百度股市通接口可能已变更或停止服务。
    实际脚本中百度仅作为TDX的fallback，TDX正常时不会用到。
    """
    try:
        url = "https://finance.pae.baidu.com/selfselect/get"
        params = {"code": "sh600519", "market": "ab", "tag": "daily"}
        headers = {
            "User-Agent": UA,
            "Referer": "https://gushitong.baidu.com/",
        }
        r = requests.get(url, params=params, headers=headers, timeout=10)
        
        # 检查返回的content-type
        content_type = r.headers.get("Content-Type", "")
        if "text/html" in content_type:
            return {"status": "warning", "data": "返回HTML（接口可能已变更）", "note": "deprecated"}
        
        data = r.json()
        if data.get("ResultCode") == "0":
            return {"status": "success", "data": "百度行情正常"}
        return {"status": "failed", "error": f"ResultCode={data.get('ResultCode')}"}
    except json.JSONDecodeError:
        return {"status": "warning", "data": "JSON解析失败（接口可能已变更）", "note": "deprecated"}
    except Exception as e:
        return {"status": "warning", "error": str(e), "note": "deprecated"}


def test_cninfo():
    """测试巨潮资讯接口（使用正确的orgId）"""
    try:
        # 600519是上交所股票，orgId格式为 gssh0 + 代码
        code = "600519"
        ext_org_id = f"gssh0{code}"
        
        url = "https://www.cninfo.com.cn/new/hisAnnouncement/query"
        payload = {
            "orgId": ext_org_id,
            "stock": f"{code},{ext_org_id}",
            "tabName": "fulltext",
            "pageSize": "5",
            "pageNum": "1",
            "column": "szse",
            "category": "",
            "plate": "",
            "seDate": "2024-01-01~2024-12-31",
            "searchkey": "",
            "secid": "",
            "sortName": "",
            "sortType": "",
            "isHLtitle": "true"
        }
        headers = {
            "User-Agent": UA,
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "https://www.cninfo.com.cn/new/disclosure",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
        }
        r = requests.post(url, data=payload, headers=headers, timeout=15)
        
        if r.status_code != 200:
            return {"status": "failed", "error": f"HTTP {r.status_code}"}
        
        data = r.json()
        if data.get("announcements") and len(data["announcements"]) > 0:
            return {"status": "success", "data": f"返回 {len(data['announcements'])} 条公告"}
        
        total = data.get("totalAnnouncement", 0)
        if total > 0:
            return {"status": "success", "data": f"共 {total} 条公告，本页返回 {len(data.get('announcements', []))} 条"}
        
        return {"status": "failed", "error": f"返回数据为空, totalAnnouncement={total}"}
    except Exception as e:
        return {"status": "failed", "error": str(e)}


def test_tdx_tcp():
    """测试通达信TCP接口（真正的TDX连接，与实际脚本一致）
    
    注意：实际脚本使用TCP协议的mootdx/easy_tdx，不是HTTP接口。
    """
    try:
        import sys
        import os
        # 添加项目根目录到路径
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        from tdx_client import _check_tdx, tdx_get_security_bars
        
        # 第一步：检查TDX连接
        if not _check_tdx():
            return {"status": "failed", "error": "TDX连接失败（easy_tdx可能未安装或服务器不可达）"}
        
        # 第二步：获取K线数据验证
        bars = tdx_get_security_bars("600519", 5)
        if bars and len(bars) == 2 and len(bars[1]) > 0:
            return {"status": "success", "data": f"TDX正常，返回{len(bars[1])}根K线"}
        
        # 第三步：尝试获取行情
        from tdx_client import tdx_get_quote_full
        quote = tdx_get_quote_full("600519")
        if quote and quote.get("price"):
            return {"status": "success", "data": f"TDX行情正常，价格={quote['price']}"}
        
        return {"status": "failed", "error": "TDX连接成功但数据异常"}
    except ImportError as e:
        return {"status": "failed", "error": f"依赖未安装: {e}"}
    except Exception as e:
        return {"status": "failed", "error": str(e)}


def test_eastmoney_reportapi():
    """测试东财研报接口"""
    try:
        url = "https://reportapi.eastmoney.com/report/list"
        params = {
            "pageSize": "10",
            "industry": "*",
            "rating": "*",
            "beginTime": "2024-01-01",
            "endTime": "2030-01-01",
            "pageNo": "1",
            "code": "600519",
            "qType": "0",
        }
        headers = {
            "User-Agent": UA,
            "Referer": "https://data.eastmoney.com/",
        }
        r = requests.get(url, params=params, headers=headers, timeout=15)
        
        if r.status_code != 200:
            return {"status": "failed", "error": f"HTTP {r.status_code}"}
        
        data = r.json()
        if data.get("data") and len(data["data"]) > 0:
            return {"status": "success", "data": f"返回 {len(data['data'])} 条研报"}
        return {"status": "failed", "error": "返回数据为空"}
    except Exception as e:
        return {"status": "failed", "error": str(e)}


def main():
    print("="*70)
    print("数据源诊断测试 V2.0")
    print("="*70)
    print(f"测试日期: {date.today().strftime('%Y-%m-%d')}")
    print(f"请求间隔: {REQUEST_INTERVAL}秒（防止触发限流）")
    
    tests = [
        ("腾讯行情", test_tencent_quote),
        ("东财数据中心", test_eastmoney_datacenter),
        ("东财push2", test_push2_eastmoney),
        ("东财研报", test_eastmoney_reportapi),
        ("同花顺强势股", test_ths_hot_pool),
        ("新浪财报", test_sina_finance),
        ("百度股市通", test_baidu_finance),
        ("巨潮资讯", test_cninfo),
        ("通达信TCP", test_tdx_tcp),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n测试: {name}...", end="", flush=True)
        result = test_func()
        results.append((name, result))
        
        if result["status"] == "success":
            print(f" ✅ {result['data']}")
        elif result["status"] == "warning":
            print(f" ⚠️ {result['data'] if 'data' in result else result['error']}")
            if result.get("note"):
                print(f"      说明: {result['note']}")
        else:
            print(f" ❌ {result['error']}")
        
        # 请求间隔，防止过快请求触发限流
        time.sleep(REQUEST_INTERVAL)
    
    print("\n" + "="*70)
    print("测试总结")
    print("="*70)
    success_count = sum(1 for _, r in results if r["status"] == "success")
    warning_count = sum(1 for _, r in results if r["status"] == "warning")
    fail_count = len(results) - success_count - warning_count
    
    print(f"成功: {success_count}/{len(results)}")
    print(f"警告: {warning_count}/{len(results)}")
    print(f"失败: {fail_count}/{len(results)}")
    
    if fail_count > 0 or warning_count > 0:
        print("\n需要关注的接口:")
        for name, r in results:
            if r["status"] == "failed":
                print(f"  ❌ {name}: {r['error']}")
            elif r["status"] == "warning":
                err = r.get("data", r.get("error", ""))
                print(f"  ⚠️ {name}: {err}")
    
    print("\n" + "="*70)
    print("说明:")
    print("  • ✅ 成功: 接口正常工作")
    print("  • ⚠️ 警告: 接口可能有变化，但不影响主功能（有fallback）")
    print("  • ❌ 失败: 接口异常，需要检查")
    print()
    print("  百度股市通: 仅作为TDX的fallback，TDX正常时不会用到")
    print("  通达信TCP: 实际脚本使用的真正TDX连接（TCP协议）")
    print()
    print("如果多个东财接口同时失败，可能是IP被限流")
    print("建议: 等待一段时间后重试，或检查网络连接")

if __name__ == "__main__":
    main()
