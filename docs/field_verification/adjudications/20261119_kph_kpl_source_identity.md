# KPH（开盘红）与 KPL（开盘啦）来源身份核查

核查日期：2026-11-19。

## 结论

项目中的 KPH 与 KPL 是两个独立的数据源身份，按各自产品、官网和 API 主机分别采集、登记和碰撞。字段样本相等只能用于具体字段关系判断，不能据此合并来源或采集路线。

| 项目身份 | 产品 | 官网 | 本项目接口主机 | 运行别名 |
|---|---|---|---|---|
| KPH | 开盘红 | <https://www.kaipanhong.com/> | `apphis.kaipanhong.com` | `kph` |
| KPL | 开盘啦 | <https://www.kaipanla.com/> | `apphis.longhuvip.com` | `kpl` |

两个官网分别以“开盘红”和“开盘啦”作为产品名称。两站页脚都列出深圳开盘啦网络科技有限公司；这说明运营主体相同，但不改变项目中两个不同产品/API 服务的来源身份，也不构成字段等价证据。

## 项目路径核对

- `stock_common/sc_datasource/_kph.py` 的 `KPH_HISTORY_URL` 指向 `https://apphis.kaipanhong.com/w1/api/index.php`，KPH 使用 `get_kph_limit_up_history` 独立分页适配器和 `kph` 来源族。
- `stock_common/sc_kpl.py` 的历史主机配置指向 `https://apphis.longhuvip.com/w1/api/index.php`；专用涨停明细以 `开盘啦(kpl_limit_up_detail) → kpl` 登记。
- `开盘啦(kpl)` 是历史字段标签，当前只映射到聚合容器 `market_sources`。该容器不代表专用 KPL API，也不得据标签把聚合数据归并到 KPH 或 KPL。
- `docs/field_verification/source_lineage.json` 中 KPH/KPL 来源族分别是 `kph` 与 `kpl`；逐字段比对继续要求同股、同交易日、同路径，不能用来源总值相似率推断同源。
- KPH/KPL 的逐字段对照只作为被动证据；即使连续样本完全相等，也不得据此将 KPH 标记为可停采路线或从碰撞中屏蔽。采集身份闸门对 KPH 明确关闭冗余抑制，两个来源独立采集。

## 既有样本边界

2026-11-16 至 2026-11-18 的 KPH/KPL 103 组日期对齐观测中，83 组相等、20 组不同。该结果支持拒绝“所有共同字段都逐值等价”，但来源身份区分本身依据的是两款产品、官网和项目接口路由，而非相等率。具体字段映射仍须逐字段保留独立证据；不得因相等样本减少任一路线。

## 可复核来源

- [开盘红官网](https://www.kaipanhong.com/)：首页展示“开盘红”品牌，页脚列出运营公司。
- [开盘啦官网](https://www.kaipanla.com/)：首页展示“开盘啦”品牌，页脚列出运营公司。
- [本项目 KPH 适配器](../../../stock_common/sc_datasource/_kph.py) 与 [KPL 适配器](../../../stock_common/sc_kpl.py)：分别核实采集端点主机。
- 逐日字段对撞细节见 [`../research/20261119_kph_industry_limit_up_count_followup.md`](../research/20261119_kph_industry_limit_up_count_followup.md)。
