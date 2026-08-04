---
name: board-safety
description: >
  Variable scope and UnboundLocalError prevention guidelines for the a-stock-data
  codebase (data_provider.py, get_*_report.py, tdx_client.py). Use this skill
  whenever the user is editing Python files that build dicts/lists inside
  try/except blocks, dereference nested fields like `boards["area"][0]`, or
  debugs the recurring crash "UnboundLocalError: local variable 'X' referenced
  before assignment" — especially for `board`/`industry`/`concepts` in
  get_canonical_stock_data. Trigger on phrases like "变量未初始化",
  "UnboundLocalError 修复", "board 取不到", "try 块外初始化".
version: 1.0.0
---

# Board & Scope Safety Guidelines

V15.2 P0 crash 修复后的强约束规则集。2026-07-28 一次 35 只 sht/med/lng 股票全部失败的根因就是 `board = boards["area"][0].get("name", "")` 在 `try` 内执行而 `board` 变量在 `try` 外未初始化。本 skill 把这条经验沉淀为 4 条不可违反的规则。

## Rule 1: Always Initialize Variables Outside Try Blocks (P0 必读)

Every variable that will be dereferenced or evaluated outside or **after** a `try...except` block MUST be initialized with a safe default value BEFORE entering the `try` block.

**Why**: Python 在 `try` 块内任何分支未执行时，块外就找不到该变量名；旧的 `if not board: board = ''` 死代码检查只能在 `board` 已绑定的前提下工作，一旦 `try` 内连一个分支都没走到，绑定就没发生，触发 `UnboundLocalError` —— **35 只股票 100% 失败的根因**。

```python
# GOOD: safe default initialization BEFORE try block
industry = ""
board = ""
try:
    from tdx_client import tdx_get_belong_boards
    boards = tdx_get_belong_boards(code_str)
    if boards and boards.get("industry"):
        industry = boards["industry"][0].get("name", "")
    if boards and boards.get("area"):
        board = boards["area"][0].get("name", "")
except Exception as _e:
    _debug_log(f"tdx boards error: {_e}")

# Safe evaluation guaranteed (no UnboundLocalError possible)
industry_code = str(zhb_dict.get("industry_code") or "")
```

```python
# BAD: variable bound INSIDE try, used OUTSIDE
try:
    boards = tdx_get_belong_boards(code_str)
    if boards and boards.get("area"):
        board = boards["area"][0].get("name", "")
except Exception:
    pass
if not board:           # ← NameError / UnboundLocalError if area missing
    board = ""
```

## Rule 2: Never Assume Dict Key Existence

When accessing nested dict structures (e.g. `boards["area"][0]`), always check that the list is non-empty before indexing into element 0.

**Why**: `boards.get("area")` may return `[]` (empty list) or `None` (key absent). Indexing `[][0]` raises `IndexError`, and `None[0]` raises `TypeError` — 两者都让 `try` 块中断，但中断后块外访问仍可能触发 `UnboundLocalError`。

```python
# GOOD: empty-list guard before [0]
if boards and boards.get("area"):
    area = boards["area"]      # already verified non-empty
    if area:                   # double-check length
        board = area[0].get("name", "")
```

## Rule 3: Always Use `or ""` / `or 0` for Optional Numeric/Str Coercion

When extracting a value from ZHB dict that may be missing, use `_safe_float()` or `or 0` / `or ""` — never assume the value is present.

```python
# GOOD
pe_ttm = _safe_float(zhb_dict.get("pe_ttm"))
change_5d = _safe_float(zhb_dict.get("change_5d", 0))

# BAD
pe_ttm = zhb_dict["pe_ttm"]   # KeyError if missing
```

## Rule 4: Move Imports Inside `try` for Optional Dependencies

For `try` blocks that import heavy / optional modules (e.g. `from tdx_client import tdx_get_belong_boards`), keep the import INSIDE the try. The `try` then guards both the import and the call.

## Output format (P0 修复后)

```python
# Standard board/industry assignment block in data_provider.py
industry = ""
board = ""
try:
    from tdx_client import tdx_get_belong_boards
    boards = tdx_get_belong_boards(code_str)
    if boards and boards.get("industry"):
        industry = boards["industry"][0].get("name", "")
    if boards and boards.get("area"):
        board = boards["area"][0].get("name", "")
except Exception as _e:
    _debug_log(f"get_canonical_stock_data tdx boards error: {_e}")
# V15.2: 死代码 if not board: board = '' 已删除（board 已在 try 块外初始化）
industry_code = str(zhb_dict.get("industry_code") or "")
```

## Examples

**Example 1** (V15.2 P0 真实事故)
Input: 用户报 "sht 报告 35 只股票全部失败，错误 `UnboundLocalError: local variable 'board'`"
Action:
1. 定位 `data_provider.py` 327-340 行附近
2. 把 `board = ''` 移出 `try` 块
3. 删除 `if not board: board = ''` 死代码
4. 验证 `data_provider.py` 语法
Output: 35 只股票恢复运行，无 UnboundLocalError

**Example 2** (预防)
Input: 用户报 "新增字段 `concepts` 总是空"
Action: 检查 `concepts` 变量是否在 `try` 内赋值而在 `try` 外读；若是，按 Rule 1 改为 `concepts_list = []` 在 `try` 外初始化

## Submission Checklist

- [ ] 每个在 `try` 块内**首次绑定**的变量名，都在 `try` 块外初始化为空值
- [ ] 嵌套 dict 访问用 `if x and x.get("k")` 保护
- [ ] `try` 块内 import 模块时 import 放在 `try` 第一行
- [ ] 死代码（`if not X: X = ""`）已删除
- [ ] `_debug_log` 写明数据源 + 字段名（`tdx boards error` 而非 `error`）
