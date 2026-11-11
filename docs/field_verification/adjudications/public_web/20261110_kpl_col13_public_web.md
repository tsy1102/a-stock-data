# 2026-11-10 KPL col_13 公共资料核查

## 核查结论

没有找到开盘啦公开的 `DailyLimitPerformance` 字段合同。公开产品页能确认其界面展示“实际流通”，但没有说明原始数组索引、单位或股本基数。第三方逆向接口说明把 `DailyLimitPerformance` 返回数组中成交额后的下一数值标为“实际流通”，再下一数值标为“实际换手”；这与本项目 `raw_columns.col_13`、`raw_columns.col_14` 的相邻位置一致，但该说明不是开盘啦官方接口合同。

Tushare 的开盘啦榜单文档另将 `free_float` 标为“实际流通”，并把 `amount` 与 `turnover_rate` 分列；文档没有给出 `free_float` 单位，也不能单独证明本项目私有接口的字段定义。单位判断因此还需本地样本核验。

## 资料

- 开盘啦官方产品页：[开盘啦首页](https://www.kaipanla.com/page)，“市场风口”表格列出“实际流通”。
- 第三方接口逆向说明：[KPL 接口说明](https://github.com/LowellLee/kpl/blob/master/KPL%E6%8E%A5%E5%8F%A3.md#L1422-L1449)，历史涨停返回示例中成交额之后是“实际流通”，随后为“实际换手”。这只支持字段位置与展示名，不视为官方契约。
- Tushare 开盘啦榜单文档：[榜单数据（开盘啦）](https://github.com/waditu/tushare-skill/blob/master/references/%E6%95%B0%E6%8D%AE%E6%8E%A5%E5%8F%A3/%E8%82%A1%E7%A5%A8%E6%95%B0%E6%8D%AE/%E6%89%93%E6%9D%BF%E4%B8%93%E9%A2%98%E6%95%B0%E6%8D%AE/%E6%A6%9C%E5%8D%95%E6%95%B0%E6%8D%AE%EF%BC%88%E5%BC%80%E7%9B%98%E5%95%A6%EF%BC%89.md#L190-L216)，将 `free_float` 标作“实际流通”；`amount`、`turnover_rate` 是相邻字段。

## 限制

以上公开资料只能确认产品标签和第三方记录的位置关系。它们没有说明开盘啦“实际流通”的股本基数、计算公式或与证券行情常用“流通市值”的等价关系，也没有覆盖本项目使用的 `DailyLimitPerformance` 私有接口版本。因此报告中的单位和含义结论依赖另行保存的保留期样本审计；不建立到东方财富 `circulating_value` 的跨源映射。
