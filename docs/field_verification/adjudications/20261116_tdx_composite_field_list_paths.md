# TDX 0x0010 斜杠清单不是单一字段路径

裁决日期：2026-11-16

精确身份：

- `TDX(双命名源)::gudongrenshu/zongzichan/liudongfuzhai/changqifuzhai/jingzichan/zhuyingshouru/jinglirun/jingyingxianjinliu/ipo_date/liutongguben/zongguben/meigujingzichan/cunhuo/yingshouzhangkuan/zibengongjijin/weifenpeilirun/updated_date/province/industry`
- `TDX(双命名源)::market/code/guojiagu/faqirenfarengu/farengu/bgu/hgu/zhigonggu/liudongzichan/gudingzichan/wuxingzichan/zhuyinglirun/yingyelirun/touzishouyu/zongxianjinliu/lirunzonghe/shuihoulirun/baoliu2`

## 结论

这两条注册身份是历史文档把字段清单写成斜杠分隔一格后留下的伪路径，不是 TDX 响应字段。两组分别包含 19 和 18 个独立代码，共 37 项；每个分项已有各自的 `TDX(双命名源)` 注册身份。两条合并字符串标为 `disproved / not_field_schema_token`，成员字段的语义与状态不变，也不创建跨源映射。

## 证据

1. [`field_source_reference.md` §2.1、§2.6](../../field_source_reference.md) 的逆向解析表逐行列出偏移 `0` 至 `36`，因此是 37 个槽位。旧比较表第一组实际含 19 个代码、第二组含 18 个；两组没有重复，恰好覆盖 37 个代码。它们是清单分组，不是一个 API code path。该资料明确说明 0x0010 布局来自解析器逆向，并非通达信官方字段字典。
2. [`tdx_get_finance_info()`](../../../core/tdx_client.py) 的接口注释也声明返回 37 个字段。当前 TDX raw 的财务字段位于 `stocks.<symbol>.finance_info` 对象；其中每个字段以单独键序列化。ELTDX FinanceRecord 则位于 `stocks.<symbol>.finance_batch[]`，其路径和别名另按完整身份登记。
3. [`审计 CSV`](../research/20261116_tdx_composite_field_list_audit.csv) 扫描了保留边界 `2026-10-15` 之后、目录名与 `meta.data_date` 一致的 19 份 `raw_tdx.json`，共检查 380 个 `finance_info` 对象。两个合并字符串作为 JSON 对象键的出现数均为 0；每行保留 raw/meta SHA-256。此处只用响应结构证明路径身份，不把目录日期当作 TDX 来源实际日期，也不比较业务数值。
4. [`field_registry.json`](../field_registry.json) 中的 37 个分项均有独立的 `TDX(双命名源)` 注册身份且状态为 `verified`。合并字符串原先只有空含义和 `registry_status_only_single_source`，没有逐字段参考证据；它们也不在当前 [`registered_field_sets()`](../../../scripts/audit_field_completeness.py) 得到的 TDX 原生字段基线中，亦不是来源字段补录。

## 同步修改

- 将两条伪路径标记为 `disproved / not_field_schema_token`，保留审计记录并从默认破解目标退出。
- 在历史字段清单旁明确斜杠表示列表分隔符，纠正“36 槽位”和“Gemini 18 项”计数错误，避免再次把整串当成完整来源路径。
- 修正历史清单表格的列结构，并将被误当作 canonical 的“历史清单未列出的其余 18 项”分组标签从字段矩阵过滤；37 个分项仍由偏移表和逐字段注册身份表示。
- 将未知字段视图中的该状态说明改为“非字段标记或清单”，同时适用于日期/类型格式标记和误登记的字段清单。

本裁决不改变任何单项字段释义、单位、来源路由、采集行为或日期资格。
