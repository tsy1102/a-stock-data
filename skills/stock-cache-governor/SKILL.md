---
name: stock-cache-governor
description: >
  Cache dirty data prevention (`valid_if` / `_has_zero_price` / `_cross_verify_with_zhb`)
  and ZHB disk bypass rules for stock_cache.py. Use this skill whenever the
  user is editing `@cached` decorators, debugging "cache returned empty dict"
  pollution, or discussing cache TTL/cross_verify semantics. Trigger on phrases
  like "valid_if 校验", "make_valid_if", "缓存污染", "ZHB 旁路",
  "交叉验证", "两次获取一致", "L1 缓存上限", "clear CLI".
version: 1.0.0
---

# Stock Cache Governor Guidelines

V15.2 缓存强化的强约束规则集。解决 3 类历史问题：
1. **空 dict 污染**：HTTP 失败返回 `{}` 被缓存，下次读还是空 → 5743 个 zhb_data 缓存 0 命中
2. **嵌套 0 值漏检**：`_has_zero_price` 仅检查顶层 dict，错过龙虎榜未成交席位
3. **ZHB 交叉验证缺失**：网络瞬断返回的异常值被缓存

## Rule 1: Always Use `make_valid_if` Factory, Not Bare `r is not None`

Every `@cached` decorator MUST use `make_valid_if(check_zeros=True, min_size=N)` factory — never bare `lambda r: r is not None`. The factory rejects None/空 dict/空 list/全 0 字段。

**Why**: `r is not None` 接受 `{}` 和 `[]`（F10 失败时 HTTP 接口普遍返回 `{}`），导致 1000+ 条空缓存污染 SQLite。

```python
# GOOD: factory function
from stock_cache import make_valid_if

@cached(category="f10_fund_flow", trading_day=True,
        valid_if=make_valid_if())  # 拒绝 None/空 dict/全 0
def tdx_get_fund_flow(code: str):
    ...

# GOOD: list/dict 至少 N 条
@cached(category="dragon_tiger", ttl_seconds=TTL["dragon_tiger"], trading_day=True,
        valid_if=make_valid_if(min_size=1))  # 至少 1 条记录才缓存
def get_dragon_tiger_board(code: str, days: int = 30):
    ...

# GOOD: float/int 字段允许 0 值
@cached(category="zhb_data", ttl_seconds=TTL["f10_fund_flow"], trading_day=True,
        valid_if=make_valid_if(check_zeros=False))  # PE=0 是有效的
def get_pe_ttm(code: str) -> Optional[float]:
    ...

# BAD: 仅 None 检查
@cached(category="f10_fund_flow", trading_day=True,
        valid_if=lambda r: r is not None)  # 接受 {} 和 []
def tdx_get_fund_flow(code: str):
    ...
```

## Rule 2: `_has_zero_price` Must Be Recursive (V15.2 修复)

The `_has_zero_price` function in `stock_cache.py` MUST recursively check all nested dict levels (depth ≤ 3) for `price/close/open/high/low == 0` — TDX bad data signature.

**Why**: 龙虎榜未成交席位的子 dict 含 `price=0`；板块列表中无成交板块的嵌套 dict 含 `amount=0`。仅检查顶层会漏过这些脏数据。

```python
# GOOD: recursive check (depth ≤ 3)
def _check_recursive(v, depth=0):
    if depth > 3:
        return False
    if isinstance(v, dict):
        for key in ("price", "close", "open", "high", "low"):
            if v.get(key) == 0:
                return True
        for sub_v in v.values():
            if _check_recursive(sub_v, depth + 1):
                return True
    return False
```

## Rule 3: `_cross_verify_with_zhb` for HTTP Categories

For HTTP-returning categories (`f10_*` / `f10_fund_flow` / `dragon_tiger`), the `set_cache` function MUST call `_cross_verify_with_zhb(code, value)` before persisting. If the HTTP value deviates >50% from ZHB on key fields (`pe_ttm/pb/price/change_pct`), reject the cache.

**Why**: 网络瞬断可能让 HTTP 接口返回异常值（如 price 翻倍），若直接缓存会污染后续读取。

```python
# In set_cache:
if category in ("f10_fund_flow", "f10_announcements", "f10_reminders",
                "f10_financial", "f10_shareholder", "f10_share_capital",
                "f10_news", "dragon_tiger") and args:
    code = args[0] if isinstance(args[0], str) else ""
    if code and not _cross_verify_with_zhb(code, value):
        return  # 偏离 ZHB 过大，拒绝缓存
```

## Rule 4: `cross_verify=True` Means "Two-Fetch Consistent"

