# ELTDX 0x0010 财务元数据字段契约核验（2026-11-09）

## 定案范围

本批仅核验 `TDX-eltdx(适配层)` 的 5 个精确路径：

- `updated_date`
- `ipo_date`
- `province_raw`
- `industry_raw`
- `record_hex`

运行路径为 `scripts/capture_tcp_collectors.py::collect_eltdx` → `client.corporate.finance_batch(codes, include_raw=True)` → `_jfy` 序列化 → `raw_eltdx.json` 的 `stocks.<code>.finance_batch[0]`。`requirements.txt` 固定 `eltdx==3.3.2`。本批确认 ELTDX 适配层的公开模型路径，不建立 TDX、ZHB 或其他来源的跨源映射。

## 来源契约

ELTDX v3.3.2 的 `FinanceRecord` 字段表和 0x0010 方法手册明确给出以下定义：

| 完整路径 | 定案含义 | 单位/表示 | 边界 |
|---|---|---|---|
| `updated_date` | 财务数据更新日期 | 日期字符串；保留样本格式为 `YYYY-MM-DD` | 不等同于财报公告日期或报告期 |
| `ipo_date` | 上市日期 | 日期字符串；保留样本格式为 `YYYY-MM-DD` | 只确认日期含义，不扩展到其他上市状态日期 |
| `province_raw` | 地区（省份）原始编号 | 无物理单位 | 不推断编号对应的省份名称或编码版本 |
| `industry_raw` | 行业原始编号 | 无物理单位 | 不推断编号对应的行业名称或分类版本 |
| `record_hex` | 单条 0x0010 财务记录的原始十六进制 | 十六进制字符串 | 协议审计数据，不是业务指标 |

接口字段到项目路径的映射由上述采集调用链逐字段保持；文档没有定义的编号表和值域未作猜测。`include_raw=True` 保留 `record_hex`。

- [ELTDX v3.3.2 FinanceRecord 字段手册](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/FIELD_REFERENCE.md#financerecord)
- [ELTDX v3.3.2 `finance_batch` 方法手册](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/METHOD_REFERENCE.md#财务基础信息)
- [通达信量化平台专业财务数据接口](https://help.tdx.com.cn/quant/docs/markdown/TdxQuant.md/mindoc-1h10m001ic888.html)：另行定义 `announce_time`（公告日期）和 `tag_time`（报告期）；本批不将它们映射到 `updated_date`。

## 保留样本核对

核对 `docs/field_verification/20261105/raw_eltdx.json` 和 `20261106/raw_eltdx.json`。每个采集日均有 20 条财务记录，5 个目标字段分别在 20/20 条记录中存在。日期样本如 600309 `updated_date=2026-10-26`、`ipo_date=2001-01-05`；`province_raw`、`industry_raw` 为原始整数编号；每条 `record_hex` 样本为 286 个十六进制字符。两日重复值用于确认序列化稳定性，不作为额外的语义定义。

## 实现更正与影响

上游将 `updated_date` 定义为财务数据更新日期；项目 `tdx_get_finance_info` 注释曾误称其为“财报披露日”并提及事件驱动 TTL。本批更正该注释，避免把更新标记当作公告日、报告期或 TTL 事件信号。

另发现股东人数 TDX 回退路径把 `updated_date` 强制转换为整数，因此无法处理 ELTDX 当前输出的 `YYYY-MM-DD` 字符串。本批增加严格支持 `YYYY-MM-DD` 与既有 `YYYYMMDD` 两种输入的日期解析；无效日期不写入历史记录。记录仍使用既有 ISO `date` 字段，SQLite key、TTL 和记录结构不变。

```text
TDX::updated_date (finance_info) = 财务数据更新日期
TDX-eltdx::updated_date (finance_batch) = 财务数据更新日期
```

上面只是两条各自的来源内定义摘要，不表示已登记跨源映射；本批 registry 裁决只应用于 `TDX-eltdx(适配层)`。
