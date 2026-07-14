# -*- coding: utf-8 -*-
"""
龙虎榜数据可用性诊断脚本
=========================

用途：
  1. 直接测试东财数据中心 3 个龙虎榜 API 是否能返回数据；
  2. 测试 stock_common 中 get_dragon_tiger_board / get_recent_dragon_tiger 是否能拿到数据；
  3. 判断 "获取失败" 是接口本身不通、还是时段问题（非交易日/盘中数据未更新）。

用法：
  cd 到项目根目录后运行：
    python tests\\diag_dragon_tiger.py                # 默认测试 3 只典型股票 + 全市场龙虎榜
    python tests\\diag_dragon_tiger.py 600519            # 指定股票代码测试

运行时间：约 30-60 秒

典型使用场景：
  - 短线脚本龙虎榜字段为空或为 0 时，运行此脚本判断是东财接口问题还是脚本逻辑问题
  - 新电脑/新网络环境验证数据接口连通性
  - 非交易时段验证历史数据可用
"""

import sys, os, json, time
from datetime import datetime, date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stock_common import (
    DATACENTER_URL, UA, _request_with_retry, _safe_float,
    get_dragon_tiger_board, get_recent_dragon_tiger,
)


# -----------------------------------------------------------------------------
# 工具函数
# -----------------------------------------------------------------------------

def _h(tag: str, msg: str = "") -> None:
    print("\n" + "=" * 78)
    print(f"  [{tag}] {msg}")
    print("=" * 78)


def _raw_call(report_name: str, filter_str: str, sort_columns: str = "TRADE_DATE",
              sort_types: str = "-1", page_size: int = 20) -> dict:
    """直接调用一次东财 datacenter API，返回完整 JSON（便于肉眼看结构/错误码）。"""
    t0 = time.time()
    r = _request_with_retry(
        DATACENTER_URL,
        params={
            "reportName": report_name,
            "columns": "ALL",
            "filter": filter_str,
            "pageNumber": "1",
            "pageSize": str(page_size),
            "sortColumns": sort_columns,
            "sortTypes": sort_types,
            "source": "WEB",
            "client": "WEB",
        },
        headers={"User-Agent": UA},
        timeout=15,
    )
    dt = time.time() - t0

    if r is None:
        print(f"    ✖ HTTP 请求失败（所有重试耗尽，可能是网络/域名不通），耗时 {dt:.1f}s")
        return {"_status": "http_failed", "http_code": None}

    print(f"    HTTP {r.status_code}  耗时 {dt*1000:.0f}ms  URL: {r.url[:160]}")

    if r.status_code != 200:
        return {"_status": "http_error", "http_code": r.status_code, "text": r.text[:500]}

    try:
        d = r.json()
    except Exception as e:
        return {"_status": "json_error", "http_code": r.status_code, "error": str(e),
                "text_sample": r.text[:300]}

    # 东财常规返回结构: {"version": "...", "result": {"pages":1, "data":[...]}, "success": true, "message": "...", "code": 0}
    # 或: {"result": None, "success": False, "status": -1, "message": "..."}
    status = "ok"
    if isinstance(d, dict):
        if d.get("status") == -1 or d.get("success") is False:
            status = "biz_error"
        elif not d.get("result") or not d["result"].get("data"):
            status = "empty"
    else:
        status = "unexpected"

    return {"_status": status, "http_code": r.status_code, "raw": d}


