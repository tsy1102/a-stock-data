#!/usr/bin/env python3
"""东财风控限流验证测试

测试目标：验证东财风控是按域名独立限流还是按IP总请求限流

三组对照实验：
  第一组：基准测试 - 单域名1秒间隔（确认安全基线）
  第二组：交叉测试 - 三域名轮询，总QPS≈3（关键验证）
  第三组：串行测试 - 三域名串行，总QPS≈1（对照组）

安全机制：
  - 渐进式启动
  - 熔断机制（1次429/3次失败立即停止）
  - 每组之间冷却5分钟
  - 轻量级请求（pageSize=1）
"""
import requests
import time
import json
import os
from datetime import datetime
from pathlib import Path

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/117.0.0.0 Safari/537.36"

# 三个东财域名的测试接口（与实际脚本一致）
TEST_ENDPOINTS = [
    {
        "name": "datacenter",
        "url": "https://datacenter-web.eastmoney.com/api/data/v1/get",
        "params": {
            "reportName": "RPT_DAILYBILLBOARD_DETAILSNEW",
            "columns": "SECURITY_CODE,SECURITY_NAME_ABBR",
            "pageNumber": "1",
            "pageSize": "1",
            "sortColumns": "TRADE_DATE",
            "sortTypes": "-1",
        },
        "check": lambda r: r.get("success", False) is not False and r.get("result", {}).get("data") is not None,
    },
    {
        "name": "push2",
        "url": "http://83.push2.eastmoney.com/api/qt/clist/get",
        "params": {
            "pn": "1",
            "pz": "1",
            "po": "1",
            "np": "1",
            "fltt": "2",
            "invt": "2",
            "fs": "m:0 t:6,m:0 t:80",
            "fields": "f12,f14,f2,f3",
        },
        "check": lambda r: r.get("data", {}).get("dif") is not None and len(r["data"]["dif"]) > 0,
    },
    {
        "name": "reportapi",
        "url": "https://reportapi.eastmoney.com/report/list",
        "params": {
            "pageSize": "1",
            "industry": "*",
            "rating": "*",
            "beginTime": "2024-01-01",
            "endTime": "2030-01-01",
            "pageNo": "1",
            "code": "600519",
            "qType": "0",
        },
        "check": lambda r: r.get("data") is not None and isinstance(r.get("data"), list),
    },
]

# 日志目录（基于项目根目录的相对路径）
PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "em_rate_limit_test.log"


