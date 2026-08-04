---
name: zhb-dataset-expert
description: >
  ZHB 35 physical columns reference, CanonicalStockData field mapping, and data
  honesty rules for the a-stock-data codebase. Use this skill whenever the user
  is reading ZHB raw dicts, mapping fields into `CanonicalStockData` dataclass,
  or deciding whether to render `0.00%` vs `N/A (需F10)` in reports. Trigger on
  phrases like "ZHB 字段", "CanonicalStockData 字段", "tdxstat.cfg 列",
  "0x0010 协议", "ZHB 没有 ROE", "数据诚实性", "0.00% 误导".
version: 1.0.0
---

# ZHB Dataset Expert Guidelines

ZHB（通达信本地数据）是大 A 报告的"地基"数据源，**约 25-30 个字段**直接可读；超出范围的字段必须**显式标注"需 F10/HTTP 补全"**，不能用 0.00% 伪装。本 skill 把 ZHB 物理边界和 CanonicalStockData 字段映射全部沉淀。

## Rule 1: Respect ZHB Physical Field Boundaries

### ZHB Direct (无需 HTTP fallback)

| 字段 | ZHB key | 单位 | 备注 |
|:---|:---|:---|:---|
| 当前价 | `price` | 元 | |
| 涨跌幅 | `change_pct` | % | |
| 5/10/20/30/60日涨跌 | `change_5d/10d/20d/30d/60d` | % | 30日仅 tdxstat.cfg Col[18] |
| 涨跌停连板 | `streak_days` | 天 | 正=连涨，负=连跌 |
| PE(TTM) | `pe_ttm` | 倍 | |
| 动态PE | `pe_dynamic` | 倍 | |
| PB | `pb` | 倍 | |
| 股息率 | `dividend_yield` | % | |
| 换手率 | `turnover_pct` | % | |
| 主力净买额 | `main_net_buy_wan` | 万元 | |
| 主力净买量 | `main_net_buy_hands` | 手 | |
| 52周高/低 | `high_52w` / `low_52w` | 元 | |
| IPO 发行价 | `ipo_price` | 元 | |
| 成交额 | `amount_wan` | 万元 | |
| 总/流通股本 | `zongguben` / `liutongguben` | 万股 | **0x0010 协议无下划线** |
| 行业代码 | `industry_code` | str | 动态概念板块代码，非固定行业 |
| 员工数 | `employee_count` | 人 | |
| 年初至今涨跌幅 | `change_ytd` | % | |

### ZHB Not Included (需 F10/HTTP 补全)

| 字段 | 数据源 | 备注 |
|:---|:---|:---|
| `ROE` | F10 `_tdx_finance_info` / HTTP | |
| `gross_margin` | F10 | |
| `net_profit_margin` | F10 | |
| `shareholder_count` | F10 `gudongrenshu` | **0x0010 key 无下划线** |
| `dividend_history_details` | F10 | |
| `block_trades` | 龙虎榜 / 大宗交易 | |
| `lockup_expiries` | F10 公告 | |
| `net_profit` | F10 0x0010 `jinglirun` | 元 |
| `eps` | F10 0x0010 `jinglirun/zongguben` 推算 | 元 |
| `industry` (固定行业) | TDX boards | **非 ZHB**，用 `tdx_get_belong_boards()` |
| `operating_cash_flow` | F10 0x0010 `jingyingxianjinliu` | 元 |

**Why**: ZHB 只有 25-30 个物理字段；把"没有"包装成"0.00%"会让用户误以为公司基本面差，而不是数据缺失。

## Rule 2: Data Honesty — Never Default Missing Ratios to 0.00%

When ZHB or F10 does not have a financial ratio (such as `ROE` or `gross_margin`), populate `None` (not `0.00`). Render `N/A (需F10)` in reports so users are never misled by fake zero figures.

```python
# GOOD: 数据诚实
roe = _safe_float(zhb_dict.get("roe"))  # ZHB 没有 → None
if roe is None or roe == 0:
    roe_str = "N/A (需F10)"
else:
    roe_str = f"{roe:.1f}%"

# BAD: 误导性 0
roe = 0.0
roe_str = "0.0%"   # 用户误以为公司 ROE=0 → 不可接受
```

## Rule 3: 0x0010 Protocol Key Naming (V15.1 修正)

The 0x0010 protocol used by TDX `get_finance_info()` uses **no underscores** in field names. Common mistakes corrected in V15.1:

| 错误 key（带下划线） | 正确 key（无下划线） | 字段含义 |
|:---|:---|:---|
| `zong_guben` | `zongguben` | 总股本 |
| `liutong_guben` | `liutongguben` | 流通股本 |
| `gudong_renshu` | `gudongrenshu` | 股东户数 |
| `jing_lirun` | `jinglirun` | 净利润 |
| `jingying_xianjinliu` | `jingyingxianjinliu` | 经营现金流净额 |

