# 2026-11-15 TDX XDXR 日期与类别字段核验

## 裁决对象

- `TDX(双命名源)::date`：确认是 XDXR 权息/股本变迁记录的事件日期；不等同采集日期。现有契约没有把它进一步限定为公告日、股权登记日或除权除息日。
- `TDX(双命名源)::category_name`：确认是 ELTDX `CapitalChangeRecord` 模型中事件类别的可读名称；不扩展类别码表。
- 两条裁决只确认各自来源路径，不建立跨源映射。

## 契约与代码路径

- 项目锁定 `eltdx==3.3.2`。对应版本的 [ELTDX 字段手册 §CapitalChangeRecord](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/FIELD_REFERENCE.md) 将 `date_raw / date` 列为“事件日期原始值 / 日期”，将 `category_raw / category / category_name` 列为“事件类别编号 / 类别名称”。该手册定义的是 ELTDX 解析后的客户端模型，不是 TDX 原始 wire 字段布局。
- `core/eltdx_adapter.py::_EltdxAdapter.xdxr` 从 `record.date`（缺失时回退 `date_raw`）生成输出 `date`；`core/tdx_client.py::tdx_get_dividend_history` 使用该日期筛选并输出 `category == 1` 的分红记录。
- 同一适配器读取 `category` 或 `category_raw`，当前没有把 `category_name` 转发到规范化 DataFrame。故 `category_name` 的裁决只确认 ELTDX 上游返回模型的字段角色，不表示每日采集已覆盖它。

## 官方业务语义旁证

- 通达信官方 [公式函数说明](https://help.tdx.com.cn/gspt/docs/markdown/redword/functionlist.html) 将 `SPLITBARS` 定义为“除权除息到现在的周期数”，并以当天发生除权作为 `0` 的示例；官方 [get_stock_info 字段表](https://help.tdx.com.cn/quant/docs/markdown/mindoc-1ctuhthaq5qmg/mindoc-1h10jj7r7jol4.html) 将 `TodayDRFlag` 定义为当天是否有除权除息。这支持 XDXR 日期属于公司行为事件日期域，但未进一步说明 `CapitalChangeRecord.date` 的具体日期子类型。
- 贵州茅台 [2025 年度权益分派实施公告](https://static.cninfo.com.cn/finalpage/2026-06-22/1225379934.PDF) 将 2026-06-25 标为股权登记日、2026-06-26 标为除权（息）日。该例说明这两类业务日期不同；本次没有把该公告日期与保留期 XDXR 原始行逐值配对。

## 样本覆盖和限制

- 按保留边界扫描了 2026-10-15 至 2026-11-12 的 18 个 `raw_eltdx.json` 归档；没有文件包含 `xdxr`、`capital_changes`、`category_name` 或 `CapitalChangeRecord` 路径。因此不声称有历史逐值碰撞、类别码表验证或来源日期验证。
- 通达信官方 [get_gb_info_by_date](https://help.tdx.com.cn/quant/docs/markdown/mindoc-1ctuhthaq5qmg/mindoc-1hc4303vsv1fk.html) 也包含名为 `Date` 的字段，样例为 `YYYYMMDD` 股本统计日期；但当前项目未找到将该函数响应映射到 `TDX(双命名源)::Date` 的代码路径。不能只凭同名把这一定义套到大写 `Date`，该字段继续待核。
- 日期字段的“事件日期”角色已核实，具体公告/登记/除权日类型、接口日期编码、事件类别码表及 `category_name` 的采集覆盖仍未核实。
