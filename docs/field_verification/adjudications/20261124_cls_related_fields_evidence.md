# 财联社电报关联证券与主题字段实证

复核日期：2026-11-24。此次只读取保留样本并浏览财联社、上交所公开页面，没有调用采集器或请求采集 API。

## 裁决范围

- `财联社(cls)::stock_list` 是财联社电报条目上游附加的关联证券列表。确认列表项中的证券代码与名称用于标识文章关联证券。空列表仅表示该条记录没有返回关联项，不据此断言正文未提及证券。
- `财联社(cls)::subjects` 是电报条目关联的主题/题材标签列表。确认列表项的 ID 与名称对应财联社官方文章详情页上的主题链接。
- 不建立跨来源映射，也不推断 CLS 与其他新闻源字段同义。
- `stock_list[]` 的 `pct` 由项目适配器从上游 `RiseRange` 映射而来，但它的单位、来源实际数据时点及是否按文章发布时间固定尚未核实；这部分不纳入本次定案。

## 项目字段路径

项目 [`_eastmoney.py`](../../../stock_common/sc_datasource/_eastmoney.py) 的 `cls_telegraph()` 调用财联社 `/v1/roll/get_roll_list`，把响应 `data.roll_data[*].stock_list` 归一化为 `raw_cls.json.telegraph[*].stock_list[*].{code,name,pct}`：`StockID` / `stock_code` 映射到 `code`，`name` / `stock_name` 映射到 `name`，`RiseRange` 映射到 `pct`。响应 `subjects` 归一化为 `raw_cls.json.telegraph[*].subjects[*].{id,name}`：`subject_id` 映射到 `id`，`subject_name` 映射到 `name`。

归档文件是适配器归一化后的采集记录，不是未经处理的线缆响应。字段身份按财联社电报记录中的完整属性路径判断。

## 保留样本覆盖

按照 `scripts/capture_retention.py` 的保留边界，只审计 2026-10-15 至 2026-11-19 的归档：

- 22 个 `raw_cls.json` 文件、1,050 条电报记录；对应来源状态均为 `ok`。
- 150 条记录含非空 `stock_list`，共 198 个证券项；198 项均有非空代码、名称和数值型 `pct`。
- 893 条记录含非空 `subjects`，共 1,537 个标签项；1,537 项均有 ID 和名称。
- 以上多日统计用于检查归一化结构是否稳定；公开网页逐值核对的样本另列如下，不把结构完整率冒充为对所有文章的外部逐条验证。

## 官方页面逐值核对

2026-11-19 归档记录包含以下电报：

- 记录时间：`2026-11-19 15:24:29`；正文为“频准激光：半导体检测光源客户验证与放量正在逐步推进”。
- `stock_list`：`[{"code":"sh688826","name":"频准激光","pct":-7.4199996}]`。
- `subjects`：`[{"id":1279,"name":"半导体芯片"},{"id":2710,"name":"激光"}]`。

同一篇[财联社官方文章](https://api3.cls.cn/share/article/2538923?app=&os=CailianpressWeb&sv=829)包含相同标题、正文和发布时间，并在文章下展示“频准激光”证券关联项及“半导体芯片”“激光”两个主题链接。[上交所上市公告](https://www.sse.com.cn/disclosure/announcement/listing/ipo/c/c_20260817_10829108.shtml)确认证券代码 `688826` 的简称为“频准激光”；财联社官方的[主题 ID 1279 页面](https://api3.cls.cn/share/subject/1279?os=ios&sv=864)和[主题 ID 2710 页面](https://api3.cls.cn/share/subject/2710?os=CailianpressWeb&sv=840)均列出同一篇文章。该例逐项支持关联证券、证券代码/名称以及主题 ID/名称的解释。

网页显示的行情会变化：本次打开的官方文章页显示该证券 `-6.96%`，而该条归档记录的 `pct` 是 `-7.4199996`；较早的官方搜索索引快照曾显示 `-7.42%`。因此，不能把当前文章页上的涨跌幅当作 2026-11-19 的历史值，也不能仅凭这个页面确定 `pct` 的时点口径。本次只裁决 `stock_list` 的证券关联与代码/名称身份。

## 文件指纹

- 归档样本：`docs/field_verification/20261119/raw_cls.json`，SHA-256 `fb3580916b59cba78b951d694e043e65c86b9011ad1ff718a2560b882ab0c738`。
- 采集元数据：`docs/field_verification/20261119/meta.json`，SHA-256 `c33dd40b7f340d0009987b4889f421c6bef8cf543f91b5caff0ce3501f07fe7f`。
- 该来源的采集开始时间为 `2026-11-19 15:30:20`，市场阶段为 `closed`，状态为 `ok`；本裁决比较的是文章关联字段，不用采集目录名替代任何来源日期或行情时点。