def _print_summary(res: dict, label: str) -> None:
    s = res.get("_status")
    if s == "ok":
        data = res["raw"]["result"]["data"]
        print(f"    ✅ {label}: 共 {len(data)} 条记录")
        if data:
            row = data[0]
            keys = sorted(row.keys())
            print(f"       可用字段: {', '.join(keys[:30])}{' ...' if len(keys) > 30 else ''}")
            interesting = [k for k in keys if any(p in k.upper() for p in
                           ["TRADE_DATE", "SECURITY_CODE", "SECURITY_NAME",
                            "BILLBOARD_NET_AMT", "EXPLANATION", "OPERATEDEPT",
                            "BUY", "SELL", "NET", "TURNOVER"])]
            for k in interesting[:12]:
                print(f"       - {k}: {row.get(k)}")
    elif s == "empty":
        print(f"    ·  {label}: 接口正常但无数据（result.data 为空列表）")
        msg = (res.get("raw") or {}).get("message") or (res.get("raw") or {}).get("result")
        if isinstance(msg, dict):
            msg = msg.get("msg")
        print(f"       message: {msg}")
    elif s == "biz_error":
        print(f"    ✖ {label}: 业务错误（status=-1 / success=false）")
        print(f"       message: {(res.get('raw') or {}).get('message', '')}  code: {(res.get('raw') or {}).get('code', '')}")
    elif s == "http_error":
        print(f"    ✖ {label}: HTTP {res['http_code']}  {res.get('text','')[:200]}")
    elif s == "json_error":
        print(f"    ✖ {label}: JSON 解析失败 - {res.get('error')}")
        print(f"       text_sample: {res.get('text_sample','')}")
    elif s == "http_failed":
        print(f"    ✖ {label}: HTTP 请求完全失败（检查 DNS/网络/东财是否可用）")
    else:
        print(f"    ? {label}: 未知状态 {s}")


# -----------------------------------------------------------------------------
# 主体
# -----------------------------------------------------------------------------

