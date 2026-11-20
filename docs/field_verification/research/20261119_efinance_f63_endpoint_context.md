# efinance 中 `f63` 的接口路径核对

本轮复核 Ulist `f63` 时，核对了公开仓库 [Micro-sheep/efinance](https://github.com/Micro-sheep/efinance) 的字段映射，避免把相同数字代码跨接口误认为同一字段。

- efinance 的 `EASTMONEY_HISTORY_BILL_FIELDS` 把 `f63` 标为“涨跌幅”；同一个 `get_history_bill` 函数实际请求 `/api/qt/stock/fflow/daykline/get`，见[字段表](https://github.com/Micro-sheep/efinance/blob/main/efinance/common/config.py#L140-L154)及[请求实现](https://github.com/Micro-sheep/efinance/blob/main/efinance/common/getter.py#L1913-L1942)。
- efinance 的 `EASTMONEY_QUOTE_FIELDS` 用于 `/api/qt/ulist.np/get`，包含报价字段、更新时间和最新交易日，但没有 `f63`，见[报价字段表](https://github.com/Micro-sheep/efinance/blob/main/efinance/common/config.py#L117-L138)及[Ulist 请求实现](https://github.com/Micro-sheep/efinance/blob/main/efinance/common/getter.py#L2218-L2249)。

因此，仓库里的 `f63 → 涨跌幅` 是**另一个接口**的字段定义；它不能转移到本项目精确身份 `东财-ulist239(np/get)::f63`。这是对 efinance 代码实际采用字段映射的描述，不是东方财富官方字段契约，也不能解释本项目 Ulist `f63` 的语义。当前 Ulist `f63` 仍保持含义和单位未知。

## 东方财富官方前端的路径交叉核验（2026-11-20）

东方财富官方[个股资金流页面](https://data.eastmoney.com/zjlx/600519.html)加载的 [`stock.js`](https://data.eastmoney.com/newstatic/js/zjlx/stock.js) 进一步显示字段码必须连同接口路径解释：

- `getnumdata()` 调用 `/api/qt/ulist.np/get`，请求 `f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,...`，没有请求 `f63`。同一脚本的资金流字段映射将 `f62` 映射为页面主力净流入 `zlje`，未给 Ulist `f63` 建立名称映射。因此此官方资金流页面实现没有提供 `ulist.np/get::f63` 的定义。
- 页面另用 `getdkdata()` 调用 `/api/qt/stock/fflow/daykline/get`，请求连续字段 `f51`–`f65`。其 `loadlstable()` 将返回行的第 12 个值（零基索引 `arr[11]`）显示为收盘价，将第 13 个值（`arr[12]`）显示为涨跌幅。按请求字段顺序对应，**这个不同接口**的 `f63` 是涨跌幅。
- 对该日线接口读取 600519 的 2026-11-20 行，15 个返回值中第 12、13 项为 `1485.75`、`1.75`；东方财富页面同日历史表显示收盘价 `1485.75`、涨跌幅 `1.75%`。这核实了 `daykline::f63` 的列位，不把它转用为 Ulist 字段定义。
- 另以 `beg=20261118&end=20261119` 查询官方 1 分钟 K 线接口时，响应返回 240 行且日期均为 2026-11-20，没有提供 11 月 18 日的开盘分钟记录。本次结果不能检验 Ulist `f63` 是否等于 11 月 18 日 09:25 竞价值；因此不作为对“竞价相关”候选的支持或反证。

综上，官方实现再次确认了 `f63` 是**接口路径限定的编号**，且目前未发现官方前端对 `东财-ulist239(np/get)::f63` 的字段名、单位或业务定义。`ulist239.f63` 继续保持未知；不更新 registry、主字典或 mappings，也不把其他接口的 `f63 → 涨跌幅` 迁入 Ulist 路径。
