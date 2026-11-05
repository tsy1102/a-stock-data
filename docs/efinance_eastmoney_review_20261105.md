# efinance 东财数据获取与字段映射复核（2026-11-05）

## 范围与结论

本次固定检查上游源码快照 `c8fd370a3109b2d14a121e3a32a86e9c8354b01b`。按全仓文件树盘点文档、模块入口与配置，阅读 README/API 说明和变更记录，并完整追踪 `common/stock/fund/bond/futures` 的 getter/config、`shared` Session、代码搜索工具及其中全部 Eastmoney URL 字面量。后续在 2026-11-05 12:44（UTC+8）按用户授权，使用本项目请求器完成一次备份域优先的 Ulist 实时字段对照；没有安装或运行 efinance。

**结论：不引入 efinance 依赖，也不替换已有运行路径。** 对照当前实际消费链后，只接入一项低成本调查能力：Ulist 原始证据请求额外包含 `f297`，以便后续用本项目样本核对交易日口径；它仍不是正式字段定义。财务摘要、股东数据、板块成员、快照等接口暂不新增生产调用，因为已有适配或当前没有可证明的字段缺口。此前已修复的问号占位识别及破解目标说明继续保留。

逐源注册表原先把 `东财-ulist239(np/get)::f124` 标为“股东户数?”且已验证。本轮确认 2026-11-02 和 11-03 的两份 Ulist 原始样本中，`f124` 与同股 push2 `stock/get::f86` 分别 20/20 精确相等，值可还原为 Unix 秒行情时间戳；11-05 两端点实时样本也返回接近各自请求时刻的 Unix 秒值。因此已将 Ulist `f124` 纠正为“行情更新时间戳（Unix 秒）”。同号 `东财-push2(stock/get)::f124` 仍是独立的未验证来源路径，保持不变；更完整的证据与处理见本报告“本轮低频主机探测”和[纠正记录](field_verification/adjudications/20261105_ulist_f124_timestamp_correction.md)。

## 上游如何获取东财数据

| 数据用途 | efinance 使用的接口 | 请求与解析方式 |
|---|---|---|
| 全市场行情列表 | `/api/qt/clist/get` | 按 `fs` 市场筛选，使用 `pn/pz` 分页及 `fields` 选字段；先请求第一页估算总数，再用线程池获取分页。 |
| 指定证券最新行情 | `/api/qt/ulist.np/get` | 用 `secids=市场号.代码` 批量指定证券，按字段映射创建表格；解析 `f124` 更新时间戳及 `f297` 最新交易日。 |
| 历史 K 线 | `/api/qt/stock/kline/get` | 传 `secid`、`beg/end`、`klt`、`fqt`；把 `klines` 的逗号分隔字符串按 `fields2` 映射成列。 |
| 日/分钟资金流 | `/api/qt/stock/fflow/daykline/get`、`/api/qt/stock/fflow/kline/get` | 分别用日频/分钟频参数，请求 `f51-f63` 字段后拆分 `klines`。 |
| 基本资料与估值 | `/api/qt/stock/get` | 按 `fields` 请求 PE、PB、行业、市值、ROE、利润率等字段。 |
| 逐笔成交 | `/api/qt/stock/details/get` | 按 `secid` 读取交易明细，并将响应字段整理成价格、成交量、单数。 |
| 代码到行情 ID | `search-codetable.eastmoney.com/codetable/search/web` | 通过搜索返回市场号与证券代码，组成 `市场号.代码`；对搜索结果做本地缓存。 |
| 财务业绩摘要 | `datacenter-web.eastmoney.com/api/data/get`，报表 `RPT_LICO_FN_CPD` | 使用报表名、报告期过滤和分页；响应列为具名字段，含营业收入、净利润、EPS、ROE 等。 |
| 股东户数 | `datacenter-web.eastmoney.com/api/data/v1/get`，报表 `RPT_HOLDERNUM_DET` / `RPT_HOLDERNUMLATEST` | 按证券代码查询报告期及股东户数、变化比例、户均持股和户均市值等具名字段。 |
| 股东持仓明细 | `emh5.eastmoney.com/api/GuBenGuDong/GetFirstRequest2Data`、`GetShiDaLiuTongGuDong` | POST 请求获取股本/股东相关页面数据，包括十大流通股东一类的明细。 |
| 行业/概念成员 | `/api/qt/slist/get` | 通过 `fs` 与 `fields` 查询板块成员及报价字段；不是 `clist` 的同一请求契约。 |
| 快照补充接口 | `hsmarketwg.eastmoney.com/api/SHSZQuoteSnapshot` | 返回具名 JSON 行情快照字段，覆盖最新价、昨收、开高低、成交量额、换手率及买卖盘等。 |

请求构造集中在 `common/config.py` 与 `common/getter.py`。上游把 `clist` 用于市场/板块列表，把 `ulist.np` 用于指定代码集合；这两种请求的参数和分页方式不同，不能仅凭字段编号将它们当成同一个契约。