def main():
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    weekday = now.strftime("%A")

    print("\n" + "#" * 78)
    print(f"# 龙虎榜数据可用性诊断  {now.strftime('%Y-%m-%d %H:%M:%S')}  ({weekday})")
    print("#" * 78)

    hour = now.hour
    is_weekend = now.weekday() >= 5
    if is_weekend:
        print("\n⚠️  当前为周末，交易所休市 → 东财不会更新当日龙虎榜")
        print("    测试将默认使用『上一个交易日』作为查询日期，查看历史数据是否可访问")
    elif hour < 16:
        print(f"\n⚠️  当前为盘前/盘中时段（{hour:02d}:00 前），当日龙虎榜约 16:30 后才会更新")
        print("    若返回『无数据』属于正常现象，脚本同时会回查最近历史数据")
    elif 16 <= hour < 17:
        print(f"\n⌛ 当前为盘后更新时段（{hour:02d}:00），龙虎榜数据可能正在分批发布")
        print("    若某些股票仍无数据，17:00 后再重试通常能拿到完整结果")
    else:
        print(f"\n✅ 当前为盘后稳定时段（{hour:02d}:00 后），龙虎榜数据应已全部发布")

    codes = sys.argv[1:] if len(sys.argv) > 1 else ["600519", "000001", "300750"]
    start_str = (now - timedelta(days=10)).strftime("%Y-%m-%d")

    _h("1", "直接调用东财 datacenter 3 个龙虎榜底层接口")

    for code in codes:
        print(f"\n  ── 股票 {code} ──")
        res_a = _raw_call(
            "RPT_DAILYBILLBOARD_DETAILSNEW",
            filter_str=f'(TRADE_DATE>="{start_str}")(TRADE_DATE<="{today_str}")(SECURITY_CODE="{code}")',
            sort_columns="TRADE_DATE", sort_types="-1", page_size=10,
        )
        _print_summary(res_a, "接口① 上榜明细 RPT_DAILYBILLBOARD_DETAILSNEW")

        latest_date = None
        if res_a.get("_status") == "ok":
            data = res_a["raw"]["result"]["data"]
            if data:
                latest_date = str(data[0].get("TRADE_DATE", ""))[:10]

        if latest_date:
            res_b = _raw_call(
                "RPT_BILLBOARD_DAILYDETAILSBUY",
                filter_str=f'(SECURITY_CODE="{code}")(TRADE_DATE="{latest_date}")',
                sort_columns="BUY", sort_types="-1", page_size=10,
            )
            _print_summary(res_b, f"接口② 买入席位 {latest_date} RPT_BILLBOARD_DAILYDETAILSBUY")
            res_c = _raw_call(
                "RPT_BILLBOARD_DAILYDETAILSSELL",
                filter_str=f'(SECURITY_CODE="{code}")(TRADE_DATE="{latest_date}")',
                sort_columns="SELL", sort_types="-1", page_size=10,
            )
            _print_summary(res_c, f"接口③ 卖出席位 {latest_date} RPT_BILLBOARD_DAILYDETAILSSELL")
        else:
            print("    ·  接口②③:  接口①无上榜记录，跳过席位明细查询（无 date 可查）")

    _h("2", "全市场龙虎榜接口 - 最近 5 日所有上榜股票")

    res_all = _raw_call(
        "RPT_DAILYBILLBOARD_DETAILSNEW",
        filter_str=f'(TRADE_DATE>="{start_str}")(TRADE_DATE<="{today_str}")',
        sort_columns="TRADE_DATE", sort_types="-1", page_size=20,
    )
    _print_summary(res_all, "全市场最近5日龙虎榜")
    if res_all.get("_status") == "ok":
        data = res_all["raw"]["result"]["data"]
        print(f"       前 5 条: {[(str(d.get('SECURITY_CODE','')), str(d.get('SECURITY_NAME','')), str(d.get('TRADE_DATE',''))[:10]) for d in data[:5]]}")

    _h("3", "通过 stock_common.get_dragon_tiger_board 调用（与短线脚本同路径）")

    for code in codes:
        t0 = time.time()
        dtb = get_dragon_tiger_board(code, today_str, days=30)
        dt = time.time() - t0
        recs = dtb.get("records", [])
        inst = dtb.get("institution", {})
        print(f"\n  {code}: {len(recs)} 条上榜记录  (耗时 {dt:.1f}s)")
        print(f"     net_sum_5d={dtb.get('net_sum_5d', 0)}万, net_sum_30d={dtb.get('net_sum_30d', 0)}万, consecutive_net_buy_days={dtb.get('consecutive_net_buy_days', 0)}")
        print(f"     机构席位: 买入 {inst.get('buy_amt', 0)}万, 卖出 {inst.get('sell_amt', 0)}万, 净额 {inst.get('net_amt', 0)}万")
        if recs:
            print(f"     最近1条: date={recs[0]['date']}, reason={recs[0]['reason'][:20]}, net_buy={recs[0]['net_buy']}万, turnover={recs[0]['turnover']}%")
        else:
            print("     （无上榜记录 —— 白马蓝筹 / 最近30日无异动达标属于正常现象）")
        if dtb.get("seats") and (dtb["seats"]["buy"] or dtb["seats"]["sell"]):
            buy_top = dtb["seats"]["buy"][0] if dtb["seats"]["buy"] else None
            sell_top = dtb["seats"]["sell"][0] if dtb["seats"]["sell"] else None
            if buy_top:
                print(f"     买一: {buy_top.get('name', '')[:20]}  净{buy_top.get('net', 0)}万")
            if sell_top:
                print(f"     卖一: {sell_top.get('name', '')[:20]}  净{sell_top.get('net', 0)}万")

    _h("4", "通过 stock_common.get_recent_dragon_tiger(3) 调用")
    t0 = time.time()
    dt_map = get_recent_dragon_tiger(3)
    dt = time.time() - t0
    print(f"\n  耗时 {dt:.1f}s, 返回类型: {type(dt_map).__name__}")
    if isinstance(dt_map, dict):
        n = len(dt_map)
        print(f"  覆盖股票数: {n}")
    elif isinstance(dt_map, list):
        print(f"  列表长度: {len(dt_map)}")
    else:
        print(f"  内容: {repr(dt_map)[:200]}")

    _h("5", "诊断结论")
    print(f"\n  运行时间: {now.strftime('%Y-%m-%d %H:%M:%S')}  ({weekday})")
    if is_weekend:
        print("  → 周末：无新数据属于正常，历史数据应该仍可查")
    elif hour < 16:
        print("  → 盘中：当日龙虎榜约 16:30 后更新，此前可能无当日数据")
    elif 16 <= hour < 17:
        print("  → 更新中：部分股票数据可能尚未公布，17:00 后重试通常可拿到完整结果")
    else:
        print("  → 稳定时段：若仍无数据，通常为该股未达异动标准或接口变化")
    print("\n  若接口①~④全部为『http_failed / http_error / biz_error』，")
    print("  → 说明是东财接口变化 / 网络问题 / 被临时封禁，与时段无关，")
    print()


if __name__ == "__main__":
    main()
