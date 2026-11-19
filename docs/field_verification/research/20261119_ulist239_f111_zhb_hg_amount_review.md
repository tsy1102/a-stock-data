# Ulist `f111` 与 ZHB `hg_amount_yi` 相关候选复核

复核日期：2026-11-19。目标路径：`东财-ulist239(np/get)::f111`；候选对照路径：`ZHB-tipinfo::hg_amount_yi`。

## 数据日期与候选身份

- 本次本机时钟显示北京时间 2026-11-19 19:49，设备已过收盘；运行卡默认数据日是 2026-11-19。Ulist 采集重跑时因本地 `ip_banned` 熔断而 `attempts=0`，没有新增 Ulist 样本。本复核明确使用已有 2026-11-17、2026-11-18 样本，不把本次运行日当成它们的数据日。
- 审阅依据报告（审阅前版本）：`20261119/20261119_collision_report.json`，schema 5、完整性 `complete`，报告 SHA-256 `56b64ac09412f9108dcec9d6cfc039b84c7f686fd3ff273fecac596789368e75`。写入审阅后，以相同数据重新生成报告，SHA-256 为 `c1bbbfb1720a42e2f3e424b4d2ad4c3923ad870055fca98da7a5d7cf2718a066`，完整性仍为 `complete`，该候选显示 `rejected`。
- 候选 ID：`cc1_cd2a299866852a9f3a2cad0a7f5f470b206afcfa9e95fddb77dfd40a1d3fc80f`。方法为 `robust_correlation`，报告给出 Pearson `0.5513`、Spearman `0.8783`、12 行、数据日 2026-11-17 与 2026-11-18。
- Ulist `f297` 已由来源内实证确认为逐证券行情数据日（`adjudications/20261114_ulist239_f297_empirical_semantics_evidence.md`）；CSV 同时保存每行 `f297`。ZHB 数据日按压缩包文件名确认：[`zhb_20261117.zip`](../../../cache/zhb/zhb_20261117.zip) 与 [`zhb_20261118.zip`](../../../cache/zhb/zhb_20261118.zip)；raw 中日期副本不替代文件名。
- 原始来源文件的规范 LF SHA-256：
  - `20261117/raw_ulist239.json`: `fb52140dd18d2c010f1ea85299762534c55804e54568ca8b2dc26852bd0ffffd`
  - `20261117/raw_zhb.json`: `be437783ffae98a9e3b3bd7259676263d02e5e2d310f600776298cc132fa1f41`
  - `20261118/raw_ulist239.json`: `c8ac75aaf6f3a1cb926089555f490ff5f3ecc09151188e0619993d7e872a611c`
  - `20261118/raw_zhb.json`: `77f46ce79cd502634c6fcfbcc1b2a3d7cdbc931de14539a526ac8a5333432072`

## 逐行结果与解释

完整 12 行见 [逐股样本 CSV](20261119_ulist239_f111_zhb_hg_amount_samples.csv)。这 12 行并非 12 个独立的跨日变化样本：只有 6 只证券，且每只证券在两个数据日的 `f111` 与 `hg_amount_yi` 均各自保持完全相同。也就是说，这个候选没有任何逐股时间变化信息；相关系数完全来自 6 只证券之间的截面排序，不能据此把两个字段解释为等价或由一个字段推算另一个字段。

在这 12 行中，`f111` 只观察到 `131072`、`524288` 两个值；`hg_amount_yi` 则为 `0.2`、`0.6`、`1`、`2`、`5`、`30`。没有逐值相等，样本也没有给出稳定单位换算。数值差异本身不能揭示 `f111` 的正式含义；目前没有 Eastmoney 官方资料把精确路径 `ulist.np/get::f111` 对应到一个中文字段定义。

## 结论边界

将这一个 `f111`—`hg_amount_yi` 相关候选标为 `rejected`：否定它作为字段等价/释义关系的证据价值。**不**据此认定 `f111` 的字段语义、不推断其是否为位标记、不否定未来出现的新候选；精确路径 `东财-ulist239(np/get)::f111` 仍为 `unverified`，主字典、registry 与 `mappings` 均不变。若后续取得官方键值定义或新的逐股变化样本，应以新报告和新证据重新评估。
