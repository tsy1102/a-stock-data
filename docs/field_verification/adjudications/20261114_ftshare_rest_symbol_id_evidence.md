# FTShare REST `symbol_id` 来源内实证

## 结论范围

仅处理精确身份 `FTShare REST::symbol_id`，接口为 `GET /api/v1/market/data/daec/stocks/all`。在项目保留期内该接口返回的 A 股样本中，`symbol_id` 是六位证券代码字符串，与同一响应记录 `symbol` 去掉交易所后缀后的数字代码完全相同。定义限定于该 A 股行情列表接口和本次观察范围；不据此声称它是 FTShare 所有接口的通用 ID，不建立跨源映射。

这是一项来源内实证定案，不是官方字段契约。项目契约镜像 `docs/verify/ftshare_rest_contract.md` 将 `symbol` 定义为含交易所后缀的证券代码，并明确把 `symbol_id` 列为“观测但未列入返回字段表”。FTShare 官方文档页面登记于 [A 股行情列表](https://market.ft.tech/gateway/doc/p/mdsj0xyo)；本轮未找到该页面对响应 `symbol_id` 的明确字段释义，因此不把它标为官方契约锚。已验证的 `FTShare REST::symbol` 作为同接口结构锚。

## 路径与解析核对

- `scripts/capture_verified_collectors.py::collect_ftshare_rest` 调用 `stock_common.sc_ftshare.get_a_share_quote_snapshot` 并原样返回采集结果。
- `stock_common/sc_ftshare.py` 调用 `/api/v1/market/data/daec/stocks/all`；解析器用官方 `symbol` 归一化所请求证券，随后以 `stocks[symbol_code] = dict(item)` 保存上游记录。原始 `stocks[*].symbol_id` 没有被本项目计算、改名或转换。
- 每个留存日期的 raw `as_of_date`、来源级 `source_meta.as_of_date`、目录数据日和行情时间戳日期一致。采集时间另行保留；周末补存的 2026-10-30、2026-11-06 快照仍按来源时间戳归到对应交易日，不把运行/采集自然日当作来源数据日。

## 全部可比样本

纳入样本为保留起点 2026-10-15 之后所有存在 `raw_ftshare_rest.json` 的日期：15 个不同来源数据日、同一 20 只 A 股证券，共 300 条记录。每个日期均请求并返回 20 只，缺失证券和意外证券数均为 0；逐行将 `ts_millis` 转为 Asia/Shanghai 后，300/300 的时间戳日期均等于 raw `as_of_date`、来源 `source_meta.as_of_date` 和目录数据日。`symbol_id` 的 300 个值均为 JSON 字符串，格式为六位代码；与 `symbol` 的六位部分逐条精确相等，300/300，无反例或缺字段。20 个股票与标识符配对跨 15 日保持稳定。

| 来源数据日 | 来源采集时间（上海时区） | 返回股票 | 精确相等 | 不匹配 | raw SHA-256 |
|:--|:--|--:|--:|--:|:--|
| 20261020 | 10/20/2026 19:06:29 | 20 | 20 | 0 | `cab385535ab9451cf420882eecc48028b3f2c099d052153333e035b66eeb3f8a` |
| 20261021 | 10/22/2026 07:59:31 | 20 | 20 | 0 | `01953407f526386a9dd3958b1a30d6455b6a78491e98a2a8fa63bdfb132b17c4` |
| 20261023 | 10/23/2026 20:05:28 | 20 | 20 | 0 | `8b63d788ca5109bf17e07606d5638451012812661a537e7e46a1db8808c87872` |
| 20261026 | 10/26/2026 21:20:05 | 20 | 20 | 0 | `4ea51e9a768e78967108606afff474e438ee7847290f2225dcc3418e3c3c5b3b` |
| 20261028 | 10/28/2026 20:19:46 | 20 | 20 | 0 | `4d400a94e5df7120c4973d29e2098f86e87c76b612844d61c71531e700b9944a` |
| 20261029 | 10/29/2026 21:05:37 | 20 | 20 | 0 | `7d066fcfeb435b67cadc533f7a69cc7adca0fc42584e15dfd2c598465ef7a0c4` |
| 20261030 | 11/01/2026 18:05:30 | 20 | 20 | 0 | `e5717fc5371508924b2d6e8d64b632fa38007b80d044271c1e9eae05e61d4845` |
| 20261102 | 11/02/2026 16:28:35 | 20 | 20 | 0 | `a55ffe825571cb4b8fba17fa52cdf3b53cf4d96709fa89aa02210993e940def5` |
| 20261103 | 11/03/2026 21:48:43 | 20 | 20 | 0 | `75fbe7737eb438ae934d7856bac63f7b4a420464ac94eebaf14b6682781f6078` |
| 20261104 | 11/04/2026 18:30:39 | 20 | 20 | 0 | `0994efc1dd4363dd3737b6483ce01699f19004e1f2c71629605ace11a6acc40b` |
| 20261105 | 11/05/2026 20:15:38 | 20 | 20 | 0 | `c7ba377991dce0abd7c6fc7c961ba70c804769f1e2ee887e5c9f0a44e68cb625` |
| 20261106 | 11/08/2026 10:29:32 | 20 | 20 | 0 | `6c5d846caecebdb9b051173d0e5f5464ffd15d007de02b1dbe4d9f0e439e1eb6` |
| 20261109 | 11/09/2026 20:00:26 | 20 | 20 | 0 | `71d82cd91d588f2307ebc8e6d6640528b44717666fa45e566769d7a13dee3c72` |
| 20261110 | 11/10/2026 21:11:37 | 20 | 20 | 0 | `b41c4588296d5e4fc55fee3fe6215daf0bc63cd72aeba99a31685052e67d2332` |
| 20261112 | 11/12/2026 23:22:56 | 20 | 20 | 0 | `57787b013551ef79094e3ad2fccf91d663cee2523637d086f5437c693e6372d6` |

全部逐行原值及换算见 [样本表](../research/20261114_ftshare_rest_symbol_id_samples.csv)；逐日 raw 哈希、覆盖计数和审计边界见 [manifest](../research/20261114_ftshare_rest_symbol_id_manifest.json)。样本表 SHA-256：`cb20c73a16120192b9ddb56b02f57c7c46e0d186ce0f8cfb1b13e6ce3d81bf44`。

## 备选解释与边界

样本直接证明的事实是该接口响应中 `symbol_id` 等于证券代码数字部分。虽然列名含 `id`，但官方没有给出它跨接口唯一性、底层数据库键或与其他市场/品种的映射契约；因此释义不扩张为“全局唯一证券 ID”。同名字段在 FTShare 其他接口中的含义不自动继承。

当前处理只更新该字段的来源内释义与状态；`symbol_id` 仍不是 `official_contract` 锚，不新增 `mappings`，不改变采集或调用逻辑。
