# 2026-11-18 Ulist239 f148 官方资格位核验

## 范围和结论

- 精确字段身份：`东财-ulist239(np/get)::f148`。项目[采集器实现](../../../../scripts/capture_http_collectors.py)由 `collect_ulist239` 请求东方财富 `https://push2delay.eastmoney.com/api/qt/ulist.np/get`，并保留原始 `f148` 键；该上游响应没有提供 `f148` 的字段标签。本记录只用 2026-10-15 保留边界之后的数据；对照数据日为 2026-11-09、11-10、11-17，均为同一 20 只股票，共 60 条原始记录。最新对照日是 2026-11-17。
- 这批样本中 `f148` 对每只股票在三个数据日保持不变，观测值仅有 `1, 65, 577, 1025, 1089`，分解为 `1 + 64 + 512 + 1024` 中出现的子集。
- `bit6 (64)` 与 2026-11-17 交易所两融标的资格 20/20 匹配；`bit9 (512)` 与沪股通双向可交易名单 20/20 匹配；`bit10 (1024)` 与深股通双向可交易名单 20/20 匹配。逐股票证据见 [JSON witness](20261118_ulist239_f148_membership_witness.json)。
- `bit0 (1)` 在 20/20 样本恒为 1，无法区分它是 A 股标记、普通股票类型位还是通用基位。东方财富的公开响应展示原始键 `f148`，但未给字段标签。因此暂不更改主字典/注册表，精确路径继续保持 `unverified`。

## 最新样本逐股对照

| 证券 | f148 | bit6 两融 | bit9 沪股通 | bit10 深股通 | 两融名单/规则依据 |
|:--|--:|--:|--:|--:|:--|
| `000007` | 1 (`0x1`) | 0 | 0 | 0 | not in active SZSE list |
| `000011` | 1025 (`0x401`) | 0 | 0 | 1 | not in active SZSE list |
| `000037` | 1 (`0x1`) | 0 | 0 | 0 | not in active SZSE list |
| `000568` | 1089 (`0x441`) | 1 | 0 | 1 | SZSE Q3 2026 stock list |
| `000678` | 1089 (`0x441`) | 1 | 0 | 1 | SZSE Q3 2026 stock list |
| `002034` | 1089 (`0x441`) | 1 | 0 | 1 | SZSE Q3 2026 stock list |
| `002242` | 1089 (`0x441`) | 1 | 0 | 1 | SZSE Q3 2026 stock list |
| `300031` | 1089 (`0x441`) | 1 | 0 | 1 | SZSE Q3 2026 stock list |
| `300788` | 1025 (`0x401`) | 0 | 0 | 1 | not in active SZSE list |
| `301190` | 1089 (`0x441`) | 1 | 0 | 1 | ChiNext registration-IPO from-listing-day rule |
| `600309` | 577 (`0x241`) | 1 | 1 | 0 | SSE Q3 2026 stock list |
| `600519` | 577 (`0x241`) | 1 | 1 | 0 | SSE Q3 2026 stock list |
| `600675` | 577 (`0x241`) | 1 | 1 | 0 | SSE Q3 2026 stock list |
| `600825` | 577 (`0x241`) | 1 | 1 | 0 | SSE Q3 2026 stock list |
| `601288` | 577 (`0x241`) | 1 | 1 | 0 | SSE Q3 2026 stock list |
| `688327` | 577 (`0x241`) | 1 | 1 | 0 | STAR registration-IPO from-listing-day rule |
| `688553` | 65 (`0x41`) | 1 | 0 | 0 | STAR registration-IPO from-listing-day rule |
| `688589` | 65 (`0x41`) | 1 | 0 | 0 | STAR registration-IPO from-listing-day rule |
| `920118` | 65 (`0x41`) | 1 | 0 | 0 | BSE official target-stock query for 2026-11-17 |
| `920508` | 65 (`0x41`) | 1 | 0 | 0 | BSE official target-stock query for 2026-11-17 |

## 证据来源

- [港交所 Eligible Securities 页面](https://www.hkex.com.hk/Mutual-Market/Stock-Connect/Eligible-Stocks/View-All-Eligible-Securities?sc_lang=en)：页面标注 `Updated 17 Nov 2026`，分别列出沪股通和深股通“两边可买可卖” CSV。样本逐股比对对应 CSV，支持 bit9/bit10。
- [上交所 2026 年第三季度两融标的调整通知](https://www.sse.com.cn/lawandrules/sselawsrules2025/trade/specific/margin/c/c_20261016_10834885.shtml)：附件包含 1000 只非注册制股票，自 2026-10-19 起施行。采样的上交所主板证券逐项核对附件；科创板注册制证券按[上交所现行实施细则第二十四条](https://www.sse.com.cn/lawandrules/sselawsrules2025/trade/specific/margin/c/c_20250616_10782015.shtml)核对上市首日起可作为标的证券。
- [深交所 2026 年第三季度两融标的调整通知](https://www.szse.cn/disclosure/margin/business/t20261016_623333.html)：附件1列出 1200 只非注册制股票。采样的非注册制深市证券逐项核对附件；注册制首发股票按[深交所实施细则第三章第 3.2 条](https://docs.static.szse.cn/www/lawrules/rule/trade/W020230217568325595241.pdf)核对上市首日起可作为标的证券。
- [北交所标的股票信息页面](https://www.bse.cn/disclosure/rzrq_bdzq_list.html)：对数据日 `2026-11-17` 的官方查询中，`920118` 与 `920508` 均返回 `rzbd=Y`、`rqbd=Y`。查询结果字段及响应哈希列在 JSON witness。

## 碰撞候选处理

最新碰撞报告将 `f148` 与 Tencent `[71]`、FTShare 60 日涨跌幅、ELTDX `active1` 及 ZHB 若干涨跌幅列为相关性候选。相关系数不能把分类位掩码变成同一回报字段；本轮不建立这些跨源映射。分类值在不同交易日稳定、而回报字段按日变化，说明旧相关性来自横截面分组，不是字段身份。

## 尚缺证据

要完整定案该精确路径，还需查明恒为 1 的 bit0：取得东方财富的 `f148` 字段标签，或取得同一 Ulist 接口下非 A 股/ETF/指数等负对照并用相应官方证券分类资料区分解释。现有样本不能证明 bit0 的业务含义；不把它擅自命名为“A股标记”。

历史 2026-09-23 报告曾把 f148 记为已定案位掩码；但当前逐源注册表的 `东财-ulist239(np/get)::f148` 仍为 `unverified`。本记录不复用保留边界前的原始样本，也不把旧报告视作当前注册表裁决。
