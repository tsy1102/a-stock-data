# TDX 0x0010 兼容财务别名批量核验（2026-11-21）

## 结论与范围

本批审查 15 个 Easy-TDX 财务解析器下划线路径及 `reserve2`。这不是 15 个新的独立底层字段：项目 `_EasyTdxAdapter.finance()` 会为每个含下划线的字段生成删除下划线的兼容键。保留的 2026-11-10 同次响应包含 20 条 `record_hex`；安装环境 easy-tdx 1.20.8 的文件与固定仓库提交 `41e56376fafa3abae0f6538f271eafd6af26d27f` 内容哈希一致。

```text
easy-tdx parser SHA-256: 0f7baa655709e9a203c55a24aa85747f5b2dc3aa7074aec07b3fa9375d4e56ab
FinanceInfo model SHA-256: e1831d93aff976c4f97d2ffc3c21c9f92da758ceb2acf75a9e7c7cab9ea337b0
```

## 下划线字段与已验证同源路径

逐条重放 `record_hex` 后，15 个字段的解析值与项目生成的去下划线兼容键共 300/300 精确相等。除 `zhigong_gu` 外，其余 14 个字段又与同一 0x0010 记录在 ELTDX 路径中的对应字段及当前适配器转换 280/280 精确相等。

| Easy-TDX path | Verified same-source path | Result |
|---|---|---|
| `b_gu` | `bgu` | alias 20/20; 20/20 ELTDX exact |
| `changqi_fuzhai` | `changqifuzhai` | alias 20/20; 20/20 ELTDX exact |
| `guojia_gu` | `guojiagu` | alias 20/20; 20/20 ELTDX exact |
| `h_gu` | `hgu` | alias 20/20; 20/20 ELTDX exact |
| `jing_lirun` | `jinglirun` | alias 20/20; 20/20 ELTDX exact |
| `jing_zichan` | `jingzichan` | alias 20/20; 20/20 ELTDX exact |
| `jingying_xianjinliu` | `jingyingxianjinliu` | alias 20/20; 20/20 ELTDX exact |
| `liutong_guben` | `liutongguben` | alias 20/20; 20/20 ELTDX exact |
| `meigujing_zichan` | `meigujingzichan` | alias 20/20; 20/20 ELTDX exact |
| `shuihou_lirun` | `shuihoulirun` | alias 20/20; 20/20 ELTDX exact |
| `touzi_shouyu` | `touzishouyu` | alias 20/20; 20/20 ELTDX exact |
| `wuxing_zichan` | `wuxingzichan` | alias 20/20; 20/20 ELTDX exact |
| `yingshou_zhangkuan` | `yingshouzhangkuan` | alias 20/20; 20/20 ELTDX exact |
| `zhigong_gu` | `zhigonggu` | alias 20/20; no ELTDX counterpart |
| `zong_guben` | `zongguben` | alias 20/20; 20/20 ELTDX exact |

逐股票/逐字段解析值、对应 ELTDX 原始槽位、更新时间和 record hash 见[300 行 CSV](../research/20261121_tdx_finance_alias_batch_samples.csv)，规范 LF SHA-256：`182507737347e4599ede2b0c44c7d6a95875a6b69165ea17d927933302b67a6a`。`zhigong_gu` 在 ELTDX v3.3.2 `_FIN_MAP` 中没有同名字段，因此只认定解析器别名等值；其语义来自已验证的 `zhigonggu` 锚，不冒称存在 ELTDX 独立配对。

### 职工股输出单位勘误

`GetFinanceInfoCmd.parse_response()` 将 `zhigong_gu` 原始浮点值乘 `10,000` 后交给 `FinanceInfo`；项目兼容器不再换算。模型类注释的“股本（万股）”描述与解析器实际返回值冲突。注册表的单位定义是当前兼容输出口径，因此将 `TDX(双命名源)::zhigonggu` 从“万股”更正为“股”；原始协议字段及旧样本不改写。举例，600519 同记录解析输出 `zhigong_gu=515299.98779296875` 股。这个裁决只说当前 Easy-TDX 兜底返回单位，不外推到未映射该字段的 ELTDX 路径。

## 历史清单 token 冲突修复

`2.6 与 Gemini 核实字段清单的逐项对照` 将多个完整字段名拼接成一个复核清单 token；该 token 被旧 registry 解析成五个字段的 competing `canonical`，但它并不是这些字段的第二种语义。逐路径审计已将该完整 token 识别为 `not_field_schema_token`。本批先对 `changqifuzhai`、`jingzichan`、`jingyingxianjinliu`、`meigujingzichan`、`yingshouzhangkuan` 精确记录并清除此历史冲突，再应用兼容别名裁决。释义、单位、verified 状态及原始 reference evidence 均保留；每条裁决保留被清理的冲突快照。

审计定位和原始 token 见[路径 provenance 表](../research/20261121_tdx_bare_path_provenance.csv)，规范 LF SHA-256：`227c47472177d9902e362dd56602410cf423e0d7206b360cda266d5427896c57`。

## `reserve2` 与 `baoliu2`

Easy-TDX 的 `FinanceInfo.reserve2` 明确注释为“原 baoliu2”；同一批 20 个 `record_hex` 中，解析器 `reserve2`、ELTDX 原始 `bao_liu_2_raw_float` 和归一后的 `finance_info.baoliu2` 三列均逐条相等，20/20 无差异。逐股记录见[样本 CSV](../research/20261121_tdx_reserve2_baoliu2_samples.csv)，规范 LF SHA-256：`4f99655050105ec0e4584dac8d5f27839de9295fa50a7096300ddc211b0588b1`。

`baoliu2` 已有的 17 个保留采集目录、340 条观测及三家发行人半年报/三季报核验，只确认值 6/9 分别对应 6 月/9 月报告期末月份。`reserve2` 继承这一已裁定的精确来源内语义；不推断其他月份/年份，不把它当作公告日或来源数据日，不新增跨源映射。

## 来源版本和复核边界

- Easy-TDX 精确代码：[`GetFinanceInfoCmd.parse_response()`](https://github.com/yanwei99521/easy-tdx/blob/41e56376fafa3abae0f6538f271eafd6af26d27f/src/easy_tdx/commands/finance_info.py) 与 [`FinanceInfo`](https://github.com/yanwei99521/easy-tdx/blob/41e56376fafa3abae0f6538f271eafd6af26d27f/src/easy_tdx/models/finance.py)。
- 项目别名代码：[`_EasyTdxAdapter.finance()`](https://github.com/tsy1102/a-stock-data/blob/f670b70/core/tdx_client.py#L407-L425)，对应仓库提交 `f670b70`。
- 输入保留样本：`data_date=20261110`；原始文件 SHA-256：`raw_eltdx.json=6952797ab5f73c4915989ed2c1a5a4abf49336b8064f488b182d6fea947cddf6`、`raw_tdx.json=99a8668ef019883a99c9800956630c0c04931ef416e5cf30a8afd9de9e98fd99`。
- Easy-TDX 与 ELTDX 解码同一 0x0010 槽位，属于同源适配器对照；不计作独立来源证据。
- 本批没有采集新数据；未使用保留边界前样本。日频/公开网页仍可用于后续独立语义核验。
