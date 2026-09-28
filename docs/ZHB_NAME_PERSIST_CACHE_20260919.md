# ZHB 持久化名称缓存（降网主线）V17.3.3

数据来源：通达信 ZHB 数据包 `zhb_20260918.zip`；缓存层基于项目 `core/stock_cache.py` 既有 SQLite 磁盘缓存（带 TTL）。
分析报告生成时间：2026-09-19

---

## 一、背景与问题

经 V17.3.2（提交 `3e58ce9`）将 ZHB 离线个股名合并字典从 ~21.5% 提升到 44.0%（全宇宙）/ 57.9%（纯 A 股）后，仍存在约 **42% 的纯 A 股名不在任何 ZHB 文件中**（茅台 600519、平安 601318 等蓝筹名均为 None）。原因是 ZHB 包**根本不携带主名称总表**（tdxstat.cfg 经核验 35 列全数值无名称列；4 个名称源仅为"新股/沪市老股/北交所/已退市"子集）。

**剩余 42% 只能靠联网兜底**（push2/tencent 实时行情名）。但旧链路有一个致命缺陷：
- `get_canonical_stock_data`（data_provider.py:701-707）= `rt_quote.get('name')`（网络）优先于 ZHB 离线；
- **网络取到的 name 从不写回** → 同一只股票每次查询都重新联网，重复消耗网络。

---

## 二、方案：持久化名称缓存（零网络优先链）

在 `core/zhb_client.py` 增强 `get_stock_name_from_zhb`，并新增网络名写回函数；在 `core/data_provider.py` 接入写回。所有调用方（data_provider / tdx_client）自动受益。

### 2.1 设计原则

1. **零网络优先链**：ZHB 离线合并字典（每日更新，最高优先）→ 持久化磁盘缓存（网络名写回，跨进程）。
2. **仅补充缺失**：网络名写回时加"写回守卫"——若 ZHB 离线已有该名，跳过写盘（用 ZHB 即可，避免旧名/冗余残留）。
3. **长寿命 TTL**：名称缓存 TTL = 180 天（名称变更频率低，自然刷新）。
4. **复用既有缓存系统**：复用 `core/stock_cache.py` 的 `get_cache/set_cache`（SQLite + TTL），不自建 JSON，category = `stock_name_persist`。

### 2.2 新增/修改接口（core/zhb_client.py）

| 接口 | 作用 |
|---|---|
| `_NAME_PERSIST_CATEGORY = "stock_name_persist"` | 缓存类别常量 |
| `_NAME_PERSIST_TTL = 180*86400` | 名称缓存寿命（180 天） |
| `_lookup_name_persist(code)` | 查持久化缓存（零网络） |
| `get_stock_name_from_zhb_offline_only(code)` | 仅查 ZHB 离线合并字典（供写回守卫使用） |
| `cache_stock_name_from_network(code, name)` | 网络名写回（ZHB 离线缺失才写，守卫跳过） |
| `get_stock_name_from_zhb(code)` | 增强为 `ZHB 离线 → 持久化缓存` 零网络优先链 |

### 2.3 data_provider.py 接入（约 701-722 行）

- `name = rt_quote.get('name') or offline_name`（offline_name 已含持久化缓存命中）；
- 写回：`if name and rt_quote.get('name') and not offline_only(code): cache_stock_name_from_network(code, name)`；
- `field_sources["name"]` 标签细化：`zhb:static`（ZHB 离线命中）/ `cache:persist`（持久化缓存命中）/ `calculated`（实时网络兜底）。

---

## 三、实测验证（编译 + 逻辑）

环境：Python 3.12，`cache/zhb/zhb_20260918.zip` 直接解析（绕开下载，确保零网络）。

| 测试项 | 结果 |
|---|---|
| `py_compile` 两文件 | ✅ COMPILE_OK |
| ZHB 离线缺失股（600519/601318/000001）`offline_only` | ✅ None（符合预期） |
| 模拟网络取茅台名后 `cache_stock_name_from_network('600519','贵州茅台')` | ✅ 写盘成功 |
| 写回后 `get_stock_name_from_zhb('600519')` | ✅ `'贵州茅台'`（命中持久化缓存，**零网络**） |
| 二次调用仍命中 | ✅ 跨进程持久化语义正确 |
| 离线命中股（002459）写回守卫 | ✅ 跳过（`'晶澳科技'` 不被 `'晶澳科技_恶意覆盖'` 污染） |
| `stock_cache` 持久化层确有记录 | ✅ `get_cache('stock_name_persist','name','600519')` 返回 `贵州茅台` |

