# Eastmoney IPO `LATELY_PRICE` 与 `CLOSE_PRICE` 定案

复核日期：2026-11-20

## 定案

- `东财-event_dc(IPO发行记录)::ipo_calendar[].LATELY_PRICE`：东方财富新股申购页所列的该证券**最新价**。采集响应没有给出此价格自身的 `as_of_date`，不能把它自动解释为目录目标数据日的收盘价。
- `东财-event_dc(IPO发行记录)::ipo_calendar[].CLOSE_PRICE`：该证券**上市首日收盘价**，不是当前最新价或发行价。

仅定案以上两个完整来源路径，不创建跨源映射。两字段单位均暂留空：官方模板使用“最新价”“首日收盘价”标签并把值格式化到两位小数，但没有在该表格模板中明确币种/单位。不得用 `UP_DATE` 或文件夹日期代替 `LATELY_PRICE` 的实际行情日期。

## 官方字段标签与采集路径

项目 [`_events.py`](../../../stock_common/sc_datasource/_events.py) 将 `ipo_calendar` 请求映射到东方财富 DataCenter `RPTA_APP_IPOAPPLY`，并把响应行保存到 `raw_event_dc.ipo_calendar[]`。东方财富[新股申购数据页](https://datapc.eastmoney.com/da/Purchase/Index)的官方模板将 `item.LATELY_PRICE` 绑定到“最新价”，将 `item.CLOSE_PRICE` 绑定到“首日收盘价”；两者以 `precision(1,2)` 显示。页面没有发布带版本号的字段 schema，本次于 2026-11-20 实际核对当前模板。

```text
_events.py::_EM_REPORTS['ipo_calendar']
  -> RPTA_APP_IPOAPPLY response.data[*].LATELY_PRICE
  -> ipo_calendar()
  -> raw_event_dc.ipo_calendar[].LATELY_PRICE

_events.py::_EM_REPORTS['ipo_calendar']
  -> RPTA_APP_IPOAPPLY response.data[*].CLOSE_PRICE
  -> ipo_calendar()
  -> raw_event_dc.ipo_calendar[].CLOSE_PRICE
```

## 留存样本核对与边界

样本来自 `docs/field_verification/20261119/raw_event_dc.json`：20 条 IPO 发行记录中，`LATELY_PRICE` 与 `CLOSE_PRICE` 各为 20/20 非空、数值互异。`CLOSE_PRICE` 的角色由官方“首日收盘价”列标签定义；其日期角色是上市事件字段，不能按当前行情快照处理。

`LATELY_PRICE` 的语义仅定为官方页面的“最新价”列。响应中的 `UP_DATE` 是同一 IPO 记录的更新字段，不足以证明报价恰好对应 `UP_DATE` 当日；本批没有字段级报价日期，也没有把它作为当前采集目标数据日的历史收盘价。日频跨源碰撞或定案须先取得双方可对齐的实际行情日期。

同批样本中 `TNEW_PRICE` 与 `LATELY_PRICE` 20/20 数值相等，但东方财富当前页面模板未把 `TNEW_PRICE` 绑定到展示列；因此仅记录为同响应内相等观察，不把它登记成别名或同义路径。`NEWEST_PRICE` 虽出现在另一张官方模板中并绑定“最新价”，当前 20 条原始响应却 0/20 有值；不把空值当成零，也不据此注册有观测值的字段。

原始 `raw_event_dc.json` SHA-256：`41fe019b29d038e1cf4726f69700af303aae0206a6fdb8d7399912290065b091`。20 条记录来自同一响应，不按 20 个独立报价日期计数。
