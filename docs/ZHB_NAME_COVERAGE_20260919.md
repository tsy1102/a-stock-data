# ZHB 个股名离线覆盖率提升（降网主线）— 2026-09-19 (V17.3.2)

数据来源：通达信 ZHB 数据包 `zhb_20260918.zip`（8055 只全市场快照，含 5831 只纯 A 股）。
结论均不构成投资建议。

## 一、背景与问题
`get_canonical_stock_data` 的 name 解析优先级（`data_provider.py:700-707`）为：
`实时行情名 > zhb_dict > zhb_name > get_stock_name_from_zhb(unified_name_map)`。
ZHB 离线名是**本地兜底**，但旧实现 `unified_name_map` 仅 ~21.5% 全宇宙覆盖，导致 70%+ 个股名被迫走网络（push2/tencent）。

旧实现两大缺陷（已修复）：
1. **profile.dat 被主动排除**（原 `_build_unified_name_map` 注释"避免污染"，仅合并 3 源）。
2. **优先级裁决反向**：profile（最旧、含旧名）用 `setdefault` 先占，导致 relation/tdxpkmore 的 `setdefault` 被跳过 → 旧名胜出（如 `002459`=天业通联 而非 晶澳科技）。

## 二、实测各源对全市场（8055）的覆盖率
| 源 | 独立条目 | 全宇宙覆盖 | 说明 |
|---|---|---|---|
| tdxpkmore.cfg | 1373 | 17.0% | 新股/特色，名称最新（最高优先） |
| profile.dat | 1651(1594 入宇宙) | 19.8% | 沪市老股，含旧名（最低优先，仅补缺） |
| relation.dat | 438 | 5.2% | A/B 股，二进制正则 |
| pttab.dat | 1794 | **0.0%** | 已退市老股清单，0 落于当前宇宙 |
| tdxbjmore.cfg | 349 | 4.3% | 北交所 920xxx |
| addedcode_bj.cfg | 346(新码) | 4.3% | 北交所，老码→新 920 码+名 |
| othersg.cfg / xgsg.cfg | 18/24 | 0.5% | 可转债/新股 |

**tdxstat.cfg 经核验无任何名称列**（35 列全数值），故快照本身不可作名称源。

## 三、修复后合并结果（V17.3.2）
合并全部 7 源，优先级（高→低，高优先直接赋值覆盖）：
`tdxpkmore > tdxbjmore/addedcode_bj > othersg/xgsg > relation > pttab > profile(仅 setdefault 补缺)`。

- **全宇宙覆盖：3541/8055 = 44.0%**（旧 ~21.5%，翻倍）
- **纯 A 股覆盖：3379/5831 = 57.9%**
- 更名股裁决正确：`002459`=晶澳科技、`000723`=美锦能源、`688021`=奥福科技、`200530`=冰山（原旧名 天业通联/天宇电气/奥福环保/大冷B 全部被覆盖）

## 四、硬天花板（关键结论）
即使用尽 ZHB 全部名称源，仍有 **~42% 纯 A 股名不在任何 ZHB 文件中**，包括：
- **茅台(600519)、平安(601318) 等蓝筹竟为 None** —— ZHB 根本**不携带主名称总表**，仅含"新股/特色/沪市老股/北交所"等子集。
- 缺失集中于普通主板 bulk（`60`/`00`/`30` 前缀各缺数百只）。

含义：**ZHB 离线名称无法消除网络取数**。约 42% 个股名仍需 push2/tencent 兜底（实时行情自带名，或离线批量场景走网络）。

## 五、对"降低网络消耗"的真实贡献
- ✅ 离线批量/盘前/T+1 场景：个股名本地命中率从 ~21.5% 升至 44%(全宇宙)/58%(纯A股)，对应减少约一倍于该场景的网络名请求。
- ⚠️ 实时路径：name 本就随行情快照返回，ZHB 名仅作缺失兜底，对实时路径网络无额外影响。
- ❌ 剩余 42% 个股名（含茅台/平安）无离线源，无法仅靠 ZHB 降网。

## 六、进一步降网的真正杠杆：持久化名称缓存（建议待办）
ZHB 天花板既知，真正把覆盖率推向 ~95%+ 且不重复耗网的做法：
**在 `get_stock_name_from_zhb` 之上加一层磁盘持久化名称缓存**（如 `cache/name_cache.json` 或 pickle），网络取到的正确名写回缓存，下次直接命中。属于新增子系统，触及 `data_provider.py` 网络路径，需单独立项。

## 七、本次代码改动（core/zhb_client.py）
- 重写 `_build_unified_name_map`：纳入 profile + relation + tdxpkmore + tdxbjmore + addedcode_bj + othersg + xgsg + pttab，修正优先级。
- 新增 `stock_name_map` 规范属性（别名 `unified_name_map` 向后兼容）。
- `get_stock_name` 改走 `stock_name_map`。
- 兼容处理：全角Ａ/Ｂ归一、去除 `(已切换)` 等括注状态、名称含首字母(N/C/ST)亦可识别。
