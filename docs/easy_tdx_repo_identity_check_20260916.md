# easy-tdx 仓库（yanwei99521）身份核查与接入价值分析

> 分析日期：2026-09-16 ｜ 数据来源：通达信（TDX TCP 协议客户端族：eltdx / easy_tdx / mootdx）
> 性质：**仅分析、不改动代码**（与 `docs/tdx_sources_consolidation_analysis_20260916.md` 联动）
> 结论不构成投资建议。

---

## 〇、一句话结论

`github.com/yanwei99521/easy-tdx` **不是新数据源**，它就是项目 `requirements.txt` 已在用的 `easy-tdx` PyPI 包（由上游 `handsomejustin/easy_tdx` 发布）的一个 GitHub fork。项目 `tdx_client.py` 当前正是用它的 `easy_tdx.client.TdxClient` / `easy_tdx.mac.client.MacClient` API 作为**行情兜底 + ZHB 下载 + 板块归属**源。

→ 因此"是否需要接入"的答案是：**已经接入了**，无需再做接入动作；其超出现有范围的扩展能力（期货/港美股/缠论/回测/因子/Web UI）按项目"轻量优先"纪律**不应引入**。

---

## 一、仓库概况（yanwei99521/easy-tdx）

| 维度 | 内容 |
|---|---|
| 语言 | Python 核心 + Vue3/Vite/TS 前端（回测 Web UI） |
| 协议/端口 | MAC 协议 7709（A股）/ 7727（扩展市场）；标准 TdxClient 7709 |
| 市场 | A股（沪深北/科创/创业）、港股、美股、**期货**（郑/大/上期/中金所）；文档未提期权 |
| 行情 | 多周期 K线（前/后复权）、实时五档、分时、逐笔成交、集合竞价、异动 |
| 板块 | 行业/概念/风格/地区板块列表、成分、汇总、排行、N日涨跌 |
| 资金流 | 个股/板块/历史主力净流入、大单维度 |
| 财务 | 新浪三表、TDX 原生 F10、巨潮公告（独立 HTTP 源，不依赖行情服务器） |
| 分析 | 34 个技术指标（基于 MyTT）、完整缠论（分型→笔→中枢→买卖点→背驰） |
| 量化 | 回测引擎 + Web UI、19 内置因子 + IC/分层、组合优化、选股扫描 |
| 离线 | 直读本地 `vipdoc/*.day`（无需联网） |
| 交付 | Python API + Click CLI + FastAPI REST/WebSocket 三通道 |
| 许可 | MIT |

**上游关系**：README 徽章与 Wiki 全部指向 `github.com/handsomejustin/easy_tdx`；并在 NOTICE 中声明借鉴 `pytdx` / `xmtdx` / `mootdx` / `MyTT`。即 `yanwei99521/easy-tdx` = `handsomejustin/easy_tdx` 的 fork/镜像，`easy-tdx` PyPI 包由 handsomejustin 发布。

---

## 二、身份同一性证据链（铁证）

1. **本机 pip 元数据**（命令 `py -3.12 -m pip show` / `importlib.metadata`）：
   - `Name = easy-tdx`，`Version = 1.32.6`
   - `Summary = "通达信 TCP 协议行情数据客户端，支持在线行情、离线数据读取与写入同步"`
   - README Description 内含：`[![GitHub Repo stars](...)](https://github.com/handsomejustin/easy_tdx)`、`https://pypi.org/project/easy-tdx/`、`deepwiki.com/handsomejustin/easy_tdx`
   - 安装位置：`<USER_HOME>\AppData\Local\Programs\Python\Python312\Lib\site-packages\easy_tdx`

2. **requirements 版本演进吻合**：`requirements.txt:33` 锁定 `easy-tdx>=1.32.6,<2.0`，注释记录的 1.20.4（K线解码修复）→ 1.32.6（新增 `get_price_limits`/`get_market_stat`/`get_security_list_all`、SecurityQuote 直解 `s_vol/b_vol/rise_speed`）与该库活跃开发节奏一致。

3. **API 导入路径 100% 吻合**：项目 `core/tdx_client.py` 实际调用：
   - `from easy_tdx.client import Market` / `from easy_tdx import Market, KlineCategory`
   - `from easy_tdx.client import TdxClient`
   - `from easy_tdx.mac.client import MacClient` / `from easy_tdx.mac.enums import BoardType`

   上述深层嵌套模块路径（`easy_tdx.client` / `easy_tdx.mac.client` / `easy_tdx.mac.enums`）与该仓库 README 的 `MacClient.from_best_host()` / `TdxClient` API 完全一致——不同库不会恰好共用这种私有路径结构。

4. **家族自洽**：该库 NOTICE 明确"mootdx 为工程化封装参考"，与项目"eltdx 主 → easy_tdx 兜底 → mootdx 末级"的三级链路在血缘上自洽。

