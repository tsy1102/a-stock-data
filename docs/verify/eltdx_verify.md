# eltdx(7709/7615) 字段验证分字典

> 源：eltdx（Rust 内核通达信 7709/7615 客户端，PyPI `eltdx`，Research-Only 许可）
> 采集入口：`scripts/capture_field_probe.py` → `collect_eltdx`（主字典第 24 源，scheme=`eltdx`）
> 状态：V17.2.15 接入；本文件为分字典占位，原始证据由 `docs/field_verification/{YYYYMMDD}/raw_eltdx.json`
> 与 `collide.py` 对撞产出填充。

## 采集覆盖

| 类 | eltdx API | 返回 | 原始字节 |
|---|---|---|---|
| 行情快照 | `client.quotes.get_snapshots([code])` | QuoteSnapshot(23) | `tail_raw`(帧尾) |
| 日K | `client.bars.get(code, period="day", include_raw=True)` | KlineBar(22) | `record_hex` |
| 市场统计 | `client.bars.get("sh880005", period="day")` | KlineSeries | — |
| 0x0010 财务 | `client.corporate.finance_batch(code, include_raw=True)` | FinanceRecord(42) | `finance_info_raw` |
| 短线指标 | `client.helpers.shortline_indicators([codes])` | ShortlineIndicator(41) | — |
| 连板天梯 | `client.helpers.limit_ladder()` | — | — |
| 题材强度 | `client.helpers.theme_strength_rank()` / `stock_theme_strength_rank()` | — | — |
| 成交对比/买卖力道 | `client.helpers.volume_comparison()` / `buy_sell_strength()` | — | — |

## 与 TDX(双命名源) 关系

eltdx 与 easy-tdx 同属通达信 7709/7615 协议源；本项目原 `core/tdx_client.py` 用 easy-tdx，
V17.2.15 起 P0 替换为 eltdx（Rust 握手含 2026-09 新式单条随机 msg_id，移除 `_tdx_handshake_patch.py`）。
字段治理：eltdx 与 TDX 同逻辑源，值级对撞回锚黄金锚（fuyao/东财官网）定中文命名。

**字段契约登记位置（本分字典须与主字典同步）**：eltdx 字段契约登记于主字典
§12.13.10（eltdx Helpers 净新增字段破解：行情快照 / 短线指标 / 连板天梯 / 题材强度 / 成交对比·买卖力道）
与 §12.13.11（eltdx 统一层契约字段 `cdata.eltdx_*`，V17.2.22 接入 canonical）。
本分字典承载 eltdx 专属**采集实证**（`scripts/capture_field_probe.py → collect_eltdx` → `docs/field_verification/{YYYYMMDD}/raw_eltdx.json`）
与**对撞产出**（`collide.py`）；主字典每破解/升级一个 eltdx 字段，须同步在本文件补原始证据（帧字节 / 样本值 / 对撞结论），确保 §12.15.10 强制规则不被绕过。

数据来源：通达信协议（eltdx 7709/7615 客户端）；以上为字段验证分字典框架，不构成投资建议。