```python
# GOOD: V15.1 修正后的 key
total_shares = _safe_float(fi.iloc[0].get('zongguben', 0))
float_shares = _safe_float(fi.iloc[0].get('liutongguben', 0))
_profit = _safe_float(fi.iloc[0].get('jinglirun', 0))
_ocf = _safe_float(fi.iloc[0].get('jingyingxianjinliu', 0))

# BAD: V15.0 错误的 key (返回 0 永远)
total_shares = _safe_float(fi.iloc[0].get('zong_guben', 0))  # KeyError/0
```

## Rule 4: `industry` Field MUST Use TDX Boards (V15.1 B-8/B-9 修正)

The ZHB dict does NOT contain a fixed `industry` field — it has `industry_code` (动态概念板块代码). For the actual industry classification, use `tdx_get_belong_boards()`:

```python
# GOOD: industry 用 TDX boards
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

# ZHB 的 industry_code 仍是"动态概念板块代码"，不是固定行业
industry_code = str(zhb_dict.get("industry_code") or "")
```

## Rule 5: ZHB-First Routing (盘前/盘后/盘中)

`get_canonical_stock_data()` implements ZHB-first routing based on real-time period:

- **盘前 (<09:30) / 假日**: 100% ZHB，零网络
- **盘中/盘后 (09:30-24:00)**: 行情/资金流强制 HTTP/TDX（ZHB 当天包深夜前未生成），其他静态/估值/财务/股本/概念走 ZHB

```python
# Standard ZHB-first pattern in get_canonical_stock_data
def get_canonical_stock_data(code: str, force_realtime: bool = False):
    m_status, _ = get_market_status()
    if m_status in ("closed", "pre_market") and not force_realtime:
        # 盘前/假日：100% ZHB
        return _build_canonical_from_zhb(code)
    else:
        # 盘中/盘后：行情/资金流走 HTTP
        return _build_canonical_hybrid(code)
```

## Output format

```python
# Standard cdata field assignment
cdata = CanonicalStockData(
    code=code_str,
    name=zhb_dict.get("name", ""),
    price=_safe_float(zhb_dict.get("price")),
    change_pct=_safe_float(zhb_dict.get("change_pct")),
    pe_ttm=_safe_float(zhb_dict.get("pe_ttm")),
    pb=_safe_float(zhb_dict.get("pb")),
    # ... 25-30 ZHB fields
    # F10 字段（如 ROE）从 F10 补，缺则 None
    roe=roe_from_f10,  # None if F10 失败
    industry=industry,  # 来自 TDX boards 而非 ZHB
    board=board,
    data_source="zhb",
    time_anchor="t-1",
)
```

## Examples

**Example 1** (V15.1 真实事故)
Input: 用户报 "lng 报告净利润、现金流都显示 0"
Action: 把 `fi.iloc[0].get('jing_lirun', 0)` 改为 `fi.iloc[0].get('jinglirun', 0)`（无下划线）
Output: 净利润、现金流正确显示

**Example 2** (数据诚实性)
Input: 用户报 "新上市公司 ROE 显示 0.0%"
Action: `roe` 缺时改 `None`，渲染 `N/A (需F10)`

**Example 3** (industry 字段缺失)
Input: 用户报 "industry 字段总是空"
Action: ZHB `industry` 字段本来就不存在；改用 `tdx_get_belong_boards()`

## Submission Checklist

- [ ] ZHB 字段名（`zongguben`/`liutongguben`/`gudongrenshu`）无下划线
- [ ] 0x0010 协议字段（`jinglirun`/`jingyingxianjinliu`）无下划线
- [ ] `industry` 字段用 TDX boards 而非 ZHB
- [ ] 缺数据的 F10 字段（ROE/gross_margin 等）渲染 `N/A (需F10)` 而非 `0.00%`
- [ ] CanonicalStockData 字段映射参考 `docs/field_dict.md` 第 7 章
- [ ] 静态分类走 ZHB-first，盘中/盘后行情走 HTTP
- [ ] ZHB 离线优先路由在 `get_canonical_stock_data()` 中实现

## Reference Files

- `references/zhb_columns.md` — 完整 ZHB 35 物理列清单
- `references/canonical_data_mapping.md` — CanonicalStockData 字段映射表
- `references/0x0010_protocol.md` — TDX 0x0010 协议所有正确 key

## External References

- `docs/field_dict.md` 第 7 章 — 字段路由矩阵
- `docs/script_data_dict.md` — 6 大报告字段调用矩阵
- `docs/roadmap.md` — V15.0/V15.1 变更历史