def log(msg: str):
    """打印并记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def _test_single_endpoint(endpoint: dict) -> tuple:
    """测试单个接口，返回 (success: bool, status_code: int, elapsed: float, error: str)"""
    try:
        headers = {
            "User-Agent": UA,
            "Referer": "https://data.eastmoney.com/",
        }
        t0 = time.time()
        r = requests.get(endpoint["url"], params=endpoint["params"], headers=headers, timeout=15)
        elapsed = time.time() - t0

        # 检测429限流
        if r.status_code == 429:
            return False, 429, elapsed, "429 Too Many Requests"

        if r.status_code != 200:
            return False, r.status_code, elapsed, f"HTTP {r.status_code}"

        try:
            data = r.json()
        except (json.JSONDecodeError, ValueError):
            return False, r.status_code, elapsed, "JSON解析失败"

        # 业务校验
        try:
            if endpoint["check"](data):
                return True, r.status_code, elapsed, ""
            else:
                return False, r.status_code, elapsed, "业务数据为空"
        except Exception as e:
            return False, r.status_code, elapsed, f"校验异常: {e}"

    except Exception as e:
        return False, 0, 0, f"异常: {e}"


def run_test_phase(name: str, endpoints: list, interval: float, duration: int,
                   fail_threshold: int = 3) -> dict:
    """执行一个测试阶段

    Args:
        name: 阶段名称
        endpoints: 要测试的端点列表
        interval: 请求间隔（秒）
        duration: 持续时间（秒）
        fail_threshold: 连续失败阈值（超过则熔断）

    Returns:
        dict: 测试结果统计
    """
    log(f"\n{'='*70}")
    log(f"开始测试: {name}")
    log(f"  端点数量: {len(endpoints)}")
    log(f"  请求间隔: {interval:.2f}秒")
    log(f"  持续时间: {duration}秒")
    log(f"  预计请求数: ~{int(duration / interval)}")
    log(f"{'='*70}")

    results = []
    consecutive_failures = 0
    total_success = 0
    total_fail = 0
    idx = 0
    t_start = time.time()

    while time.time() - t_start < duration:
        endpoint = endpoints[idx % len(endpoints)]
        idx += 1

        success, status_code, elapsed, error = _test_single_endpoint(endpoint)

        if success:
            total_success += 1
            consecutive_failures = 0
            log(f"  ✅ [{endpoint['name']}] 成功 ({elapsed:.2f}s)")
        else:
            total_fail += 1
            consecutive_failures += 1
            log(f"  ❌ [{endpoint['name']}] 失败: {error} (HTTP {status_code})")

            # 熔断：检测到429立即停止
            if status_code == 429:
                log("  🔥 检测到429限流！立即停止测试")
                break

            # 熔断：连续失败超过阈值
            if consecutive_failures >= fail_threshold:
                log(f"  🔥 连续失败{consecutive_failures}次！触发熔断，停止测试")
                break

        results.append({
            "endpoint": endpoint["name"],
            "success": success,
            "status_code": status_code,
            "elapsed": elapsed,
            "error": error,
        })

        # 等待间隔
        time.sleep(interval)

    # 统计
    total = total_success + total_fail
    success_rate = (total_success / total * 100) if total > 0 else 0

    log(f"\n--- {name} 结果 ---")
    log(f"  总请求数: {total}")
    log(f"  成功: {total_success}")
    log(f"  失败: {total_fail}")
    log(f"  成功率: {success_rate:.1f}%")
    log(f"  实际耗时: {time.time() - t_start:.1f}秒")

    if total_fail > 0:
        log("  失败详情:")
        fail_types = {}
        for r in results:
            if not r["success"]:
                key = r["error"]
                fail_types[key] = fail_types.get(key, 0) + 1
        for err, cnt in fail_types.items():
            log(f"    - {err}: {cnt}次")

    return {
        "name": name,
        "total": total,
        "success": total_success,
        "fail": total_fail,
        "success_rate": success_rate,
        "results": results,
        "triggered_fuse": consecutive_failures >= fail_threshold,
    }


def main():
    log("=" * 70)
    log("东财风控限流验证测试")
    log(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log("=" * 70)

    # ========== 热身请求（确认接口正常） ==========
    log("\n[热身] 确认三个接口都正常...")
    all_ok = True
    for ep in TEST_ENDPOINTS:
        success, sc, elapsed, error = _test_single_endpoint(ep)
        if success:
            log(f"  ✅ {ep['name']}: 正常 ({elapsed:.2f}s)")
        else:
            log(f"  ❌ {ep['name']}: 失败 - {error}")
            all_ok = False
        time.sleep(1.0)

    if not all_ok:
        log("\n❌ 热身失败，有接口不可用，取消测试")
        return

    log("\n✅ 热身完成，所有接口正常，开始正式测试")

    all_results = []

    # ========== 第一组：基准测试 ==========
    # 只测push2（已确认安全的接口），1秒1次，持续60秒
    result1 = run_test_phase(
        name="第一组：基准测试（单域名 push2，1秒间隔）",
        endpoints=[TEST_ENDPOINTS[1]],  # 只用push2
        interval=1.0,
        duration=60,
    )
    all_results.append(result1)

    # 检测是否触发熔断
    if result1["triggered_fuse"]:
        log("\n❌ 基准测试都触发熔断！测试终止")
        return

    # 冷却
    log("\n⏳ 冷却5分钟...")
    time.sleep(300)

    # ========== 第二组：交叉测试（关键验证） ==========
    # 三个域名轮询，每个域名间隔0.33秒，总QPS≈3
    result2 = run_test_phase(
        name="第二组：交叉测试（三域名轮询，总QPS≈3）",
        endpoints=TEST_ENDPOINTS,  # 三个域名轮询
        interval=0.33,
        duration=60,
    )
    all_results.append(result2)

    # 冷却
    log("\n⏳ 冷却5分钟...")
    time.sleep(300)

    # ========== 第三组：串行测试（对照组） ==========
    # 三个域名串行，每个域名间隔3秒，总QPS≈1
    result3 = run_test_phase(
        name="第三组：串行测试（三域名串行，总QPS≈1）",
        endpoints=TEST_ENDPOINTS,  # 三个域名串行
        interval=3.0,
        duration=60,
    )
    all_results.append(result3)

    # ========== 最终结论 ==========
    log("\n" + "=" * 70)
    log("测试总结")
    log("=" * 70)

    for r in all_results:
        log(f"\n{r['name']}:")
        log(f"  成功率: {r['success_rate']:.1f}% ({r['success']}/{r['total']})")
        if r["triggered_fuse"]:
            log("  ⚠️  触发熔断")

    # 判定
    log("\n" + "=" * 70)
    log("结论判定")
    log("=" * 70)

    r1, r2, r3 = all_results[0], all_results[1], all_results[2]

    if r2["success_rate"] < r1["success_rate"] - 20 and r2["success_rate"] < r3["success_rate"] - 20:
        log("\n✅ 结论: 东财风控按【IP总请求数】限流")
        log("   证据: 第二组（总QPS≈3）成功率显著低于一、三组")
        log("   建议: 三个东财域名统一全局限流，总QPS≤1")
    elif r2["success_rate"] >= 90 and r3["success_rate"] >= 90:
        log("\n❓ 结论: 无法确定（可能限流阈值更高）")
        log("   证据: 三组成功率都很高")
        log("   建议: 可尝试更高频率进一步测试")
    else:
        log("\n❓ 结论: 测试结果不明确")
        log("   建议: 重新运行测试或调整参数")

    log(f"\n详细日志已保存到: {LOG_FILE}")


if __name__ == "__main__":
    main()
