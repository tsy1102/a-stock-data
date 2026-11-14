# Fuyao 行情快照裸根路径身份退役（2026-11-15）

## 决定

退役五个缺少 `snapshot` 分组的旧登记身份，并将 `canonical` 指向当前采集对象中的完整路径：

| 旧身份 | 当前完整身份 | 官方接口含义 |
|---|---|---|
| `同花顺-fuyao::last_price` | `同花顺-fuyao::snapshot.last_price` | 最新成交价 |
| `同花顺-fuyao::open_price` | `同花顺-fuyao::snapshot.open_price` | 当日开盘价 |
| `同花顺-fuyao::high_price` | `同花顺-fuyao::snapshot.high_price` | 当日最高价 |
| `同花顺-fuyao::low_price` | `同花顺-fuyao::snapshot.low_price` | 当日最低价 |
| `同花顺-fuyao::prev_price` | `同花顺-fuyao::snapshot.prev_price` | 前收盘价 |

这里裁定的是项目采集记录中的路径身份。Fuyao 官方端点的 `data.item[]` 确实包含这些叶字段；项目的适配器提取 item 后，采集器把整条记录保存到 `stocks.<代码>.snapshot`，并不生成 `stocks.<代码>.<字段>` 根键。既有嵌套字段的含义、单位和状态保持不变，不创建跨源映射，也不重审行情值之间的映射。

## 官方契约与当前实现

- [Fuyao 官方行情快照文档](https://fuyao.aicubes.cn/llms-full.txt) 将行情快照定义为 `GET /api/a-share/prices/snapshot`，在 `data.item[]` 中列出五个字段及其中文含义；`last_price`、`open_price`、`high_price`、`low_price`、`prev_price` 均为原始货币计价价格。
- 官方文档说明 `data.timestamp` 是本次快照中最新的上游有效时间。项目 [`stock_common/sc_fuyao.py`](../../../stock_common/sc_fuyao.py) 的 `_items` 仅返回 `data.item`，不保留响应信封；[`scripts/capture_verified_collectors.py`](../../../scripts/capture_verified_collectors.py) 将 item 放入股票记录的 `snapshot` 分组。
- 因而来源级 `as_of_date` 只用于确认这些样本目录的来源日期，不被解释为各价格字段的独立上游时间。本次仅用样本核查路径结构，不据此做跨源数值碰撞或重新定案。

## 保留样本路径审计

仅检查保留边界 `20261015` 起、含 `raw_fuyao.json` 的 18 个日目录，范围止于最新可用样本 `20261112`。逐记录检查根键是否存在（包括值为 `null` 的键）：

- 18 个目录均有 Fuyao `ok` 状态和 20 条股票记录；来源级 `as_of_date` 与目录数据日相符，共 18 个不同来源日期、360 条股票记录。
- 五个裸根路径的键均出现 **0 次**。
- 五个完整 `snapshot.<字段>` 路径各有 **320 条非空观察**，覆盖 16 个目录；`20261015` 和 `20261026` 各有 20 条股票记录未产生 snapshot item，已保留在清单中但不用于字段值推断。
- 逐日期、逐股票、逐字段的根键/嵌套键状态、原始值以及 `raw_fuyao.json`、`meta.json` 的 SHA-256 见 [`20261115_fuyao_snapshot_path_inventory.csv`](../research/20261115_fuyao_snapshot_path_inventory.csv)。
- 没有读取 `20261015` 之前的 raw、ZHB 压缩包或解析缓存。

## 注册表处置边界

五条裸根身份设为 `disproved` / `retired_legacy_path`，分别保留原状态快照并指向同源的完整嵌套路径。`disproved` 表示裸根采集路径不存在；它不否定官方 item 叶字段，也不改变五条已验证嵌套路径的语义裁决。
