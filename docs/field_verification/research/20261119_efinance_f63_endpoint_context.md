# efinance 中 `f63` 的接口路径核对

本轮复核 Ulist `f63` 时，核对了公开仓库 [Micro-sheep/efinance](https://github.com/Micro-sheep/efinance) 的字段映射，避免把相同数字代码跨接口误认为同一字段。

- efinance 的 `EASTMONEY_HISTORY_BILL_FIELDS` 把 `f63` 标为“涨跌幅”；同一个 `get_history_bill` 函数实际请求 `/api/qt/stock/fflow/daykline/get`，见[字段表](https://github.com/Micro-sheep/efinance/blob/main/efinance/common/config.py#L140-L154)及[请求实现](https://github.com/Micro-sheep/efinance/blob/main/efinance/common/getter.py#L1913-L1942)。
- efinance 的 `EASTMONEY_QUOTE_FIELDS` 用于 `/api/qt/ulist.np/get`，包含报价字段、更新时间和最新交易日，但没有 `f63`，见[报价字段表](https://github.com/Micro-sheep/efinance/blob/main/efinance/common/config.py#L117-L138)及[Ulist 请求实现](https://github.com/Micro-sheep/efinance/blob/main/efinance/common/getter.py#L2218-L2249)。

因此，仓库里的 `f63 → 涨跌幅` 是**另一个接口**的字段定义；它不能转移到本项目精确身份 `东财-ulist239(np/get)::f63`。这是对 efinance 代码实际采用字段映射的描述，不是东方财富官方字段契约，也不能解释本项目 Ulist `f63` 的语义。当前 Ulist `f63` 仍保持含义和单位未知。