For multi-day TTL categories, `cross_verify=True` enables true two-fetch verification: first write saves `verified=0`; second fetch matching `prev_value` flips to `verified=1`; mismatches keep `verified=0`. `get_cache(..., cross_verify=True)` returns None for unverified entries.

**Why**: V10.0 简化版"valid_if 通过即 verified=1" 在实时数据场景下会缓存偏离值；真正的"两次一致"语义能过滤网络瞬断。

```python
# GOOD: set_cache cross_verify=True branch
if not cross_verify:
    # 普通模式：直接写入，不验证
    cursor.execute("INSERT OR REPLACE ... verified=0", ...)
else:
    # 交叉验证模式：第一次 verified=0，第二次相同 verified=1
    with _db_lock:
        row = cursor.execute("SELECT value, prev_value, verified FROM ...").fetchone()
        if row is None:
            cursor.execute("INSERT ... verified=0", ...)  # 第一次
        else:
            existing_blob, prev_value_blob, verified = row
            if prev_value_blob == value_bytes:
                cursor.execute("UPDATE SET verified=1 ...", ...)  # 第二次一致
            else:
                cursor.execute("UPDATE SET verified=0 ...", ...)  # 第二次不一致
```

## Rule 5: L1 缓存上限 10000

`_L1_MAX_ENTRIES = 10000` (V15.2 从 5000 升级)。val 报告 5721+ zhb_data 在 5000 上限下频繁淘汰，导致重复读 L2 SQLite + 重复 I/O。

## Rule 6: Enforce `_ZHB_BYPASS_CATEGORIES` Disk Bypass

Static and ZHB-covered categories (`basic_info_static`, `share_capital`, `concept_blocks`, `board_type`) MUST be included in `_ZHB_BYPASS_CATEGORIES` in `stock_cache.py` to bypass SQLite disk writes completely.

## Rule 7: `clear` CLI for Recovery

Run `python stock_cache.py clear --category <name>` to recover from polluted cache. The CLI supports `--category` and `--pattern` (code filter).

```bash
python stock_cache.py clear --category zhb_data        # 清空全部 zhb_data
python stock_cache.py clear --category dragon_tiger    # 清空龙虎榜
python stock_cache.py clear --category f10_fund_flow --pattern 600519  # 清空单只
python stock_cache.py clear-expired                    # 清过期
python stock_cache.py clear-all                        # 清全部
```

## Output format

```python
# Standard @cached decorator pattern in tdx_client.py
from stock_cache import cached, make_valid_if

@cached(category="<category_name>", ttl_seconds=TTL["<key>"], trading_day=True,
        valid_if=make_valid_if())  # 或 make_valid_if(min_size=1) / check_zeros=False
def <func_name>(code: str, ...):
    ...
```

## Examples

**Example 1** (V15.2 真实事故)
Input: 用户报 "zhb_data 缓存 5743 个全部 0 命中，hit_count 都是 0 或 1"
Action:
1. 检查 `data_provider.py` 中 12 个 `@cached(category="zhb_data", ...)` 函数
2. 把 `valid_if=lambda r: r is not None` 全部改为 `valid_if=make_valid_if(...)`
3. `python stock_cache.py clear --category zhb_data` 清空脏数据
Output: 缓存命中率恢复，无空 dict 污染

**Example 2** (V15.2 龙虎榜嵌套 0 值)
Input: 用户报 "龙虎榜缓存被空 list 污染"
Action: 把 `_has_zero_price` 从顶层检查改为递归（Rule 2）；`valid_if` 用 `make_valid_if(min_size=1)`

**Example 3** (V15.2 性能)
Input: 用户报 "val 报告 1000s 跑完，zhb_data 频繁淘汰"
Action: `_L1_MAX_ENTRIES = 5000` 改为 `10000`

## Submission Checklist

- [ ] 所有 `@cached` 装饰器使用 `make_valid_if(...)` factory（非 bare lambda）
- [ ] `_has_zero_price` 递归实现（depth ≤ 3）
- [ ] `set_cache` 集成 `_cross_verify_with_zhb`（F10/dragon_tiger 分类）
- [ ] `cross_verify=True` 真实现"两次一致"语义
- [ ] `_L1_MAX_ENTRIES = 10000`
- [ ] 4 个静态分类在 `_ZHB_BYPASS_CATEGORIES` 中
- [ ] 修改 valid_if 策略后 `python stock_cache.py clear --category <name>` 清脏数据
- [ ] CLI 文档更新（README / CHANGELOG）

## Reference Files

- `references/valid_if_recipes.md` — 各种数据类型的 `make_valid_if` 参数组合
- `references/ttl_tuning.md` — TTL 调优矩阵（trading_day / 7d / 30d / 90d 的适用场景）
