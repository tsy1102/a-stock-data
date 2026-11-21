# 财联社 `level` 类别代码单位补充核验

复核日期：2026-11-21。

## 裁决

将 `财联社(cls)::level` 的 registry `unit` 补为“代码”。这只标注字段值是离散代码，不定义完整枚举、等级名称、排序或分类规则。先前的官方来源契约裁决仍是字段网页展示含义的依据；本次仅补齐单位/类型元数据，旧契约裁决与字段规范名保持不变。

## 证据与样本范围

- 字段路径由 `stock_common/sc_datasource/_eastmoney.py::cls_telegraph()` 映射到财联社 `/v1/roll/get_roll_list` 响应 `data.roll_data[*].level`，并原样保存于 `raw_cls.json`。财联社官方前端将该值作为展示分支代码读取；前次来源契约记录及官方脚本链接见 [`20261121_cls_level_source_contract.md`](20261121_cls_level_source_contract.md)。
- 本次只读取 `scripts/capture_retention.py` 允许的保留期内现存原始归档，不发起采集。22 个原始文件中 2026-10-15 文件为空；其余 21 个日期共 1,050 条记录，1,050 条均为非空字符串。取值为 `A=2`、`B=122`、`C=926`，没有缺失、非字符串或其他观察值。
- 逐日计数、异常计数与每个原始文件 SHA-256 见[留存样本审计表](../research/20261121_cls_level_retained_audit.csv)。审计表 SHA-256：`1d0097be97c1de30dfb466b6661ac698e8b21b2e50626785d0df2b162d3b40e0`。

## 解释边界

1,050/1,050 的离散字符串观测，加上官方前端将该值用于 A/B/C 样式分支，足以将 registry 的 `unit` 标为“代码”。这不证明完整代码表，也不证明 A/B/C 的具体业务含义或重要性排序。`reports::level` 仍是不同来源路径，未合并、未映射。本次不改变采集代码或碰撞口径。
