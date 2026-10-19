# 数据源与 GitHub 仓库谱系

> 由 `field_verification/source_lineage.json` 自动生成。只记录有项目内或上游证据的关系；
> 项目证据状态与对话确认状态分列；确认某客户端仓库不等于确认它是底层数据提供方。

| 字典来源 | 采集器状态 | 运行时命名空间 | 数据提供方 | 独立来源族 | 可作锚 | 项目证据 | 对话确认 |
|:--|:--|:--|:--|:--|:--:|:--|:--|
| AxData | active | axdata | AxData multi-provider framework; current shortline interface uses Tongdaxin | 未确认（unconfirmed） | 否 | confirmed | confirmed（2026-10-08） |
| TDX(双命名源) | active | tdx | Tongdaxin | tdx（confirmed） | 是 | confirmed | confirmed（2026-10-06） |
| TDX-eltdx(适配层) | active | eltdx | Tongdaxin | tdx（confirmed） | 是 | confirmed | confirmed（2026-10-06） |
| ZHB-tdxstat | active | zhb | Tongdaxin | tdx（confirmed） | 是 | confirmed | confirmed（2026-10-06） |
| ZHB-tdxstat2 | active | zhb | Tongdaxin | tdx（confirmed） | 是 | confirmed | confirmed（2026-10-06） |
| ZHB-tipinfo | active | zhb | Tongdaxin | tdx（confirmed） | 是 | confirmed | confirmed（2026-10-06） |
| FTShare | active | ftshare | FTShare hosted MCP service at market.ft.tech | 未确认（unconfirmed） | 否 | confirmed | pending |
| Levistock历史未归属 | historical | 未确认 | Levistock 多源客户端包装库的历史未归属字段记录 | 未确认（unconfirmed） | 否 | confirmed | confirmed（2026-10-06） |
| 开盘红(Levistock适配) | active | kph | KPH / 开盘红（通过 Levistock 的历史方法路径） | kph（confirmed） | 是 | confirmed | confirmed（2026-10-06） |
| reports | active | reports | Eastmoney | eastmoney（confirmed） | 是 | unconfirmed | pending |
| 东财-clist | active | clist | Eastmoney | eastmoney（confirmed） | 是 | confirmed | confirmed（2026-10-08） |
| 东财-datacenter(英文键) | active | datacenter | Eastmoney | eastmoney（confirmed） | 是 | confirmed | confirmed（2026-10-08） |
| 东财-em_kline_f61 | active | em_kline_f61 | Eastmoney | eastmoney（confirmed） | 是 | confirmed | confirmed（2026-10-08） |
| 东财-push2(stock/get) | active | push2 | Eastmoney | eastmoney（confirmed） | 是 | confirmed | confirmed（2026-10-08） |
| 东财-push2_full | retired_duplicate → 东财-push2(stock/get) | push2_full | Eastmoney | eastmoney（confirmed） | 否 | confirmed | confirmed（2026-10-08） |
| 东财-push2ex | active | push2ex | Eastmoney | eastmoney（confirmed） | 是 | confirmed | confirmed（2026-10-08） |
| 东财-slist | active | slist | Eastmoney | eastmoney（confirmed） | 是 | confirmed | confirmed（2026-10-08） |
| 东财-ulist239(np/get) | active | ulist239 | Eastmoney | eastmoney（confirmed） | 是 | confirmed | confirmed（2026-10-08） |
| 东财-热榜(em_hot) | active | em_hot | Eastmoney | eastmoney（confirmed） | 是 | confirmed | confirmed（2026-10-08） |
| 东财-资金流(em_fund_flow) | active | em_fund_flow | Eastmoney | eastmoney（confirmed） | 是 | confirmed | confirmed（2026-10-08） |
| 同花顺-fuyao | active | fuyao | Tonghuashun | tonghuashun（confirmed） | 是 | confirmed | confirmed（2026-10-06） |
| 巨潮(cninfo) | active | cninfo | CNINFO | cninfo（confirmed） | 是 | unconfirmed | pending |
| 市场源(market_sources) | active | market_sources | 多源聚合 | 未确认（unconfirmed） | 否 | unconfirmed | pending |
| 开盘啦(kpl) | active | market_sources | 开盘啦 | 未确认（unconfirmed） | 否 | confirmed | confirmed（2026-10-08） |
| 开盘啦(kpl_limit_up_detail) | active | kpl | 开盘啦 | kpl（confirmed） | 是 | confirmed | confirmed（2026-10-08） |
| 开盘红 | active | kph | KPH / 开盘红（AxData source_code=kph） | kph（confirmed） | 是 | unconfirmed | pending |
| 新浪(hq.sinajs) | active | sina | Sina | sina（confirmed） | 是 | confirmed | confirmed（2026-10-08） |
| 新浪(扩展API) | active | sina_extended | Sina | sina（confirmed） | 是 | confirmed | confirmed（2026-10-08） |
| 沪深交易所 | active | exchange | 沪深交易所 | exchange（confirmed） | 是 | unconfirmed | pending |
| 百度(baidu) | pending_validation | baidu | Baidu | baidu（confirmed） | 是 | unconfirmed | pending |
| 腾讯(qt.gtimg) | active | tencent | Tencent | tencent（confirmed） | 是 | confirmed | confirmed（2026-10-08） |
| 财联社(cls) | active | cls | CLS | cls（confirmed） | 是 | confirmed | confirmed（2026-10-08） |

