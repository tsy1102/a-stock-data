# 主字典拉丁字母字段名拆解审计

**审计日期：** 2026-10-14

**审计范围：** 当前工作区的 `docs/field_verification/field_registry.json`，覆盖全部来源路径中含拉丁字母的记录。
**完整逐路径清单：** [20261014_alphabetic_field_name_inventory.csv](20261014_alphabetic_field_name_inventory.csv)

## 结论

主字典方法论文档已经列出拼音、英文、缩写和中英混合的命名启发，但此前没有逐来源路径的覆盖清单，也没有强制把“词面拆解候选”与“真实字段语义”分开记录。本轮补上了全量清单和证据规则。

本轮确认了可从来源文档定名的 TDX 字段族，也复核了几个容易误判的拼音/混合字段。`lirunzonghe` 的字面拆音是“利润总和”，当前语义已按 TDX 字段定义和既有对撞证据订正为“利润总额”。其旧参考摘录保留“利润总和”作为历史记录，不能反向覆盖当前定案。

本轮没有把纯词面候选改成已验证字段。部分 TDX 登记只保存了来源和叶字段名，没有保存具体 API 方法；同名键在快照、集合竞价和财务接口中可能有不同语义。未补足方法级路径和数据证据前，批量写入释义或提升状态会把猜测带入主字典。

## 覆盖范围与命名形态

| 范围 | 数量 | 说明 |
|---|---:|---|
| 主字典去重字段 | 1,852 | 其中 1,764 个字段代码含拉丁字母 |
| 来源字段路径 | 2,481 | 其中 2,279 条代码或完整路径含拉丁字母 |
| 含字母且当前释义为空的来源路径 | 1,516 | 空释义不等于可由名字直接补齐 |
| 含字母 TDX 来源路径 | 305 | 其中 223 条当前释义为空 |
| `f数字` 序号键 | 483 | 需用接口文档、原始数据和跨源样本破解，字母/数字本身不说明语义 |
| 可识别的拼音短语候选 | 39 | 只表示命中本轮审计的拼音词表，不表示已确认 |
| 可识别的英文单词候选 | 150 | 仅供拆词；`amount`、`capital`、`turnover` 等仍受接口语境影响 |
| 可识别的英文短语候选 | 3 | 例如 `long_term_debt`；仍需确认来源和口径 |
| 未能可靠自动切分的连写标识符 | 254 | 可能是拼音、缩写、专有键或普通英文，保留原码待人工/来源核对 |
| 下划线分段/混合命名 | 985 | 包含英文、拼音、缩写及组合字段名 |
| 驼峰/混合大小写 | 156 | 例如 `FreeLtgb` |
| 全大写代码/缩写 | 134 | 缩写须结合源 schema 扩展 |
| 其他字母数字混合名 | 60 | 需按协议结构区分编号和词义 |
| 接口/嵌套路径 | 11 | 按完整路径和响应 schema 解析 |
| 疑似多字段拼接成单个 code 的 TDX 记录 | 2 | 见下文“结构性异常” |
| 样本/证券标识形态 | 2 | 不是字段语义，需从字段名审计中排除或重分类 |

名称形态计数按每条来源路径互斥分类；接口路径、样本标识、`f数字` 等不作为普通词语拆解。CSV 每行保留 `(source, path)`、原始 code、现有释义/状态、分词和“词面提示”。词面提示只帮助检索，不会写回注册表，也不参与锚点。

## 已确认的拆解与语义

### 拼音字段

