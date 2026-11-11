# ELTDX 特殊品种涨跌停价格字段裁决

日期：2026-11-10<br>
裁决方式：固定版本来源契约核验；未读取采集样本。

## 裁决

| 来源身份 | 字段路径 | 确认含义 | 单位 | 处理 |
|---|---|---|---|---|
| `TDX-eltdx(适配层)` | `limit_up_price` | 涨停价 | 未公开，留空 | 已由来源契约确认 |
| `TDX-eltdx(适配层)` | `limit_down_price` | 跌停价 | 未公开，留空 | 已由来源契约确认 |

两条路径先前共用 `limit_up_price / limit_down_price` 与 `涨停价 / 跌停价` 的混合候选文本。ELTDX 3.3.2 的独立属性定义消除了该合并歧义，因此分别改为精确规范名和含义。没有证据支持价格单位，故不填单位。

## 证据与边界

- 项目锁定的 ELTDX 3.3.2 文档将 `client.limits.special(...)` / `client.limits.scan_special(...)` 说明为 7709 `0x0452` 特殊品种涨跌停限制表；`SpecialLimitRecord` 分别暴露 `limit_up_price` 与 `limit_down_price`。[METHOD_REFERENCE.md v3.3.2](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/METHOD_REFERENCE.md)
- 同版本字段手册分别定义 `SpecialLimitRecord.limit_up_price` 为涨停价、`limit_down_price` 为跌停价。[FIELD_REFERENCE.md v3.3.2](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/FIELD_REFERENCE.md)
- 本机安装的 ELTDX 3.3.2 模型实现显示，两个属性分别读取 `upper_price_raw_f32`、`lower_price_raw_f32`。该实现核对仅用于确认属性对应关系，不推断元、分或其他单位。
- 涨跌停价格是随证券和交易状态变化的数值；本次只确认字段角色，不把未带可核来源数据日的样本用于碰撞或定案，也不建立与其他来源的数值映射。
- 这两个接口当前没有项目采集调用点；本裁决不新增采集路由、缓存行为或运行时数据使用。