## 项目级历史参考基线

- [https://github.com/simonlin1212/a-stock-data](https://github.com/simonlin1212/a-stock-data) — earliest_project_reference；confirmed（2026-10-08）。用户确认该仓库是编写本项目时最早参考的项目仓库。此项是项目级历史参考基线，不代表任何单独采集源的上游提供方或当前实现来源。

## 仓库证据

### AxData

- 来源说明：AxData 是多提供方框架；本项目当前短线采集只调用 stock_shortline_indicators_tdx（通达信路径），不据此推定 AxData 其他接口的提供方或独立性。
- 对话确认：confirmed（2026-10-08）。按用户确认登记仓库关系；具体仓库的关系范围及限制见 repositories.note。
- [https://github.com/electkismet/AxData](https://github.com/electkismet/AxData) — runtime_package_repository；confirmed。确认这是 AxData 多提供方框架的运行时包仓库；本项目当前仅使用 stock_shortline_indicators_tdx，仓库关系不能推广到 AxData 的其他接口。
  - 项目内证据：requirements.txt, get_sht_report.py

### TDX(双命名源)

- 来源说明：通达信协议行情/财务客户端数据。
- 对话确认：confirmed（2026-10-06）。确认该仓库是本项目使用的 easy-tdx 运行时客户端 fork；上游数据提供方仍是通达信。
- [https://github.com/yanwei99521/easy-tdx](https://github.com/yanwei99521/easy-tdx) — runtime_client_fork；confirmed。requirements 固定到该仓库提交；本项目 tdx_client 使用 easy_tdx API。
  - 项目内证据：requirements.txt, docs/easy_tdx_repo_identity_check_20260916.md

### TDX-eltdx(适配层)

- 来源说明：ELTDX 是通达信协议客户端适配层，不作独立数据源计数。
- 对话确认：confirmed（2026-10-06）。确认该仓库对应 ELTDX 通达信协议客户端适配层；不将适配层视作独立行情提供方。
- [https://github.com/electkismet/eltdx](https://github.com/electkismet/eltdx) — runtime_client；confirmed。ELTDX 通达信协议 Python 客户端；仓库 README/pyproject 定义该项目能力。
  - 项目内证据：requirements.txt

### ZHB-tdxstat

- 来源说明：本地 ZHB 缓存中的 TDX tdxstat 数据。
- 对话确认：confirmed（2026-10-06）。仅确认 easy-tdx 是 ZHB tdxstat 缓存的下载/读取传输客户端；不代表它托管 ZHB 缓存或拥有 TDX 数据本体。
- [https://github.com/yanwei99521/easy-tdx](https://github.com/yanwei99521/easy-tdx) — cache_transport_client；confirmed。该客户端用于 ZHB 下载/读取路径；ZHB 数据本体是 TDX 缓存，不是此仓库托管。
  - 项目内证据：requirements.txt, docs/easy_tdx_repo_identity_check_20260916.md

### ZHB-tdxstat2

- 来源说明：本地 ZHB 缓存中的 TDX tdxstat2 数据。
- 对话确认：confirmed（2026-10-06）。仅确认 easy-tdx 是 ZHB tdxstat2 缓存的下载/读取传输客户端；不代表它托管 ZHB 缓存或拥有 TDX 数据本体。
- [https://github.com/yanwei99521/easy-tdx](https://github.com/yanwei99521/easy-tdx) — cache_transport_client；confirmed。该客户端用于 ZHB 下载/读取路径；ZHB 数据本体是 TDX 缓存，不是此仓库托管。
  - 项目内证据：requirements.txt, docs/easy_tdx_repo_identity_check_20260916.md

### ZHB-tipinfo

- 来源说明：本地 ZHB 缓存中的 TDX tipinfo 数据。
- 对话确认：confirmed（2026-10-06）。仅确认 easy-tdx 是 ZHB tipinfo 缓存的下载/读取传输客户端；不代表它托管 ZHB 缓存或拥有 TDX 数据本体。
- [https://github.com/yanwei99521/easy-tdx](https://github.com/yanwei99521/easy-tdx) — cache_transport_client；confirmed。该客户端用于 ZHB 下载/读取路径；ZHB 数据本体是 TDX 缓存，不是此仓库托管。
  - 项目内证据：requirements.txt, docs/easy_tdx_repo_identity_check_20260916.md

### FTShare

- 来源说明：服务接口来源身份；底层提供方族未逐工具确认，不能作为独立来源锚。。
- 对话确认：pending。已确认仓库是 FTShare MCP 文档/集成参考；用户尚未确认将其映射为底层独立数据提供方。
- [https://github.com/FTShare-Lab/FTShare-MCP](https://github.com/FTShare-Lab/FTShare-MCP) — hosted_service_documentation；confirmed。仓库提供 FTShare MCP 的文档/集成说明；服务由 market.ft.tech 托管，仓库不包含 MCP 服务端实现，也不证明每个工具底层数据源的独立性。
  - 项目内证据：stock_common/sc_ftshare.py, docs/verify/ftshare_fields_mirror.md

### Levistock历史未归属

- 来源说明：仅保留无法逐字段归属的历史证据；不是运行源，不映射到 FTShare，也不参与碰撞锚点。。
- 对话确认：confirmed（2026-10-06）。确认该仓库对应 levistock 多源客户端包装库；不将包装库视作独立数据提供方，也不据此确认每个字段的底层来源。项目字段中的历史混合键不再映射到 FTShare 运行源。
- [https://github.com/fleetinglife/levistock](https://github.com/fleetinglife/levistock) — multi_provider_client_wrapper；confirmed。Levistock 是多源客户端包装库。项目当前使用的 CLS 与 KPH 方法分别归入财联社、开盘红；FTShare 由项目自己的 MCP 客户端采集，不映射到 Levistock。
  - 项目内证据：docs/verify/levistock_field_verify.md, docs/levistock_source_reconciliation_20261010.md

### 开盘红(Levistock适配)

- 来源说明：与开盘红 KPH 来源记录属于同一来源族；Levistock 只作为客户端参考，不形成第二个独立锚。。
- 对话确认：confirmed（2026-10-06）。确认该仓库对应 levistock 多源客户端包装库；不将包装库视作独立数据提供方，也不据此确认每个字段的底层来源。项目字段中的历史混合键不再映射到 FTShare 运行源。
- [https://github.com/fleetinglife/levistock](https://github.com/fleetinglife/levistock) — client_wrapper_reference；confirmed。仅确认 Levistock 是 KPH 方法的客户端包装参考；Levistock 不作为独立提供方，KPH 来源族以 kph 运行时身份归组。
  - 项目内证据：docs/verify/levistock_field_verify.md, docs/levistock_source_reconciliation_20261010.md

### reports

- 来源说明：Eastmoney reportapi 原始响应。
- 对话确认：pending。截至 2026-10-08，用户未确认该来源的具体 GitHub 上游仓库；项目级早期参考基线另见 project_reference，不作为此来源的映射。
- GitHub 对应仓库：**unconfirmed**。现有材料不足以证明某个仓库就是本项目使用的采集实现；等待后续证据或用户确认。

### 东财-clist

- 来源说明：Eastmoney clist 原始响应。
- 对话确认：confirmed（2026-10-08）。按用户确认登记仓库关系；具体仓库的关系范围及限制见 repositories.note。
- [https://github.com/fleetinglife/levistock](https://github.com/fleetinglife/levistock) — provider_family_reference；confirmed。按用户确认作为 Eastmoney 来源族的客户端/接口参考；levistock 是多源包装库，不是底层数据提供方，也不据此断言本项目每个端点或字段均源自该仓库。
  - 项目内证据：scripts/capture_field_probe.py, stock_common/sc_datasource/_eastmoney.py

### 东财-datacenter(英文键)

- 来源说明：Eastmoney datacenter-web 原始响应。
- 对话确认：confirmed（2026-10-08）。按用户确认登记仓库关系；具体仓库的关系范围及限制见 repositories.note。
- [https://github.com/fleetinglife/levistock](https://github.com/fleetinglife/levistock) — provider_family_reference；confirmed。按用户确认作为 Eastmoney 来源族的客户端/接口参考；levistock 是多源包装库，不是底层数据提供方，也不据此断言本项目每个端点或字段均源自该仓库。
  - 项目内证据：scripts/capture_field_probe.py, stock_common/sc_datasource/_eastmoney.py

### 东财-em_kline_f61

- 来源说明：Eastmoney K 线接口原始响应。
- 对话确认：confirmed（2026-10-08）。按用户确认登记仓库关系；具体仓库的关系范围及限制见 repositories.note。
- [https://github.com/fleetinglife/levistock](https://github.com/fleetinglife/levistock) — provider_family_reference；confirmed。按用户确认作为 Eastmoney 来源族的客户端/接口参考；levistock 是多源包装库，不是底层数据提供方，也不据此断言本项目每个端点或字段均源自该仓库。
  - 项目内证据：scripts/capture_field_probe.py, stock_common/sc_datasource/_eastmoney.py

### 东财-push2(stock/get)

- 来源说明：单股行情 stock/get 的原始响应源。
- 对话确认：confirmed（2026-10-08）。按用户确认登记仓库关系；具体仓库的关系范围及限制见 repositories.note。
- [https://github.com/fleetinglife/levistock](https://github.com/fleetinglife/levistock) — provider_family_reference；confirmed。按用户确认作为 Eastmoney 来源族的客户端/接口参考；levistock 是多源包装库，不是底层数据提供方，也不据此断言本项目每个端点或字段均源自该仓库。
  - 项目内证据：scripts/capture_field_probe.py, stock_common/sc_datasource/_eastmoney.py

### 东财-push2_full

- 来源说明：仅保留旧 push2_full 原始快照的历史运行身份；该重复采集器已停用，不作独立碰撞锚。
- 对话确认：confirmed（2026-10-08）。按用户确认登记仓库关系；具体仓库的关系范围及限制见 repositories.note。
- [https://github.com/fleetinglife/levistock](https://github.com/fleetinglife/levistock) — provider_family_reference；confirmed。按用户确认作为 Eastmoney 来源族的客户端/接口参考；levistock 是多源包装库，不是底层数据提供方，也不据此断言本项目每个端点或字段均源自该仓库。
  - 项目内证据：scripts/capture_field_probe.py, stock_common/sc_datasource/_eastmoney.py

### 东财-push2ex

- 来源说明：Eastmoney push2ex 原始响应。
- 对话确认：confirmed（2026-10-08）。按用户确认登记仓库关系；具体仓库的关系范围及限制见 repositories.note。
- [https://github.com/fleetinglife/levistock](https://github.com/fleetinglife/levistock) — provider_family_reference；confirmed。按用户确认作为 Eastmoney 来源族的客户端/接口参考；levistock 是多源包装库，不是底层数据提供方，也不据此断言本项目每个端点或字段均源自该仓库。
  - 项目内证据：scripts/capture_field_probe.py, stock_common/sc_datasource/_eastmoney.py

### 东财-slist

- 来源说明：Eastmoney slist 原始响应。
- 对话确认：confirmed（2026-10-08）。按用户确认登记仓库关系；具体仓库的关系范围及限制见 repositories.note。
- [https://github.com/fleetinglife/levistock](https://github.com/fleetinglife/levistock) — provider_family_reference；confirmed。按用户确认作为 Eastmoney 来源族的客户端/接口参考；levistock 是多源包装库，不是底层数据提供方，也不据此断言本项目每个端点或字段均源自该仓库。
  - 项目内证据：scripts/capture_field_probe.py, stock_common/sc_datasource/_eastmoney.py

### 东财-ulist239(np/get)

- 来源说明：Eastmoney ulist.np/get 原始响应。
- 对话确认：confirmed（2026-10-08）。按用户确认登记仓库关系；具体仓库的关系范围及限制见 repositories.note。
- [https://github.com/fleetinglife/levistock](https://github.com/fleetinglife/levistock) — provider_family_reference；confirmed。按用户确认作为 Eastmoney 来源族的客户端/接口参考；levistock 是多源包装库，不是底层数据提供方，也不据此断言本项目每个端点或字段均源自该仓库。
  - 项目内证据：scripts/capture_field_probe.py, stock_common/sc_datasource/_eastmoney.py

### 东财-热榜(em_hot)

- 来源说明：Eastmoney 热榜接口原始响应。
- 对话确认：confirmed（2026-10-08）。按用户确认登记仓库关系；具体仓库的关系范围及限制见 repositories.note。
- [https://github.com/fleetinglife/levistock](https://github.com/fleetinglife/levistock) — provider_family_reference；confirmed。按用户确认作为 Eastmoney 来源族的客户端/接口参考；levistock 是多源包装库，不是底层数据提供方，也不据此断言本项目每个端点或字段均源自该仓库。
  - 项目内证据：scripts/capture_field_probe.py, stock_common/sc_datasource/_eastmoney.py

### 东财-资金流(em_fund_flow)

- 来源说明：Eastmoney 资金流接口；与其他 Eastmoney 接口按同一提供方计族。
- 对话确认：confirmed（2026-10-08）。按用户确认登记仓库关系；具体仓库的关系范围及限制见 repositories.note。
- [https://github.com/fleetinglife/levistock](https://github.com/fleetinglife/levistock) — provider_family_reference；confirmed。按用户确认作为 Eastmoney 来源族的客户端/接口参考；levistock 是多源包装库，不是底层数据提供方，也不据此断言本项目每个端点或字段均源自该仓库。
  - 项目内证据：scripts/capture_field_probe.py, stock_common/sc_datasource/_eastmoney.py

### 同花顺-fuyao

- 来源说明：同花顺 fuyao 官方 REST 服务。
- 对话确认：confirmed（2026-10-06）。确认该仓库对应同花顺 fuyao 官方 API 合约/客户端；确认范围不扩展为其他独立数据提供方。
- [https://github.com/HiThink-Tech/Financial-API](https://github.com/HiThink-Tech/Financial-API) — official_api_contract_and_client；confirmed。本地验证文档将其标注为同花顺官方仓库。
  - 项目内证据：docs/verify/fuyao_api_full.md

### 巨潮(cninfo)

- 来源说明：巨潮资讯官方披露数据。
- 对话确认：pending。截至 2026-10-08，用户未确认该来源的具体 GitHub 上游仓库；项目级早期参考基线另见 project_reference，不作为此来源的映射。
- GitHub 对应仓库：**unconfirmed**。现有材料不足以证明某个仓库就是本项目使用的采集实现；等待后续证据或用户确认。

### 市场源(market_sources)

- 来源说明：聚合多个接口，不作为独立来源锚点。
- 对话确认：pending。截至 2026-10-08，用户未确认该来源的具体 GitHub 上游仓库；项目级早期参考基线另见 project_reference，不作为此来源的映射。
- GitHub 对应仓库：**unconfirmed**。现有材料不足以证明某个仓库就是本项目使用的采集实现；等待后续证据或用户确认。

### 开盘啦(kpl)

- 来源说明：采集结果容器已知为 market_sources，但尚不能映射到独立原始数据源或字段路径。
- 对话确认：confirmed（2026-10-08）。按用户确认登记仓库关系；具体仓库的关系范围及限制见 repositories.note。
- [https://github.com/LowellLee/kpl](https://github.com/LowellLee/kpl) — parallel_api_reference；confirmed。按用户确认作为开盘啦/KPL 接口参考之一；与另一个并列确认仓库同时记录，当前证据不指定唯一代码来源。
  - 项目内证据：stock_common/sc_kpl.py, get_mak_report.py
- [https://github.com/Rainynitesky/kaipanla-data-parser](https://github.com/Rainynitesky/kaipanla-data-parser) — parallel_api_reference；confirmed。按用户确认作为开盘啦/KPL 接口参考之一；与另一个并列确认仓库同时记录，当前证据不指定唯一代码来源。
  - 项目内证据：stock_common/sc_kpl.py, get_mak_report.py

### 开盘啦(kpl_limit_up_detail)

- 来源说明：KPL 涨停个股明细独立 raw 文件；六个字段在 2026-09-29、09-30 与 KPH 样本逐值一致。。
- 对话确认：confirmed（2026-10-08）。按用户确认登记仓库关系；具体仓库的关系范围及限制见 repositories.note。
- [https://github.com/LowellLee/kpl](https://github.com/LowellLee/kpl) — parallel_api_reference；confirmed。按用户确认作为开盘啦/KPL 接口参考之一；与另一个并列确认仓库同时记录，当前证据不指定唯一代码来源。
  - 项目内证据：stock_common/sc_kpl.py, get_mak_report.py
- [https://github.com/Rainynitesky/kaipanla-data-parser](https://github.com/Rainynitesky/kaipanla-data-parser) — parallel_api_reference；confirmed。按用户确认作为开盘啦/KPL 接口参考之一；与另一个并列确认仓库同时记录，当前证据不指定唯一代码来源。
  - 项目内证据：stock_common/sc_kpl.py, get_mak_report.py

### 开盘红

- 来源说明：独立的 KPH 历史涨停接口；AxData 仅为请求框架，KPH 自身 GitHub 上游尚未确认。。
- 对话确认：pending。KPH 实际提供方由 AxData 接口目录与返回值确认；其上游 GitHub 仓库尚未与用户确认。
- [https://github.com/electkismet/AxData](https://github.com/electkismet/AxData) — runtime_client_framework；confirmed。用户确认的 AxData 框架仓库；该关系不代表 KPH 上游服务的仓库。
  - 项目内证据：requirements.txt, stock_common/sc_datasource/_axdata.py

### 新浪(hq.sinajs)

- 来源说明：新浪 hq.sinajs 行情响应。
- 对话确认：confirmed（2026-10-08）。按用户确认登记仓库关系；具体仓库的关系范围及限制见 repositories.note。
- [https://github.com/shidenggui/easyquotation](https://github.com/shidenggui/easyquotation) — realtime_quote_client_reference；confirmed。按用户确认作为新浪 hq.sinajs 实时行情客户端参考；不代表底层数据提供方或完整代码复制关系。
  - 项目内证据：scripts/capture_field_probe.py, stock_common/sc_schema.py

### 新浪(扩展API)

- 来源说明：新浪扩展 API；与新浪行情合并为同一提供方族。
- 对话确认：confirmed（2026-10-08）。按用户确认登记仓库关系；具体仓库的关系范围及限制见 repositories.note。
- [https://github.com/mpquant/Ashare](https://github.com/mpquant/Ashare) — historical_kline_reference；confirmed。按用户确认作为新浪扩展 API 中历史 K 线部分的参考；不扩展到该来源记录中的其他 API。
  - 项目内证据：scripts/capture_field_probe.py

### 沪深交易所

- 来源说明：交易所官方数据合并源。
- 对话确认：pending。截至 2026-10-08，用户未确认该来源的具体 GitHub 上游仓库；项目级早期参考基线另见 project_reference，不作为此来源的映射。
- GitHub 对应仓库：**unconfirmed**。现有材料不足以证明某个仓库就是本项目使用的采集实现；等待后续证据或用户确认。

### 百度(baidu)

- 来源说明：来源名可识别，但运行时字段路径仍须精确匹配。
- 对话确认：pending。截至 2026-10-08，用户未确认该来源的具体 GitHub 上游仓库；项目级早期参考基线另见 project_reference，不作为此来源的映射。
- GitHub 对应仓库：**unconfirmed**。现有材料不足以证明某个仓库就是本项目使用的采集实现；等待后续证据或用户确认。

### 腾讯(qt.gtimg)

- 来源说明：腾讯 qt.gtimg 行情响应。
- 对话确认：confirmed（2026-10-08）。按用户确认登记仓库关系；具体仓库的关系范围及限制见 repositories.note。
- [https://github.com/shidenggui/easyquotation](https://github.com/shidenggui/easyquotation) — realtime_quote_client_reference；confirmed。按用户确认作为腾讯 qt.gtimg 实时行情客户端参考；不代表底层数据提供方或完整代码复制关系。
  - 项目内证据：scripts/capture_field_probe.py, core/tdx_client.py

### 财联社(cls)

- 来源说明：财联社接口原始响应。
- 对话确认：confirmed（2026-10-08）。按用户确认登记仓库关系；具体仓库的关系范围及限制见 repositories.note。
- [https://github.com/fleetinglife/levistock](https://github.com/fleetinglife/levistock) — api_implementation_reference；confirmed。按用户确认作为财联社接口实现参考；levistock 为多源包装库，不据此确认独立数据提供方或本项目逐行复制关系。
  - 项目内证据：scripts/capture_field_probe.py, stock_common/sc_datasource/_eastmoney.py

## 解释口径

- GitHub 仓库可能是客户端、SDK、镜像或上游 API 契约仓库，不自动等同于数据提供方。
- `独立来源族` 用于碰撞证据去重；同一提供方的不同接口不能互相充当独立 L1 证据。
- `可作锚` 还要求字段状态 verified、含义/单位没有质量问题，且完整 code path 与运行时字段精确匹配。
- 未确认的来源族在默认碰撞中 fail closed；确认后更新 JSON 并重生成本页。