财务、股东等接口由 `stock/getter.py` 直接拼装 Eastmoney datacenter 报表查询。它们以 `reportName`、过滤式、排序列和分页参数选择业务报表；不同 `RPT_*` 报表可能给相近主题字段使用不同名字、日期和口径，不能把其列名直接合并成同一个源字段。

## 字段映射

下面是 efinance 源码中的映射，表示该客户端如何解释响应；它本身不等于东财官方字段字典。

| 接口/字段族 | efinance 映射示例 |
|---|---|
| Ulist/Clist 行情 | `f12` 代码、`f14` 名称、`f2` 最新价、`f3` 涨跌幅、`f4` 涨跌额、`f5/f6` 成交量/额、`f8` 换手率、`f9` 动态 PE、`f10` 量比、`f13` 市场号、`f15-f18` 最高/最低/今开/昨收、`f20/f21` 总市值/流通市值、`f124` 更新时间戳、`f297` 最新交易日。 |
| K 线 | `f51-f61` 依次映射日期、开盘、收盘、最高、最低、成交量、成交额、振幅、涨跌幅、涨跌额、换手率。 |
| 基本资料 | `f57/f58` 代码/名称、`f162/f167` 动态 PE/PB、`f127` 行业、`f116/f117` 市值、`f173` ROE、`f187` 净利率、`f105` 净利润、`f186` 毛利率。 |
| 日频资金流 | `f51` 日期；`f52-f56` 主力、小单、中单、大单、超大单净流入；`f57-f61` 各级净流入比例；`f62/f63` 收盘/涨跌幅。 |
| 分钟资金流 | 响应按 `f51-f63` 解码；对外主要展示时间及主力、小单、中单、大单、超大单净流入。 |

### Datacenter 具名字段

这些字段来自业务报表 JSON，不属于 `fNN` 路径；以下是 efinance 客户端的映射表，不代表东财公开的正式字段契约。

| 报表 | 源字段示例 | 客户端展示含义 |
|---|---|---|
| `RPT_LICO_FN_CPD` 业绩摘要 | `SECURITY_CODE`、`SECURITY_NAME_ABBR`、`NOTICE_DATE`、`TOTAL_OPERATE_INCOME`、`YSTZ`、`YSHZ`、`PARENT_NETPROFIT`、`SJLTZ`、`SJLHZ`、`BASIC_EPS`、`BPS`、`WEIGHTAVG_ROE`、`XSMLL`、`MGJYXJJE` | 证券身份、公告日、营收及净利润同比/环比、每股收益/净资产、加权 ROE、销售毛利率及每股经营现金流等。 |
| `RPT_HOLDERNUM_DET` / `RPT_HOLDERNUMLATEST` | `HOLDER_NUM`、`HOLDER_NUM_RATIO`、`HOLDER_NUM_CHANGE`、`END_DATE`、`AVG_MARKET_CAP`、`AVG_HOLD_NUM`、`TOTAL_MARKET_CAP`、`TOTAL_A_SHARES`、`HOLD_NOTICE_DATE` | 股东户数、变化比例/数量、报告期、户均市值/持股、总市值/总股本和公告日期。 |

日期字段需分开保留：`END_DATE` 是统计期末，`NOTICE_DATE` / `HOLD_NOTICE_DATE` 是公告日期；它们不能互相替代，也不能单独证明数据在某历史采集时点已经公开。

同号 `fNN` 不能脱离 endpoint 使用。项目已经用跨端点对撞记录处理过同号异义，例如 Ulist 与 push2 的资金流字段、push2 与 K 线字段。后续新增字段仍须以 `(source, 完整 code path)` 作为身份。

## efinance 是否有官方字段对照注册表

检查了上游仓库的公共文件树、README、API 说明、`common/config.py`、`stock/config.py`、`fund/config.py`、`bond/config.py`、`futures/config.py`，以及行情和业务报表的 getter 实现。找到的是**客户端映射表**，没有找到记录“东财官方字段名 ↔ efinance 字段名”的正式注册表：

- `common/config.py` 维护行情、K 线、资金流、基本资料的 `fNN → 中文 DataFrame 列名` 映射。
- `stock/config.py` 维护证券基本资料和龙虎榜报表具名键的中文列名；`bond/config.py`、`fund/config.py`、`futures/config.py` 各有范围较窄的映射。
- `stock/getter.py` 等实现还在解析处直接写了字段转换表和输出列名。这些表说明 **efinance 如何消费响应**，并未附上官方指标代码、语义定义出处、单位/时效契约、证据级别或裁决状态。
- 行情字段 `fNN`、K 线 `fNN`、Datacenter 报表键是不同响应契约。不能只因编号或中文列名相同就跨接口合并；具名报表键也应绑定 `reportName` 和 endpoint。