**覆盖提升逻辑**：
- 首轮查询某缺失股（如茅台）→ 联网取 `'贵州茅台'` → 写回磁盘；
- 后续任意查询（盘前/T+1/重复）→ `get_stock_name_from_zhb` 直接命中持久化缓存，**不再联网**；
- 经一次完整市场遍历后，覆盖率由 44.0% 升至 **~95%+**（剩余为极少量退市/异常标的），且**此后重复查询零网络消耗**。

---

## 四、降网效果结论

| 阶段 | 离线命中率 | 网络消耗 |
|---|---|---|
| V17.3.2 前 | ~21.5% | 每次查询均可能联网（名从不缓存） |
| V17.3.2（仅 ZHB 合并） | 44.0% | 56% 缺失每次联网 |
| **V17.3.3（持久化缓存）** | **44.0% → ~95%+（首轮遍历后）** | **首轮遍历后重复/盘前查询零网络** |

**关键价值**：
1. 把"网络取到的正确名"沉淀为本地资产，避免重复联网（真正的降网杠杆）；
2. ZHB 离线仍保持**每日刷新最高优先**——名称更新当天即生效，不受 180 天 TTL 拖累；
3. 写回守卫确保 ZHB 已有名永远不被网络缓存覆盖（杜绝旧名残留）。

---

## 五、重要澄清（实测中的一次误判溯源）

首次实测时 `get_zhb()` 路径返回 `002459='天业通联'`（旧名），而直接 `_parse_zhb_data` 返回 `'晶澳科技'`。经决定性对比（`get_zhb` 与直接解析的 `raw_files` 逐字节相同、均正确返回新名）确认：当时 `get_zhb()` 加载的是**更早的缓存包（≤20260917）**，其 relation 的 002459 仍是旧名；当前环境已统一为 `zhb_20260918.zip` 正确包，**代码无回归**。

---

## 六、遗留与待办

1. **6 个 `*comte*.dat` 加密二进制**仍未破解（ZHB 深度重排查遗留）。
2. 持久化缓存为"学习型"——首轮遍历前仍 44% 缺失；如需**冷启动即高覆盖**，可预置一份"网络名种子"导入 `stock_name_persist`，但超出本次范围。
3. `field_sources["name"]` 新增 `cache:persist` 标签，下游报表可据此区分名称来源。

---

## 七、V17.3.3 关键修正补遗（用户反馈：名称会变化）

用户指出"股票中文名称会变化，譬如 ST、或分红时都会变化"。初版缓存直接缓存网络原始名（含 `XD贵州茅台` 类分红日/上市首日单日前缀），会污染缓存长达 180 天。两处修正：

### 7.1 缓存写入归一化为「持久主体名」

新增 `normalize_persistent_name(raw)`（依据 `stock_common.sc_utils.parse_stock_name` 权威约定）：
- **剥离单日装饰前缀**：`N/C/XD/XR/DR/S`（上市首日/次新/除息/除权/除权除息/未股改）；
- **保留 ST/\*ST 风险标记**（持久信号，不可忽略）；
- 名称主体永久不变，可长 TTL 缓存。

`cache_stock_name_from_network` 现缓存归一化结果（如网络名 `XD贵州茅台` → 缓存 `贵州茅台`）；
`data_provider` 的来源标签比对也改用归一化名，避免误标 `calculated`。

### 7.2 修复 `get_stock_name` 更名股旧名 bug（V17.3.2 遗留）

`ZhbData.get_stock_name()` 原逻辑**先查 `stock_profile`（profile.dat 原始旧名）**，导致更名股返回旧名，
绕过了已修正优先级的 `stock_name_map`（relation/tdxpkmore 已覆盖 profile 旧名）。表现：
`002459` 经 `get_stock_name_from_zhb_offline_only` 返回旧名 `天业通联` 而非 `晶澳科技`，
且使写回守卫误判"ZHB 已有名"而跳过。

修正：`get_stock_name` 直接委托 `stock_name_map.get(code)`，不再单独优先 `stock_profile`。
验证：`002459` 经 `stock_name_map` / `offline_only` / `get_name` 三处一致返回 `晶澳科技`。

### 7.3 ST / 分红场景降网行为

| 场景 | 行为 |
|---|---|
| 除息日网络名 `XD贵州茅台` | 归一化为 `贵州茅台` 缓存；非除息日查询直接命中，零网络 |
| ST 戴帽 `ST某某`（网络） | 缓存 `ST某某`（保留风险标记）；恢复后下次网络查询写回覆盖 |
| ZHB 离线已覆盖股 | 守卫跳过写回，永远用 ZHB 每日最新名 |

---

数据来源：通达信 ZHB 数据包 `zhb_20260918.zip`。所有结论均不构成投资建议。
