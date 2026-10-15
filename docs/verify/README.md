# `docs/verify/` 字段实测附录

本目录保存按来源整理的字段契约、实测样本和交叉核验资料。逐源字段身份、完整路径与状态以 [`field_registry.json`](../field_verification/field_registry.json) 为准；主字典 [`field_dict.md`](../field_dict.md) 是生成的治理入口，本 README 是本目录当前附录的导航。各附录中的接口数、字段数和样本数是对应研究时的快照，不代表当前可用接口或采集状态。

## 附录索引

| 来源 / 主题 | 资料 |
|:---|:---|
| 东财 Push2 / Ulist | [push2_verify.md](push2_verify.md)、[ulist_verify.md](ulist_verify.md)、[ulist_push2_align.md](ulist_push2_align.md) |
| 腾讯 | [tencent_verify.md](tencent_verify.md) |
| 同花顺 | [thsdk_field_verify.md](thsdk_field_verify.md)、[ths_tableheader_ids.md](ths_tableheader_ids.md) |
| 通达信 / ZHB | [tdx_func_fields.md](tdx_func_fields.md)、[tdx_headers_definition.md](tdx_headers_definition.md)、[tdxhy_x_names.md](tdxhy_x_names.md)、[zhb_verify.md](zhb_verify.md) |
| Fuyao | [fuyao_api_full.md](fuyao_api_full.md)、[fuyao_website_anchor.md](fuyao_website_anchor.md) |
| AxData | [axdata_verify.md](axdata_verify.md) |
| FTShare | [ftshare_fields_mirror.md](ftshare_fields_mirror.md) |
| levistock | [levistock_field_verify.md](levistock_field_verify.md) |
| eltdx | [eltdx_verify.md](eltdx_verify.md) |
| KPH / KPL | [kph_kpl_history_verify.md](kph_kpl_history_verify.md) |
| 跨源与样本 | [cross_source_align.md](cross_source_align.md)、[client_fields_enum.md](client_fields_enum.md)、[samples_verify.md](samples_verify.md) |
| 东方财富官网锚点 | [eastmoney_website_anchor.md](eastmoney_website_anchor.md)、[em_indicators.md](em_indicators.md)、[em_tableheader_ids.md](em_tableheader_ids.md) |
| 网络 | [network_servers.md](network_servers.md) |

## 子目录

- [`data/`](data/) — 附录使用的 JSON 配置、连接探测与历史复测数据。

## 维护约定

- 新增实测或破解资料时，按来源或主题落入本目录，并更新本索引及 [`docs/README.md`](../README.md)。
- 字段状态、来源身份或完整代码路径变化时，同步维护 `field_registry.json` 并运行项目注册表一致性检查；不要把附录中的历史数量直接写成当前接口状态。
- 原始样本和详细推理留在证据文件；主字典只收录经过审定的字段结论及必要引用。