> 注：WebFetch 抓取 `pypi.org/project/easy-tdx` 返回 404 系 PyPI 反爬误报（本机已确装 1.32.6，且元数据内 PyPI 徽章链接有效）；`handsomejustin/easy_tdx` 与 `yanwei99521/easy-tdx` 的 GitHub 页面均可正常访问，二者为上游/fork 关系。

---

## 三、能力对比矩阵（全功能 vs 项目实际用量）

| 该库能力 | 项目是否使用 | 项目现有替代 | 是否增量价值 |
|---|---|---|---|
| TCP 行情/K线（MAC 7709） | 部分（兜底） | **eltdx 主源已覆盖** | 无（eltdx 更快更稳） |
| **ZHB 下载** | **是（唯一路径）** | eltdx 经 0x06B9 可替（已实证） | 当前唯一硬职责，待迁移 |
| 板块归属 MacClient | 是（tdx_get_belong_boards） | 东财 `get_em_belong_boards` 兜底已存在 | 可替（东财申万二级口径） |
| 期货/港股/美股 | 否 | `tdx_connector` MCP 云对撞已覆盖 | 无 + 超 A股定位 |
| 34 技术指标 | 否 | TA-Lib 61 CDL + 自研 | 无（重叠） |
| 缠论 | 否 | 项目无需求 | 偏离定位 |
| 回测/因子/Web UI | 否 | 偏离"数据治理"定位 | 负价值（重依赖） |
| 离线 .day 读取 | 否（val 直读 vipdoc） | 已覆盖 | 无 |
| F10 财务（新浪/巨潮） | 否 | TDX 0x0010 / 东财 | 无 |

---

## 四、有无优势 / 是否需要接入

### 4.1 作为"行情数据源"——已用，无增量
项目已将其作为 eltdx 之下的二级兜底 + ZHB 下载源，且用户已决策"eltdx 连续运行数个交易日后才评估删除 easy_tdx"（见 `automation_update` 任务 `18fa9ee1`，2026-09-21 回顾）。再"接入"一个 fork 仓库 = 重复，零收益。

### 4.2 扩展功能——按轻量优先纪律不引入
其独有的期货/港美股、缠论、回测引擎、因子、Web UI 与项目定位冲突：
- 项目定位是**每日收盘采集 → 字段治理 → 跨源对撞 → 报告**的轻量 A股数据治理管线，不是量化交易终端。
- 历史纪律一致：V17.0.29 移除 thsdk（盘中才可用、盘后无意义）；放弃 TdxQuant 五套 func 接口（轻量优先）；tdxrs 经评估无日频不可替代性。引入回测/Web UI 会强拉 FastAPI + Uvicorn + Vue3 前端，**严重违反轻量优先**。
- 期货/港美股本地源冗余：`tdx_connector` MCP 云对撞神谕已覆盖，且项目为 A股投研，扩展市场非刚需。
- 技术指标重叠：已有 TA-Lib 61 种 CDL + 自研指标；其"捉妖大师/30日乖离率信号"等特色若报告需要，**单独移植 MyTT 算法片段即可**，无需引整库。

### 4.3 唯一正向用途：源码参考
`yanwei99521/easy-tdx`（=handsomejustin 源码）可作为**读源码、修 bug、移植算法**的参考仓库。项目依赖仍走 PyPI 官方 `easy-tdx` 包（=handsomejustin 发布版），不切换 fork 源，避免供应链漂移。

---

## 五、风险与注意

1. **版本锁 `<2.0` 不可轻易解除**：`requirements.txt:33` 刻意锁 `easy-tdx<2.0`。若该仓库发布 2.0 含 breaking change（尤其 `MacClient` 板块路径——这是 easy_tdx 当前不可替代兜底），升级前须回归 `tests/data/test_data_tdx.py` 等 board/quote 用例。
2. **fork 漂移风险**：`yanwei99521` 可能滞后或 diverge 于上游 handsomejustin；项目装的是 PyPI 官方包（=handsomejustin），不受 fork 直接影响。读源码可取 fork 页，但生产依赖以 PyPI 为准。
3. **与 consolidation 分析联动**：本核查进一步坐实上一轮 `tdx_sources_consolidation_analysis_20260916.md` 的判断——easy_tdx 当前唯一硬职责是 **ZHB 下载**（eltdx 0x06B9 可替）+ **MacClient 板块归属**（东财兜底可替）；用户已决策暂缓删除、待 eltdx 稳定后按 P0→P1 三步退役。

---

## 六、建议

| 项 | 建议 |
|---|---|
| 是否作为新源接入 | **否**（已是依赖项） |
| 是否引入其扩展能力 | **否**（轻量优先 + A股数据治理定位） |
| fork 仓库的用途 | 仅作源码阅读 / 算法移植参考 |
| 版本策略 | 维持 `easy-tdx<2.0` 锁；升级须测试回归 |
| 后续动作 | 与 consolidation 计划联动：eltdx 稳定后按 P0→P1 让 easy_tdx 退役（ZHB→eltdx、board→东财、适配器链 eltdx→mootdx 坍缩） |

---

*本分析为架构审计，未改动任何代码与依赖。数据来源：通达信。以上结论不构成投资建议。*