东方财富官方公开的 Choice/EMQuantAPI 文档描述的是登录授权后使用的指标接口（例如 `css`/`csd` 的 `indicators`），不是 efinance 使用的 `push2`、`datacenter-web` 等匿名 Web JSON 路径。它可以提供官方指标名和独立数据参照，但现有公开文档没有给出这些 Web JSON 响应键与 EMQuant 指标的一对一表，因此不能把官方指标名称直接贴到 efinance 的 `fNN` 上。[EMQuantAPI Python 官方说明](https://quantapi.eastmoney.com/Upload/EMQuantAPI_Python.html)

| 对照层 | 本项目中可用的信息 | 能证明什么 | 不能单独证明什么 |
|---|---|---|---|
| 东财 Web 响应键 | endpoint + 原始 `fNN` 或报表 JSON 完整键 | 字段身份及响应位置 | 官方业务定义、单位和日期口径 |
| efinance 配置映射 | `fNN` / 具名键 → efinance 展示列 | 第三方客户端采用的解释 | 东财官方定义或该解释必然正确 |
| 本项目注册表 | `field_registry.json.source_fields` 的 `source`、完整 `path`、含义、单位、逐源状态和证据 | 项目自己的逐源裁决状态及证据链 | 若证据只是第三方映射，则仍不能升级成官方定义 |
| 官方 EMQuant 指标 | 官方接口指标简名、文档定义及授权接口返回值 | 相应 EMQuant 指标的官方口径 | 与 `push2` 的某个 `fNN` 自动等价 |

本项目已经有比 efinance 配置字典更适合做字段定案的结构：权威记录是 [`field_registry.json`](field_verification/field_registry.json) 的 `source_fields`；[`field_dict.md`](field_dict.md)、[`unknown_fields.md`](unknown_fields.md)、[`field_metadata_gaps.md`](field_metadata_gaps.md) 是导航/生成视图；[`field_source_reference.md`](field_source_reference.md) 是历史协议参考。注册表按 `(source, 完整 code path)` 保留逐源身份、语义和证据，因此能表达同一个 `f124` 在不同 endpoint 上不是同一个字段。

几个可核实的交叉例子：

- `ulist.np/get` 的 `f12`、`f14`、`f2`、`f3`，efinance 分别展示为代码、名称、最新价、涨跌幅；本项目逐源注册表也把对应 Ulist 路径列为股票代码、股票名称、现价、涨跌幅，并标为已验证。这里的项目状态来自项目记录的值级证据，不是因为 efinance 使用了相同标签。
- `ulist.np/get::f124` 是关键冲突：efinance 映射为更新时间戳；项目已有 2026-11-02/03 原始样本的 10 位 Unix 秒值和收盘后时间分布支持该解释，而注册表仍保留“股东户数?”的历史文本，语义完整性检查已把问号识别为待复核占位。这个第三方映射是有用的旁证，但目前没有找到东财对该 Web JSON 键的正式字段定义页，故不应单独作为官方定案。efinance 用 `datetime.fromtimestamp()` 转换，按运行机器本地时区显示，未固定为带时区的北京时间；它只能补强“epoch 秒时间戳”的解释，不能作为时区契约。
- `ulist.np/get::f297` 在 efinance 中被解析为 `YYYYMMDD` 格式的最新交易日；本项目已把它加入 Ulist 原请求作为研究字段，但尚无项目真实响应样本及正式注册表记录。先验证样本日期与交易日和采集阶段，再决定是否入册。
- Datacenter 的 `HOLDER_NUM`、`END_DATE`、`HOLD_NOTICE_DATE` 等是报表 JSON 的具名键。它们与 efinance 展示标签之间的对应可以按“报表名 + 完整键”建立，但要和官方指标口径或网页信息再核，不能只按名称相似连接到项目规范字段。

因此，如果未来把 efinance 映射纳入破解资料，合适做法是将其作为带版本/SHA 的**第三方解释证据**，保留来源链接和完整 endpoint；不能覆盖现有注册表语义、状态或正式证据等级。

## 上游实际使用的接口与请求治理

efinance 直接调用的是 Eastmoney 网站/业务服务接口，而不是官方 EMQuant Python SDK。按源码 URL 和调用封装，接口覆盖如下：

| 用途/模块 | 实际请求端点 | 代码中的请求方式 |
|---|---|---|
| 全市场/板块行情，`common/getter.py` | `push2.eastmoney.com/api/qt/clist/get` | `fs` 过滤，`pn/pz` 分页，`fields` 选列；先取第一页估总数，再由 `ThreadPoolExecutor` 并发拉分页，第一页会再次请求。 |
| 指定证券最新行情 | `push2.eastmoney.com/api/qt/ulist.np/get` | `secids` 批量传市场号和代码，`fields` 选择字段；efinance 将 `f124` 转时间、`f297` 按 `%Y%m%d` 转日期。 |
| 日/分钟 K 线、最近分钟走势 | `push2his.eastmoney.com/api/qt/stock/kline/get`、`.../trends2/get` | 以 `secid`、日期/周期和 `fields1/fields2` 请求；K 线解析使用逗号串位置映射。 |
| 日/分钟资金流 | `push2his.eastmoney.com/api/qt/stock/fflow/daykline/get`、`push2.eastmoney.com/api/qt/stock/fflow/kline/get` | 按频率分别传 `klt`、`lmt`、`fields1/fields2`。 |
| 基本资料、逐笔、板块 | `push2.eastmoney.com/api/qt/stock/get`、`.../details/get`、`.../slist/get` | 基本资料用 `fields`；逐笔按证券 ID；所属板块按 `secid` 查成员。 |
| 股票财务/股东/龙虎榜/新股等 | `datacenter.eastmoney.com/securities/api/data/get`、`datacenter-web.eastmoney.com/api/data/get`、`.../api/data/v1/get` | 使用 `reportName`、过滤式、排序和分页读取具名 JSON 列。 |
| 股东详情与行情快照 | `emh5.eastmoney.com/api/GuBenGuDong/...`、`hsmarketwg.eastmoney.com/api/SHSZQuoteSnapshot` | 前者 POST；快照端点返回具名 JSON。 |
| 基金 | `fundmobapi.eastmoney.com/FundMNewApi/...`、`fund.eastmoney.com`、`fundf10.eastmoney.com`、`api.fund.eastmoney.com` | 净值、基本资料、持仓、排名、公告/经理等不同端点。 |
| 代码搜索 | `search-codetable.eastmoney.com/codetable/search/web` | 搜索代码/名称到 `secid`，结果写本地 JSON 缓存。 |
| 可转债 | `datacenter-web.eastmoney.com/api/data/v1/get` | 由 `bond/getter.py` 直接查询；期货 getter 复用 common 行情函数。 |

**efinance 的限流并非按东财源执行的请求速率限制：**

1. `config/__init__.py` 设 `MAX_CONNECTIONS = 50`；`shared/__init__.py` 的共享 `HTTPAdapter` 将 `pool_connections`、`pool_maxsize` 设为 50，并设 `max_retries=5`。这是连接池与网络重试配置，不是每秒/每分钟额度；`HTTPAdapter` 的默认 `pool_block=False` 也意味着 `pool_maxsize` 不是硬并发闸门。代码没有给该 Adapter 配置 `status_forcelist` 或明确的 `Retry-After` 处理。Requests 文档将状态码重试作为显式 `Retry` 策略配置项；不能把 `max_retries=5` 当作 403/429 专门退避策略。[efinance Session 配置](https://github.com/Micro-sheep/efinance/blob/c8fd370a3109b2d14a121e3a32a86e9c8354b01b/efinance/shared/__init__.py#L8-L15)；[Requests 重试说明](https://requests.readthedocs.io/en/latest/user/advanced/)；[Requests `HTTPAdapter` 参数](https://requests.readthedocs.io/en/stable/api/#requests.adapters.HTTPAdapter)
2. `common/get_quote_history_multi()` 和基金批量历史函数依靠 `multitasking.get_active_tasks()` 检查全局活动任务，超过阈值时 `sleep(3)` 一次；股票基本资料批量函数没有这一检查。多个分页接口使用默认 `ThreadPoolExecutor`。这些是局部并发缓冲，不是精确上限：睡眠后没有循环等到活动数低于阈值，也不区分东财域名或 endpoint。
3. 多个函数另有 `@retry(tries=3[, delay=1])`；它是函数调用失败后的重试，不做每源排队或限速，重试包裹的部分也不一致。
4. `CustomedSession.request()` 默认超时 180 秒，只有经过共享 `session` 的请求能继承它；代码里直接调用 `requests.get/post` 的 Datacenter、emh5、快照等方法绕过该 Session，通常也没有显式 timeout 和共享 Adapter 重试。
5. 源码没有发现统一的 token bucket、请求间隔、按 host 的并发配额、403/429 熔断/冷却或 ban 状态处理。K 线调用还显式 `verify=False`，模块导入时关闭 urllib3 TLS 警告；这与限流无关，但属于应避免照搬的 TLS 风险。

东方财富官方 EMQuantAPI 文档对**授权产品**给出了函数调用频率约束和错误码：当前可核对的 Python 文档明确注明 `css` 截面函数每分钟不超过 700 次，并列出 `EQERR_FREQUENCY_OVER`、`EQERR_OVERSEAS_IP_RESTRICTED`。该限制属于需登录/有权限的 EMQuant 服务，不能外推为 `push2`、`datacenter-web` 等 efinance Web 接口的限额。[EMQuantAPI Python 官方文档](https://quantapi.eastmoney.com/Upload/EMQuantAPI_Python.html)

**对本项目的含义：** 不要复制 efinance 的连接池大小或并发等待来替代本项目按来源分组的全局限流；也不要用 EMQuantAPI 的 700 次/分钟额度推算匿名 Web 接口安全速率。efinance 的接口和字段映射适合做候选/结构参照，但本项目的生产请求仍应经过 `stock_common/sc_datasource/` 适配器及 `stock_common/sc_network.py` 的治理。

## 与本项目的对照

| 能力 | 本项目当前实现 | 对照结论 |
|---|---|---|
| 批量行情 | [`get_em_batch_quotes`](../stock_common/sc_datasource/_eastmoney.py) 使用 push2delay 的 `ulist.np/get`，按代码分批、显式选取已验证字段并做单位换算；[`get_em_ulist_batch`](../stock_common/sc_datasource/_quotes.py) 是返回原始字段记录的适配器。 | 与 efinance 的指定代码批量行情覆盖重叠；保留本项目路径。 |
| 单票行情 | [`_em_quote_full_impl`](../stock_common/sc_datasource/_quotes.py) 调用 `stock/get` 并映射更大的字段集；统一层 [`get_canonical_stock_data`](../core/data_provider.py) 按 TDX、腾讯、东财顺序回退，东财优先 push2delay，再到 push2。 | 字段面和故障回退已超过 efinance 的基础报价封装；不引入第二套包装。 |
| K 线 | 本项目已有 `东财-em_kline_f61` 来源路径和日 K 字段采集/碰撞，业务缓存按交易日复用。 | 字段族重叠，没有功能缺口。 |
| 资金流 | 本项目已有分钟、最新日和历史资金流适配器；多域回退、缓存、单位转换及东财资金流口径都有独立处理。 | 不替换现有 `_em_fflow_request` 路径。 |
| 证券身份 | A 股路径用项目内 `em_secid_prefix` 生成市场号，避免对每个代码请求搜索服务。 | efinance 的搜索适用于代码、名称及多市场解析；本项目报告以 A 股代码为主，新增搜索请求收益有限。 |
| 财务摘要 | 本项目通过新浪/富耀财报、TDX F10 等路径取得和规范化财务字段；统一层会按同报告期组合部分 TTM 指标。 | 未发现当前消费者缺少 `RPT_LICO_FN_CPD` 独有字段的证据。它与本项目现有财务路径同属财务数据主题，增加备用端点会引入报告期、公告日、字段单位及缓存一致性工作，暂不接入。 |
| 股东户数 | [`holder_change`](../stock_common/sc_datasource/_holders.py) 用东财 `RPT_F10_EH_HOLDERNUM` 及 `HOLDER_TOTAL_NUM` / `AVG_FREE_SHARES`，TDX F10 补期，并有 SQLite 缓存。 | 已有东财及 TDX 路径覆盖当前消费；`RPT_HOLDERNUM_DET` / `RPT_HOLDERNUMLATEST` 是同一提供方的另一套报表，未见足以抵消重复请求和日期口径维护成本的缺口，暂不接入。 |
| 股东持仓明细 | TDX F10 `tdx_get_shareholder_research` 已解析十大股东、十大流通股东等信息；报告侧当前未发现对 efinance emh5 明细端点的直接调用需求。 | 不新增 `GetFirstRequest2Data` / `GetShiDaLiuTongGuDong` 适配器。以后若报告明确消费某一缺失明细，再按相同期末和公告日期比对后补充。 |
| 行业与板块 | `get_em_board_members` 通过统一东财适配器走 push2 `clist`，有 15 分钟缓存、交易日失效及 PE/PB 映射测试；`slist` 也已作为采集证据源。 | 未发现 `slist/get` 对当前板块消费提供未覆盖的字段或质量收益，不替换已验证的成员接口。 |
| 快照/逐笔 | 项目已有 Ulist、`stock/get` 全量报价及逐笔数据适配器。 | `SHSZQuoteSnapshot` 没有独立消费者或已知缺口，不增加重复请求。 |

本项目相关实现位置：[`stock_common/sc_datasource/_quotes.py`](../stock_common/sc_datasource/_quotes.py)、[`stock_common/sc_datasource/_eastmoney.py`](../stock_common/sc_datasource/_eastmoney.py)、[`stock_common/sc_datasource/_holders.py`](../stock_common/sc_datasource/_holders.py)、[`stock_common/sc_datasource/_financials.py`](../stock_common/sc_datasource/_financials.py)、[`stock_common/sc_datasource/_industry.py`](../stock_common/sc_datasource/_industry.py)、[`core/data_provider.py`](../core/data_provider.py)、[`stock_common/sc_network.py`](../stock_common/sc_network.py)。真实路由仍以当前代码和测试为准。

### 是否需要同步新增依赖或接口

- **不安装 efinance。** 本项目已有统一网络、限流、域名风险组、缓存、错误处理和来源溯源；引入完整库会多出一套相互竞争的 Session、分页和字段转换路径。
- **不替换行情、K 线、资金流、证券身份路线。** 已有能力与上游接口重叠，且项目对请求治理的控制更完整。
- **已选择的有限接入：Ulist `f297` 仅进入原始证据采集。** `EM_ULIST_RESEARCH_FIELDS` 与通用 `EM_FULL_FIELDS` 分离，因此 push2 与资金流请求维持 `f1-f250`；Ulist 请求增加一项字段但不增加请求次数。代码构造和模拟回归通过。本次取得 `600000` 的单次实时样本：push2 与 push2delay 的 `f297` 均为 `20261105`。它确认请求和字段可用，但单日单票样本不足以确定跨日、盘中/盘后口径，暂不据此更新正式字段注册。
- **暂不接入 `RPT_HOLDERNUM_DET` / `RPT_HOLDERNUMLATEST` 和 `RPT_LICO_FN_CPD`。** 当前消费方已由其他路径供数，尚无需新增 Eastmoney 同源备用接口的可验证缺口；同提供方端点对照也不能单独形成独立来源定案。
- **不新增十大流通股东明细、`slist` 成员生产路由或快照路由。** 当前消费需求不足以证明新增请求值得维护；若需求明确，必须沿 `stock_common/sc_datasource/` 适配器、缓存、限流和字段证据流程实现。

## efinance 映射对本项目的价值与接口替换边界

efinance 的映射值得作为**第三方候选语义和响应解析参照**接入研究材料，但不应替代本项目的字段裁决；它用的多数也是同一东财服务，不能算独立数据源。接口是否可替代要按 endpoint、字段集合、更新时效、缓存与限流分别判断：

| 候选 | 与本项目现状 | 判断 |
|---|---|---|
| `ulist.np/get` | efinance 用 `push2.eastmoney.com`；本项目批量行情及 `f297` 研究字段用 `push2delay.eastmoney.com`。接口路径和参数形态相同，但主机策略、时效和风险组不同。 | **可作为主机级候补，不是新的来源。** 本项目目前有意把 Ulist 固定在 delay 镜像域；不因 efinance 使用主域就切换。若后续需要处理 delay 域 DNS/连接故障，可先比较同一批小样本字段值、缺失率和 `f124/f297`，并为主域单独限速。不得在 403/429 后切主机规避封禁。 |
| `stock/get` | 本项目已有主域 `get_em_quote_full()` 和带缓存的 delay 版 `get_em_quote_full_delay()`；统一层已有回退。efinance 只提供对同一接口的封装和字段改名。 | **无需替换。** 当前已经覆盖同一业务接口，项目还把来源、缓存、时效和风控接进统一层。 |
| K 线、资金流 `daykline/get` / `kline/get` | 本项目已有对应适配器与资金流端点顺序；历史资金流已区分 push2his 全窗口、push2 和 delay 保底。 | **无需搬入 efinance 实现。** 它可用于核对字段解析和参数差异，不应覆盖项目自己的历史窗口、限流和日期语义。 |
| `clist/get`、`slist/get` | 本项目已有板块/排行适配，并保留 Slist 研究采集。 | 仅在出现明确字段或覆盖缺口时补充；efinance 自身的线程池分页方式不适合替代项目网络层。 |
| Datacenter 股东/财务报表 | efinance 使用其他 `RPT_*` 报表；本项目已有东财 holder 路径和其他财务源。 | 可先做报表名、字段、报告期与公告日的离线交叉表。只有某个消费者确实缺字段或缺历史期时，才增加同源备用接口。 |
| `SHSZQuoteSnapshot` 快照 | efinance 解析了逐档买卖盘等具名字段；当前报告没有确认本项目生产消费者存在对应缺口。 | 是可能的补充候选，不适合整体替换 `stock/get`，因为字段面不同且它不返回同一份 `fNN` 合约。若要接入，应只补明确缺少的字段并统一走网络层。 |

本项目限流配置把 `push2.eastmoney.com` / `push2his.eastmoney.com` 等归为 0.25 RPS 风险组，把 `push2delay.eastmoney.com` 设为独立 1.0 RPS 风险组；它们仍共享项目的东财全局跨进程节奏。efinance 的主机选择不能覆盖这套项目策略。具体实现见 [`_eastmoney.py`](../stock_common/sc_datasource/_eastmoney.py)、[`_quotes.py`](../stock_common/sc_datasource/_quotes.py)、[`sc_network.py`](../stock_common/sc_network.py) 与 [`data_provider.py`](../core/data_provider.py)。

### 本轮低频主机探测

DNS 失败只在 Codex 受限命令行中复现：该环境无法访问本机 DNS/TUN 路径；在主机网络上下文中，系统查询经 FlClash TUN 返回 `push2delay.eastmoney.com` 的 fake-IP `198.18.0.113`，Chrome 可解析并读取东财 JSON，项目 `check_em_health.py` 对 push2 与 push2delay 的 `stock/get` 探针也各返回 HTTP 200。因此没有证据支持修改 FlClash 或 Windows DNS；问题边界是受限命令行与主机网络的隔离差异。安装版本 `v0.9.1` 的 [FlClash 配置源码](https://github.com/chen08209/FlClash/blob/v0.9.1/lib/models/clash_config.dart) 默认 DNS 模式为 fake-IP，并默认劫持 `any:53`；这与本机观察到的 DNS 路径一致。项目 `_do_request()` 显式禁用环境/系统 HTTP 代理，但操作系统启用 TUN 时，DNS 和网络包仍由 FlClash 接管；本次成功证明该链路可用，不证明 FlClash 将 Eastmoney 规则归类为 `DIRECT`。本轮没有修改系统网络设置。

在用户授权后，严格按备用域优先，对 `600000` 的 Ulist 同一字段集（`f12/f14/f2/f3/f124/f297`）使用项目 `_quick_request()` 各发一次 GET：`push2delay` 于 12:44:47、`push2` 于 12:44:53（UTC+8），每个请求 `max_retries=1`，两次开始间隔 6 秒。两端均为 HTTP 200、`rc=0`，字段如下：

| 字段 | push2delay | push2 | 结果 |
|---|---:|---:|---|
| `f12` | `600000` | `600000` | 一致 |
| `f14` | `浦发银行` | `浦发银行` | 一致 |
| `f2` | `9.89` | `9.89` | 一致 |
| `f3` | `-1.98` | `-1.98` | 一致 |
| `f124` | `1793853860` | `1793853890` | 相差 30 秒 |
| `f297` | `20261105` | `20261105` | 一致 |

两个 `f124` 值按 Unix 秒转换分别为 2026-11-05 12:44:20 与 12:44:50（UTC+8），两端相差 30 秒，符合分别返回行情快照更新时间的表现。结合 2026-11-02/03 共 40/40 条历史记录中 `ulist::f124 == stock/get::f86` 的精确配对，已将 `东财-ulist239(np/get)::f124` 从占位含义纠正为“行情更新时间戳”，单位 `Unix 秒`；明确加入“同义”标记后，注册表映射投影也不再把该关系误标为不同义。该纠正只适用于 Ulist `f124`，push2 `stock/get::f124` 仍未验证。`f297` 与本次数据日期相同，但目前只有单日单票实测，仍需跨日样本确认其日期口径。

约 13:53（UTC+8）又通过项目 `_quick_request()` 对 `push2delay` 发出一次低频 Ulist 请求，返回 `None`，没有应用层响应；未重试。FlClash 当时为“规则”模式、TUN 开启、系统代理关闭，实时连接面板未显示 Eastmoney 活动连接。面板只展示当前活动连接，因此这不能区分 DNS 失败与连接建立前的其他失败，也不能证明 Eastmoney 命中 `DIRECT`；当前规则的具体命中动作仍未核实。本次没有修改 FlClash 或 Windows 网络设置。

此次成功请求排除了“当前主机网络无法解析 Eastmoney”的说法，也没有触发封禁或传输失败；单票、单时点的跨主机对照尚不足以启用生产主机切换。探测没有运行采集、写入业务缓存，也没有绕过 `_quick_request()` 的共享限流。后续扩展必须继续遵守 [`field_verification/README.md`](field_verification/README.md) 的备用域优先规则，并在传输异常或封禁时停止。

**替换原则：** 只有明确的项目数据缺口，或经过限流内的逐字段/来源日期/更新阶段/单位对照并有成功样本，才考虑替代某个具体 endpoint；替代后还要更新适配器测试、来源注册、缓存有效期和来源溯源。整体引入 efinance 不会增加东财上游覆盖或独立证据，反而会绕过项目的统一限流、故障隔离和缓存治理。

## 可借鉴内容与不应照搬的实现

可借鉴的是“按 endpoint 明列请求字段并集中维护映射”的组织方式，以及 Ulist 响应中同时观察行情更新时间和最新交易日的思路。为此，本项目新增 `EM_ULIST_RESEARCH_FIELDS` 并仅对 Ulist 请求 `f297`；不扩大复用的 `EM_FULL_FIELDS`，避免将未知字段带入 push2 或资金流路径。

不建议复制其请求策略：

- `clist` 先取第一页估算分页后，线程池会再次请求第一页；分页并发也没有接入本项目按来源分类的全局限流。
- 多个 `session.get()` 调用没有显式设置请求超时；共享 Session 的 `HTTPAdapter` 重试并不等价于本项目的来源级限流、断路器或缓存。
- 历史 K 线请求使用 `verify=False`，并全局关闭 urllib3 的 TLS 警告。
- 请求同时使用 HTTP 与 HTTPS。项目现有网络适配器统一负责超时、限流、来源熔断和回退，不能因 efinance 使用某个 URL 就改成本项目直连调用。
- 上游变更记录显示行情分页和盘中重复记录都曾需要修复；因此它更适合做字段/协议交叉参照，不适合代替本项目已有的可靠性控制。

## `f124` / `f297` 的本地证据与后续边界

efinance 的 `EASTMONEY_QUOTE_FIELDS` 把 `f124` 映射为“更新时间戳”、`f297` 映射为“最新交易日”，并在最新行情结果中将前者转为本机时间、后者解析为日期。本项目 2026-11-02 与 2026-11-03 的保存样本给出更直接的路径区分：

- `docs/field_verification/20261102/raw_ulist239.json` 与 `20261103/raw_ulist239.json` 各有 20 个 Ulist 股票样本；`f124` 为约 10 位 Unix 秒值，按北京时间转换后分别落在文件对应数据日 15:31 至 16:12。
- 同日 `raw_push2.json` 的 20 个 `f124` 值均为 `0.0`。
- 这支持“Ulist 的 `f124` 是行情更新时间戳，单位为 Unix 秒”的解释，也证伪把 Ulist `f124` 当股东户数的猜测；它不能证明 push2 `stock/get` 的 `f124` 同义。
- 原逐源注册表曾保留“股东户数?”占位，本轮依据两日 40/40 条历史跨端点精确匹配及 2026-11-05 两域实时响应，将 `东财-ulist239(np/get)::f124` 纠正为“行情更新时间戳（Unix 秒）”。`东财-push2(stock/get)::f124` 是独立完整路径，仍保持未验证。efinance 的字段映射仅作次级佐证；裁定主要依据本项目保存样本、push2 `f86` 已验证语义和实时 Ulist 响应。
- `f297` 在本轮采集前尚未出现在本项目已保存的 Ulist 样本及逐源字段登记中。代码现已在原有 Ulist 批量请求里附带此字段，无新增请求；测试确认 `f1-f250` 原样保留且只有 Ulist 额外请求 `f297`。2026-11-05 对 `600000` 的 `push2delay` 与 `push2` 实时样本均返回 `20261105`，确认该字段可请求且两主机值一致；但目前只有单日单票证据，尚不能定案其跨日及盘中/盘后口径。后续日常采集取得多日样本后，应与文件名数据日、实际交易日及采集阶段交叉核验；确认之前不登记正式语义，也不接入报告日期或缓存键。

## 版本与授权提示

本次检查的源码快照中，`pyproject.toml` 声明版本为 `0.5.9`，`changelog.md` 最新条目为 v0.5.9（2026-07-17，适配搜索接口变更）；GitHub Releases 页面当前可见最新发布标签为 v0.5.5。版本核对时应区分默认分支源码、包元数据、变更记录和 GitHub Release 标签。

README 声明该项目仅供学习交流、不得用于商业用途，而仓库另有 MIT 许可证文件。当前任务只读取源码作为接口实现参考，没有复制或引入其代码；若将来直接复用代码，应先单独核实许可边界。

## 上游源码定位

以下链接固定到本次检查的上游提交：

- [请求字段、市场过滤器、K 线与行情字段映射](https://github.com/Micro-sheep/efinance/blob/c8fd370a3109b2d14a121e3a32a86e9c8354b01b/efinance/common/config.py#L93-L138)
- [行情列表、K 线、资金流、基本信息及 Ulist 实时行情请求](https://github.com/Micro-sheep/efinance/blob/c8fd370a3109b2d14a121e3a32a86e9c8354b01b/efinance/common/getter.py)
- [股票基本资料字段映射](https://github.com/Micro-sheep/efinance/blob/c8fd370a3109b2d14a121e3a32a86e9c8354b01b/efinance/stock/config.py#L3-L17)
- [业绩摘要与股东户数 datacenter 报表](https://github.com/Micro-sheep/efinance/blob/c8fd370a3109b2d14a121e3a32a86e9c8354b01b/efinance/stock/getter.py#L752-L934)
- [股东持仓、行业板块成员与快照接口](https://github.com/Micro-sheep/efinance/blob/c8fd370a3109b2d14a121e3a32a86e9c8354b01b/efinance/stock/getter.py)
- [代码搜索与 secid 生成](https://github.com/Micro-sheep/efinance/blob/c8fd370a3109b2d14a121e3a32a86e9c8354b01b/efinance/utils/__init__.py#L103-L220)
- [HTTP Session 重试与连接池](https://github.com/Micro-sheep/efinance/blob/c8fd370a3109b2d14a121e3a32a86e9c8354b01b/efinance/shared/__init__.py#L10-L14)
- [并发阈值与多证券 K 线重试](https://github.com/Micro-sheep/efinance/blob/c8fd370a3109b2d14a121e3a32a86e9c8354b01b/efinance/config/__init__.py#L8-L14)、[common K 线批量任务](https://github.com/Micro-sheep/efinance/blob/c8fd370a3109b2d14a121e3a32a86e9c8354b01b/efinance/common/getter.py#L171-L216)、[基金批量任务](https://github.com/Micro-sheep/efinance/blob/c8fd370a3109b2d14a121e3a32a86e9c8354b01b/efinance/fund/getter.py#L111-L133)
- [默认 180 秒超时与连接错误提示封装](https://github.com/Micro-sheep/efinance/blob/c8fd370a3109b2d14a121e3a32a86e9c8354b01b/efinance/shared/tickflow_prompt.py#L97-L108)
- [版本、变更记录与 GitHub Releases](https://github.com/Micro-sheep/efinance/blob/c8fd370a3109b2d14a121e3a32a86e9c8354b01b/pyproject.toml)、[changelog](https://github.com/Micro-sheep/efinance/blob/c8fd370a3109b2d14a121e3a32a86e9c8354b01b/changelog.md)、[Releases](https://github.com/Micro-sheep/efinance/releases)

2026-11-05 另核对了 GitHub 当前 `main`：其行情字段表仍把 Ulist/Clist 的 `f124`、`f297` 分别映射为更新时间戳和最新交易日，并在最新行情解析中转换这两个值。该主分支交叉核验只说明第三方当前实现仍如此解释，不构成东财官方字段契约。

- [当前 main 的行情字段映射](https://github.com/Micro-sheep/efinance/blob/main/efinance/common/config.py#L757-L797)
- [当前 main 的行情请求与解析](https://github.com/Micro-sheep/efinance/blob/main/efinance/common/getter.py)
