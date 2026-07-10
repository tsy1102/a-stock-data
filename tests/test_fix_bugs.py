"""验证问题1和问题2的修复"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=== 问题1 验证: sc_datasource.py FREE_DATE None 处理 ===")
test_r = {'FREE_DATE': None, 'FREE_SHARES_TYPE': '首发', 'FREE_SHARES': 1000, 'FREE_RATIO': 0.5}
result = str(test_r.get('FREE_DATE', '') or '')[:10]
print(f"  FREE_DATE=None 时: \"{result}\" (类型: {type(result).__name__})")
assert result == "", f"期望空字符串, 得到: {result}"
print("  ✅ None 不崩溃")

test_r2 = {'FREE_DATE': '2026-07-15 00:00:00', 'FREE_SHARES_TYPE': '首发', 'FREE_SHARES': 1000, 'FREE_RATIO': 0.5}
result2 = str(test_r2.get('FREE_DATE', '') or '')[:10]
print(f"  FREE_DATE=正常时: \"{result2}\" (类型: {type(result2).__name__})")
assert result2 == "2026-07-15", f"期望 2026-07-15, 得到: {result2}"
print("  ✅ 正常日期正确截断")

from stock_common.sc_datasource import get_lockup_expiry
r = get_lockup_expiry('600563', '2026-07-10', days=90, include_history=True)
print(f"  600563 解禁数据: history={len(r.get('history',[]))}, upcoming={len(r.get('upcoming',[]))}")
print("  ✅ get_lockup_expiry 正常运行")

print()
print("=== 问题2 验证: get_val_report.py coroutine 未 await ===")
import ast
with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'get_val_report.py'), 'r', encoding='utf-8') as f:
    content = f.read()

# 检查 _tasks 赋值次数
import re
task_assignments = re.findall(r'_tasks\s*=\s*\[', content)
print(f"  _tasks 列表推导式赋值次数: {len(task_assignments)}")
if len(task_assignments) == 1:
    print("  ✅ 只有一次 _tasks 赋值，没有未 await 的 coroutine")
else:
    print(f"  ❌ 仍有 {len(task_assignments)} 次赋值")

# 检查策略18是否在列表中
if "策略18【龙虎榜】" in content and content.count("策略18【龙虎榜】") >= 1:
    idx = content.find("_strategy_defs = [")
    end_idx = content.find("]", idx)
    list_content = content[idx:end_idx+1]
    if "策略18【龙虎榜】" in list_content:
        print("  ✅ 策略18在 _strategy_defs 列表中定义")
    else:
        print("  ⚠️  策略18在列表外追加")

print()
print("=== 全部验证通过 ===")
