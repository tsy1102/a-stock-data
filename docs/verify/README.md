# docs/verify/ — 字段实测附录(实证层)

> 本目录是主字典 `field_dict.md` 的**附录(实证层)**: 存放各数据源的实测字段破解全表 / 原始证据 / 样本矩阵。主字典引用处有链接, 查询未知字段先查主字典 → 按其 §12.15.9 附录索引按源查本目录。
> 父目录总览见 [`../README.md`](../README.md)。

## 按数据源分组的附录

| 源 | 文件 |
|:---|:---|
| push2 | `push2_verify.md`(114 字段破解全表) · `ulist_push2_align.md`(ulist↔push2 162 字段同值对齐) |
| 腾讯 | `tencent_verify.md`(88 字段复核 + 未知位矩阵) |
| 同花顺 | `thsdk_field_verify.md`(THS SDK 395 ID) · `ths_tableheader_ids.md`(tableheader 列 ID) |
| 通达信 | `tdx_func_fields.md`(字段总表 1924) · `tdx_headers_definition.md`(表头定义) · `tdxhy_x_names.md`(细分行业 X 码 470) |
| fuyao | `fuyao_api_full.md`(REST 全量字段契约 62 端点) |
| AxData | `axdata_verify.md`(666 字段补齐矩阵) |
| FTShare | `ftshare_fields_mirror.md`(85 工具×响应字段镜像) |
| levistock | `levistock_field_verify.md`(26/38 接口实测) |
| eltdx | `eltdx_verify.md`(本地 TDX 适配层字段) |
| 跨源 | `cross_source_align.md`(跨源对齐) · `client_fields_enum.md`(客户端字段枚举全景) |
| 网络 | `network_servers.md`(三源服务器清单 + 移动线路) |
| 东财 | `em_indicators.md`(939 指标代码) · `em_tableheader_ids.md`(表头字段 ID) |
| 样本 | `samples_verify.md`(24 股样本核实矩阵 + 未知字段破解数据) |
| 官网锚点 | `eastmoney_website_anchor.md` · `fuyao_website_anchor.md`(官网字段定义锚点) |

## 子目录

- `data/` — 附录数据文件(JSON): `tdx_connect_cfg.json` / `ths_dns_cache_*.json` / `tdx_full_retest_*.json` 等。

## 维护约定

- 新增破解/实测数据 → 写对应源附录(不膨胀主字典), 主字典加摘要+链接。
- 新增附录必须在主字典 §12.15.9 登记。
- 数据文件(JSON)统一放 `data/`。