| 字段名 | 词面拆解 | 当前语义/判断 | 证据与状态 |
|---|---|---|---|
| `liutongguben` | 流通 + 股本 | 流通股本 | 当前 registry 已验证；2026-10-14 对撞报告中与腾讯 `[72]/[76]` 连续 6 个交易日、120 组样本吻合，与 ulist `f39` 连续 3 个交易日、60 组样本吻合。 |
| `zongzichan` / `liudongzichan` / `gudingzichan` / `liudongfuzhai` | 总资产 / 流动资产 / 固定资产 / 流动负债 | 与当前已验证的财务释义一致 | registry 现有 TDX 财务记录已给出这些释义；不要把它们与其他接口的单位直接合并。 |
| `jinglirun` / `yingyelirun` / `weifenpeilirun` / `zibengongjijin` | 净利润 / 营业利润 / 未分配利润 / 资本公积金 | 与当前已验证释义一致 | registry 现有 TDX 财务记录。 |
| `lirunzonghe` | 利润 + 总 + 和（字面读法） | **利润总额**，不是利润总和 | registry 当前含义已订正；官方 TDX `FINANCE(28)` 定义为利润总额，项目既有本地 TDX/F10 与跨源对撞记录也支持该含义。[通达信公式函数表](https://help.tdx.com.cn/gspt/docs/markdown/redword/functionlist.html)；项目历史对撞证据见 [`field_source_reference.md`](../../field_source_reference.md) 与本日 finance adjudication。 |
| `faqirenfarengu` | 发起人 + 法人股 | 发起人法人股 | 当前 registry 已验证。相近拼法 `fajirenfarengu` 尚未验证，不能自动并成同一字段。 |

### 英文、缩写及混合字段

通达信官方量化文档直接列出多个字段名及含义。下表是“官方接口文档定义”，不是对所有项目路径的自动映射：

| 字段名 | 拆解提示 | 官方定义 | 需要保留的边界 |
|---|---|---|---|
| `fHSL` | `HSL` 为换手率缩写 | 换手率 | `f` 前缀不应脱离接口上下文另造含义 |
| `fLianB` | 拼音首段 | 量比 | 官方字段表给出定义 |
| `ZAF` / `OpenZAF` / `ZAFPre5` | 涨幅 / 开盘涨幅 / 前 5 日涨幅 | 涨幅、开盘涨幅、5 日涨幅 | `Pre` 的时间方向以官方字段表为准，不只按英文直译 |
| `Zsz` / `Ltsz` / `FreeLtgb` | 总市值 / 流通市值 / Free + 流通股本 | 总市值(亿) / 流通市值(亿) / 自由流通股本(万) | 单位也是字段契约的一部分 |
| `DynaPE` / `PB_MRQ` / `DYRatio` | Dynamic PE / PB + MRQ / dividend yield ratio | 动态市盈率 / 市净率(MRQ) / 股息率 | 缩写扩展须以官方表为准 |
| `MorePE` | PE 扩展值 | 港股为动态市盈率，其他扩展品种为静态市盈率 | **依证券类型而变，不能压成单一 PE 口径** |
| `Yield` | 英文常见词 | 债券为应计利息，回购为占款天数 | **依证券类型而变，不是统一收益率字段** |
| `ConZAFDateNum` / `EverZTCount` | 连续涨幅日期数 / 曾经涨停计数 | 连涨天数 / 连板天 | 官方字段说明优先于把 `Count` 按字面解释成“累计次数” |
| `LastStartZT` / `LastZTHzNum` | last/start/涨停/数量缩写 | 官方只写“几天”/“几板” | 当前定义不足以推出更精确的事件起点或统计窗口 |
| `KfEarnMoney` / `CashZJ` / `PreReceiveZJ` / `OtherQYJzc` | 拼音首字母 + 英文 | 扣非净利润 / 货币资金 / 合同负债 / 其他权益工具 | 英文或缩写直译不足以还原会计口径 |
| `PreMinum` | 疑似 `Premium` 拼写错误 | 基差/溢价 | 保留源字段原拼写；不能按拼写修正字段代码 |

来源：[通达信 `get_stock_info_batch` 字段表](https://help.tdx.com.cn/quant/docs/markdown/mindoc-1ctuhthaq5qmg/mindoc-1hlnuonsp0amo.html)、[通达信快照及 `get_more_info_batch` 字段表](https://help.tdx.com.cn/quant/docs/markdown/mindoc-1hjbidnohpjn4/mindoc-1hlir5r0t9hgc.html)。官方定义表也明确说明了 `J_jyxjl` 是经营现金净流量、`J_zxjl` 是总现金净流量；项目历史记录还区分 TDX 云 `CwInfo`（万元）与本地 `0x0010`（角）。这些代码、方法和单位不能仅因拼音近似而合并，详见 [`field_source_reference.md` §12.8.12i–j](../../field_source_reference.md)。

<a id="confirmed-lexical-findings"></a>

### 已有直接定义或项目证据的拼音/混合字段

| 字段 | 拆解与含义 | 证据 | 状态处理 |
|:---|:---|:---|:---|
| `vzangsu` | `v`（volume/量）+ `zangsu`（涨速）→ **量涨速**；与 `Zangsu`（价格涨速）区分 | 通达信官方快照字段表直接将 `vzangsu` 定义为“量涨速”；项目既有表头与样本核对也支持该含义 | 含义补入注册表；窗口口径未确认，状态仍为 `unverified` |
| `zhongguben` | 字面拼写含 `zhong`，但项目适配器把它映射自 `zong_gu_ben_raw_float`，语义为 **总股本** | [`core/eltdx_adapter.py`](../../../core/eltdx_adapter.py) 的字段映射；项目 2026-09-20 对撞记录显示乘以 10,000 后与东财总股本值精确一致 | 补入含义与 `万股` 单位；保留源键，不与 `zongguben` 合并；状态仍为 `unverified` |
| `fajirenfarengu` | 字段名的 `fajiren` 拼写不规范；适配器底层名 `fa_qi_ren_fa_ren_gu_raw_float` 可拆为 **发起人法人股** | [`core/eltdx_adapter.py`](../../../core/eltdx_adapter.py) 的逐字段映射 | 补入语义说明但保留原始键；来源值/单位仍待核，状态仍为 `unverified` |
| `fenhong` | **每股现金分红** | XDXR `category=1` 解码器把该值单独赋给 `fenhong`，并按每 10 股口径归一为每股值；字段映射文档列为每股分红 | 原注册表曾把它与 `peigujia` 合并写成一条；已拆分释义，状态仍为 `unverified` |
| `peigujia` | **配股价**，单位元/股 | XDXR `category=1` 解码器独立赋值；字段映射文档明确单位为元/股 | 原注册表曾与 `fenhong` 合并；已拆分释义，状态仍为 `unverified` |
| `songzhuangu` | **每股送转股比例** | XDXR `category=1` 解码器按每 10 股口径归一；字段映射文档明确是每股比例 | 原注册表曾与 `peigu` 合并；已拆分释义，状态仍为 `unverified` |
| `peigu` | **每股配股比例** | XDXR `category=1` 解码器按每 10 股口径归一；字段映射文档明确是每股比例 | 原注册表曾与 `songzhuangu` 合并；已拆分释义，状态仍为 `unverified` |

其中 XDXR 的四个字段现在按“分红金额、配股价格、送转比例、配股比例”分别记录，不能把相邻字段当作同义别名。项目登记的上游仓库 README 确认提供 `get_xdxr_info()`；逐字段解释由公开 easy-tdx 解码器/字段映射表交叉核对，并由另一份 TDX 协议实现复核。由于本项目当前记录没有精确到固定版本的解码代码路径，这四项仍不提升为碰撞锚。参考：[项目登记的 easy-tdx 仓库](https://github.com/yanwei99521/easy-tdx)、[XDXR 解码实现](https://github.com/handsomejustin/easy_tdx/blob/main/src/easy_tdx/commands/xdxr_info.py)、[XdxrRecord 字段映射](https://github.com/clong365/easy_tdx/blob/main/docs/field_mapping.md)、[另一份 TDX XDXR 协议实现](https://github.com/injoyai/tdx/blob/master/protocol/model_gbbq.go)。

## 同一 TDX 来源标签下的接口口径冲突

官方函数表、TDX 云 `get_stock_info_batch`、TDX 云 `CwInfo` 和本地 `0x0010` 是不同接口。下面的差异说明必须把“来源族”与“接口字段身份”分开：

| 字段/概念 | 项目本地 0x0010 记录 | 其他 TDX 官方接口说明 | 审计判断 |
|---|---|---|---|
| `jinglirun` | 本地字段表登记“净利润”，值单位为角；项目历史记录以 F10 数值复核 | 官方公式表 `FINANCE(30)` 行标题写“净利润”，说明文字写“归母净利润”；批量接口 `J_jly` 写“净利润” | 官方公式页自身文字不完全一致，且未证明 `jinglirun` 就是 `FINANCE(30)`。保留当前路径，不因名字自动改成“归母净利润”。 |
| `zhuyingshouru` | 本地字段表登记“主营业务收入”；历史样本与 F10 收入值核对 | 公式 `FINANCE(20)` 与批量键 `J_yysy` 写“营业收入” | 名称有会计术语精度差异。后续应按 0x0010 原始字段对照财报项目后，再决定主字典规范名是否改为“营业收入/营业总收入”。 |
| `jingyingxianjinliu` | 0x0010 登记“经营活动现金流” | `FINANCE(25)` 写“经营现金流量”；`J_jyxjl` 写“经营现金净流量” | 可能是方法/指标口径差异；不能仅按相似名称补“净额”。 |
| `zongxianjinliu` | 0x0010 登记“总现金流” | `FINANCE(26)` 写“总现金流量”；`J_zxjl` 写“现金及等价物净增加额” | 不同接口定义明显可能不同；不得把云 `CwInfo` 语义覆盖本地协议。 |

这四项目前没有被本轮改成新的已验证释义。特别是 `FINANCE(30)` 官方说明文本同时出现“净利润/归母净利润”两种说法；这是明确的上游文档歧义，需要方法级原始字段或报表项对照才能关闭。[通达信公式表](https://help.tdx.com.cn/gspt/docs/markdown/redword/functionlist.html)；[通达信批量基本信息字段表](https://help.tdx.com.cn/quant/docs/markdown/mindoc-1ctuhthaq5qmg/mindoc-1hlnuonsp0amo.html)。项目中 0x0010 的字段表、单位和样本证据见 [`field_source_reference.md` §零·C、§12.8.12i–j](../../field_source_reference.md)。

## 仍属候选的字段

下列字段名可产生合理猜测，但当前缺少足以提升为 verified 的来源路径或样本证据，故只留候选：

| 字段路径示例 | 拆解候选 | 当前处理 |
|---|---|---|
| `meigugongji` / `meiguweifenpei` | 每股公积金 / 每股未分配利润 | 词面可拆，但历史协议审计把这两个键列为旧文档误记，分别应由 `zibengongjijin / 10000`、`weifenpeilirun / 10000` 计算；不作为当前原始接口字段或别名，保留待治理记录 |
| `liudong_zichan` / `guding_zichan` / `liudong_fuzhai` / `zong_zichan` | 流动资产 / 固定资产 / 流动负债 / 总资产 | 与已验证拼音字段相似，但不同路径仍是独立记录，需证明它们是同一接口字段或规范化别名 |
| `jingying_xianjinliu` / `zong_xianjinliu` | 经营现金流 / 总现金流 | 需进一步确认净额、现金等价物和报表口径；不可直接套用近似拼音字段释义 |
| `shiyebianma` | 行业编码 | 历史协议审计指出它是旧文档错误键，实际协议字段为 `industry`；不把它当成可替换的别名 |
| `zhuyinglyrun` | 可能是 `zhuyinglirun` 的拼写变体 | 适配器把 `zhu_ying_li_run_raw_float` 输出成 `zhuyinglyrun`，历史样本又出现该键；同一语义还是独立原始键尚未裁定，需按接口路径确认后再决定修正映射 |
| `long_term_debt` / `short_term_debt` | 长期负债 / 短期负债 | 英文直译明确，但具体包含项、合计口径和来源仍需 schema/数值核验 |
| `turnover_pct` / `amplitude_pct` / `pe_lyr` / `vol_ratio` | 换手率 / 振幅 / 上年口径市盈率 / 量比 | 2026-10-14 碰撞报告只有单交易日候选；一天匹配不升状态 |

## 结构性异常与审查风险

1. TDX 来源下有两条 `code` 是多字段斜杠串，而非单字段：`gudongrenshu/zongzichan/.../industry` 与 `market/code/guojiagu/.../baoliu2`。它们来自历史聚合说明，不应作为一个可拆解字段。应先保留其历史证据，再在后续 registry 清理中迁移/拆分，避免直接删除时丢失原文。
2. 同花顺 `fund/...` 等斜杠字符串是合法接口路径；不能用“有斜杠”一刀切地标成坏字段。
3. `TDX(双命名源)` 当前覆盖 305 条路径，且 223 条含义为空；同一来源标签下混有多种 TDX API 和本地协议。下一轮应优先给路径补齐方法/接口层级，再利用已核验的命名和历史样本回填候选释义。
4. `f数字` 序号名、ZHB 列索引、枚举值和响应结构键不能靠拼音/英文规则破解；必须沿用各自的 schema、配置文件、值分布和跨源碰撞方法。
5. `reports`、KPL 等部分记录可能是样本值、协议类型或枚举，不是业务字段名。审计清单保留它们供分类复核，不把它们自动解释为字段。

## 与 2026-10-14 碰撞结果的衔接

### 历史采集数据复核

本次读取 2026-10-14 碰撞报告（有效交易日窗口为 2026-09-28、09-29、09-30、10-08、10-09、10-12、10-13），并检查本机保留的 2026-10-09 AxData/ELTDX/TDX/ZHB 样本。碰撞报告记录的是跨源配对统计；下表明确区分其覆盖范围，避免把一次命中误写成完整定案。

| 字段/候选 | 历史数据证据 | 本轮结论 |
|---|---|---|
| `tdx.finance_info.lirunzonghe` | 与 `ulist239.f44` 在 2026-09-28、09-30、10-08 三个不同交易日各有 20 只股票配对，共 60 组；每组均符合 `Ulist ≈ TDX × 0.1`。TDX 的角口径换算为 Ulist 元口径后吻合。碰撞报告生成时仍标记 `in_registry=false`；其后已通过 [`20261014_finance_fields.json`](../adjudications/20261014_finance_fields.json) 按完整来源路径审定。 | 数据支持“利润总额”，不是按字面拆出的“利润总和”。`ulist239.f44` 的证据不能推广到 `push2.f44`，后者仍是最高价；`f44` 不是跨接口全局身份。 |
| `zhongguben` | [2026-09-20 历史碰撞记录](../20260920_pinyin_verify.md)中，600519、601288 两只股票均满足 TDX `zhongguben × 10,000 = push2.f84`；2026-10-09 的 600519 样本又有 TDX `125008.15625` 与 ELTDX `shortline.float_shares=1250081562.5` 的 10,000 倍关系。 | 两个日期、三个来源路径样本支持“总股本”及 TDX 万股单位；其中 ELTDX 路径不能单独证明上游来源独立，且仍未达到项目完整多交易日确认窗口，状态保留 `unverified`。2026-10-09 抓取的 FTShare 股东变动记录实际公告/数据时间为 2018–2019 年，不能当作 2026 年总股本快照来反证或补证。 |
| `fajirenfarengu` | 同一 TDX 样本只观察到值 `45402960.0`；本地同股票样本没有独立来源的同口径字段可配对。 | 采集值本身不能证明字段语义。保留适配器映射给出的释义，但状态仍为 `unverified`。 |
| `pe_lyr` | TDX `quote_full.pe_lyr` 与 Tencent `[53]`、Ulist `f114` 在 2026-09-28 各有 20 组配对命中；与 push2 `f163` 有 10 组。另有 ZHB `stat.pe_lyr`、`full.pe_lyr` 与 Tencent `[53]` 的 20 股时间序列，覆盖 2026-09-29、09-30、10-09、10-12，报告的相关性中位数与符号一致率均为 1.0。 | 历史数据支持这些路径表达同一 PE 类数值；但“LYR”的具体财报期间口径仍需接口定义确认。TDX 行情路径的跨源证据只有 1 日，不提升其定案状态。 |
| `turnover_pct`、`amplitude_pct`、`vol_ratio` | 对应 TDX `quote_full` 与 Tencent/Ulist 各字段在 2026-09-28 各有 20 组配对命中；push2 每项有 10 组。报告窗口中的有效配对都集中在这一天。 | 数值支持换手率、振幅、量比这些拆解方向，但仅一天，不能满足多交易日确认要求；不提升状态。 |
| `fenhong`、`peigujia`、`songzhuangu`、`peigu` | 本次结构化原始采集样本中未发现这些 XDXR 键；检查的 2026-10-09 与 10-12 ZHB 压缩包各有 47 个条目，文件名中也未发现 `xdxr`/`gbbq` 事件数据入口。 | 现有行情缓存无法验证分红/配股事件字段。保留解码器和字段映射资料支持的拆分释义，四项仍为 `unverified`。 |
| `vzangsu` | 本次保留的结构化原始样本和项目快照中没有该键的历史数值。通达信官方快照字段表直接将其定义为“量涨速”。 | 字面含义有官方定义支撑；现有历史样本无法验证项目路径的具体计算窗口，状态仍为 `unverified`。 |
| `zhuyinglyrun` 及其他候选 | 2026-10-09 的 TDX 样本只出现 `zhuyinglyrun=94737620000.0`，没有独立来源的同股票、同日期字段作对照。其余候选在本轮结构化样本中没有可配对值。 | 单个原始值不足以确认字段含义；继续保留为待核候选。样本中未出现某键不构成该字段不存在的证明。 |

原始单点样本位于本机忽略目录 `.tmp/axdata_reconciliation_samples`，不纳入项目仓库；可复核的跨日统计见 [`20261014_collision_report.json`](20261014_collision_report.json) 及其 [Markdown 报告](20261014_collision_report.md)。本轮没有因单点数值修改字段状态或新增碰撞锚。

对候选的后续处理仍按来源路径区分，并要求满足现行来源独立性、不同交易日数和样本量规则，再通过 adjudication 同步 registry；不得把本 CSV 或单日命中直接当作定案输入。

## 后续执行顺序

1. 优先处理 223 条 TDX 空释义记录：补全具体 API 方法路径；有官方接口文档且方法完全对应的记录，再通过正式 adjudication 写入释义/证据。
2. 对拼音候选先做全量别名关系对照，重点是下划线与连写变体、错拼近邻、同一接口不同字段路径。
3. 对 English/mixed 候选逐源查 schema，特别检查单位、会计定义、统计窗口和证券类型条件。
4. 对 `f数字` 与无语义缩写继续依赖交易日数据和来源独立锚；命名分析只提供搜索方向。
