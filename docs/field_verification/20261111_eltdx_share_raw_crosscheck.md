# ELTDX 股份字段与原始财务主体核验（2026-11-11）

## 候选先行与字段范围

先拆解名字，再检查契约和样本：

| 完整路径 | 拼音/英文名称候选 | 单源结论 |
|---|---|---|
| `b_gu_raw_float` | `b_gu` = B 股；B-share count；`raw_float` 是浮点表示 | B 股原始股数，万股 |
| `h_gu_raw_float` | `h_gu` = H 股；H-share count；`raw_float` 是浮点表示 | H 股原始股数，万股 |
| `finance_info_raw` | financial information raw payload | 0x0010 财务主体原始字节块，JSON 中用十六进制字符串表示 |

## 来源契约和本地采集路径

- 项目固定 `eltdx==3.3.2`。采集路径为 `scripts/capture_tcp_collectors.py::collect_eltdx` → `client.corporate.finance_batch(codes, include_raw=True)` → `raw_eltdx.json` 中 `stocks.<code>.finance_batch[0]`。
- ELTDX v3.3.2 [财务基础信息文档](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/methods/7709-%E8%B4%A2%E5%8A%A1%E5%9F%BA%E7%A1%80%E4%BF%A1%E6%81%AF.md#L253-L329)直接将 `b_gu_raw_float`、`h_gu_raw_float` 标为 B 股、H 股原始值，单位均为万股；`finance_info_raw` 定义为 136 字节财务主体原始数据。单位文档还说明股本原始值以万股计、实际股数为 raw × 10,000。
- 对应 [0x0010 协议解析器](https://github.com/electkismet/eltdx/blob/v3.3.2/crates/eltdx-protocol/src/commands/corporate.rs#L430-L509)把 FinanceRecord 的 B/H 股字段直接解码为 `f32`；财务记录为 143 字节，`record[7..143]` 是 136 字节主体。
- 项目 JSON 转换把 `bytes` 写成十六进制。检查 2026-11-10 保留样本中 20/20 条 ELTDX 记录：`finance_info_raw` 解码后均为 136 字节，`record_hex` 均为 143 字节，且 `record_hex` 去掉 7 字节股票头后与 `finance_info_raw` 完全相同。

## 发行人股份数据交叉核对

- **B 股样本：**2026-11-10 原始采集中的 `000011` 源更新日为 2026-10-30，`b_gu_raw_float=6760.52001953125` 万股。深物业 A/B 的 [2026 年半年度报告](https://static.cninfo.com.cn/finalpage/2026-08-29/1225524518.PDF)以“单位：股”列示截至 2026-06-30 境内上市外资股 67,605,243 股，折合 6,760.5243 万股；raw 差约 43 股。报告期与源更新日不同，数值只作为近似交叉佐证，不能声称精确相等。
- **H 股样本：**同批 `601288` 源更新日为 2026-10-31，`h_gu_raw_float=3073882.25` 万股。农业银行截至 2026-10-31 的 [H 股月报公告](https://www.abchina.com.cn/zt/AboutABC/investor_relations/announcements/h-announcement/)由官网列示于 2026-11-05；可检索的[公告文本副本](https://www.cfi.net.cn/p20261105001430.html)列示 30,738,823,096 股，raw × 10,000 与其差 596 股。该差额小于这一数值量级下 `f32` 的半个量化步长；这是精度解释，不是精确命中，也不改变 H 股名称候选。

## 裁决边界

- 三项按 `TDX-eltdx(适配层)` 的完整来源路径分别记录为 `verified_by_source_contract`。来源文档直接定义这三个单源含义；样本和公开报告只作相符性核验。
- 没有把来源裁决扩展为 TDX 其他解析路径、ZHB 或东财字段映射，也没有推断 136 字节财务主体内部未登记槽位的含义。
- 原始数值只保留原值和差额；数值近似不能覆盖拼音/英文候选。采集目录日期为 2026-11-10，`updated_date` 是来源记录日期，不能混为同一个数据日期。
