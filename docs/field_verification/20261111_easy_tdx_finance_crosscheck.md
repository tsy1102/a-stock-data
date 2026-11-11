# Easy-TDX 财务兜底路径核查（2026-11-11）

## 范围与来源链

本批核查 `TDX(双命名源)` 下 Easy-TDX 兜底适配器暴露的精确下划线路径。字段身份仍按 `(source, 完整 code path)` 记录；本批 source-contract 只说明 Easy-TDX 1.20.8 的模型/解析器如何命名和换算这些输出，不建立其与其他 TDX、ELTDX、ZHB 或通达信其他接口之间的 `mappings`。

- `requirements.txt` 固定使用 `vendor/easy_tdx-1.20.8-py3-none-any.whl`。项目 `core/tdx_client.py::_get_verified_adapter()` 先尝试 ELTDX，只有它不可用时才使用 `_create_easy_tdx_adapter()`。
- Easy-TDX 的 `GetFinanceInfoCmd.parse_response()` 将协议槽位赋给 `FinanceInfo` 字段；`FinanceInfo` dataclass 转为 DataFrame 列。项目 `_EasyTdxAdapter.finance()` 保留这些原始下划线列，并为每个带下划线键生成去下划线副本。
- `scripts/capture_tcp_collectors.py::collect_tdx()` 经 `tdx_get_finance_info()` 保存 TDX 财务结果。对保留期 2026-10-15 至 2026-11-10 的 17 份 `raw_tdx.json` 逐一检查后，没有一份含本批下划线路径；这些采集日的 TDX 主适配器走 ELTDX，保存的是紧凑路径。缺少下划线值是当前采集路由的结果，不作为字段语义反证，也不把紧凑字段样本冒充本路径样本。
- 上游字段模型与解码实现：[Easy-TDX FinanceInfo 模型](https://github.com/yanwei99521/easy-tdx/blob/main/src/easy_tdx/models/finance.py)、[GetFinanceInfo 解码器](https://github.com/yanwei99521/easy-tdx/blob/main/src/easy_tdx/commands/finance_info.py)。项目使用的 wheel 版本是 1.20.8。
- 通达信官方 [公式函数表](https://help.tdx.com.cn/gspt/docs/markdown/redword/functionlist.html)列出 `FINANCE(8)` 股东人数（户）、`FINANCE(23)` 营业利润；官方 [证券基本信息接口](https://help.tdx.com.cn/quant/docs/markdown/mindoc-1ctuhthaq5qmg/mindoc-1h10jj7r7jol4.html)列有 `J_gdrs`、`J_yysy`、`J_zxjl`。这些是不同接口，只作术语或单位佐证，不建立 0x0010 路径码映射。

## 本批确认的精确路径

| 精确路径 | 拼音拆词 / 英文候选 | source-contract 释义 | 单位 | 边界 |
|---|---|---|---|---|
| `gudong_renshu` | gu dong ren shu / shareholder count | 股东人数 | 户 | 上游模型明确命名；通达信官方 `FINANCE(8)` 明确单位为户。不是通过 `gudongrenshu` 的同族值建立映射。 |
| `zhuying_shouru` | zhu ying shou ru / main-business revenue | 主营收入 | 元 | 上游模型列于“利润指标（元）”并以同名字段输出。官方另一接口使用“营业收入”名称，只作业务术语佐证；不宣称两个接口逐值等价。 |
| `zong_xianjinliu` | zong xian jin liu / total cash flow | 总现金流 | 元 | 上游模型列于“利润与现金流指标（元）”。官方另一接口 `J_zxjl` 名为“总现金净流量”，仅作类别佐证，不据此推断字段口径或映射。 |

这三条已按正式 source-contract 流程登记。注册表保留精确键名与模型释义；不修改碰撞规则、采集优先级、数据日期或现金流计算方法。

## 保留为未验证的相邻候选

- `zhuying_lirun` 按拼音及 Easy-TDX 模型注释候选为“主营利润 / main-business profit”，模型把数值列入元单位的利润指标；但目前没有找到通达信官方资料对这一精确指标的定义，也没有该下划线路径的保留原始样本可与发行人报表核对。本轮不据个人维护库的注释单独更新主字典。
- `zhuyinglyrun` 是 ELTDX→TDX 兼容输出路径中的紧凑拼写；它不同于 Easy-TDX 的 `zhuying_lirun`（按规则去下划线应为 `zhuyinglirun`）。不得因为两者外观相近而合并，也不在本批确认其业务含义。
- 本批不涉及 `fa_qi_ren_fa_ren_gu_raw_float` 与 `fa_ren_gu_raw_float` 的数值冲突。它们的拼音候选仍分别是“发起人法人股 / promoter legal-person shares”和“法人股 / legal-person shares”；数值冲突仍作为独立证据层调查。

## 决定及验证范围

- 登记 3 个 Easy-TDX 下划线 source path；没有新增跨源映射。
- `zhuying_lirun`、`zhuyinglyrun`、`fajirenfarengu` 及前述两条股本字段维持现有未定状态；不从 Easy-TDX 字段邻近排列推断语义。
- 修改仅涉及 source-field 元数据、裁决记录及生成视图；不改运行代码和金融缓存契约。source-contract parity 期望已同步更新。
- 验证通过：`tests/test_registry_parity.py` 20/20；完整离线验收 1507 passed、1 skipped、52 deselected、12 subtests passed。语法检查 293 个文件通过，Mypy 271 个源码文件无错误，Black 检查 276 个文件通过；AxData 摘要、数据访问、同步检查、规范契约及注册表 parity 闸门均通过。
