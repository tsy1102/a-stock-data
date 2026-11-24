# 巨潮公告日期、标题与旧 URL 路径核验

审计日期：2026-11-24。范围为 `巨潮(cninfo)::date/title/type/url`，只裁定实际运行路径，不建立跨来源映射。

## 当前运行路径

`stock_common/sc_datasource/_holders.py::get_strategic_announcements()` 向巨潮官方 `POST /new/hisAnnouncement/query` 查询公告：

- `announcementTitle` 清理 HTML 标签后输出到 `title`。
- `announcementTime` 按项目本地时区转换为 `YYYY-MM-DD` 后输出到 `date`。
- `announcementTypeName` 输出到 `type`；为空时输出空字符串。
- `announcementId` 输出到 `announcement_id`，`adjunctUrl` 输出到 `adjunct_url`。旧字段参考中将 `announcementId` 写成 `url`，但它是公告标识符；PDF 相对路径来自另一个键 `adjunctUrl`。

## 官方响应与页面核对

2026-11-24 16:14:53（北京时间）以一个受限请求查询证券 `600449` 的 30 条最新公告。官方响应归档见 [`response sample`](public_web/20261124_cninfo_announcement_response_sample.json)，规范 LF SHA-256：`cdc3ca85ed1186fc52ad9b176de9c3e3eb89e5f9e101bdc5d7bc99756ae0eb50`。

返回的宁夏建材第一条记录为标题“宁夏建材关于召开2026年第四次临时股东会的通知”，`announcementTime=1795536000000`、`announcementId=1225685351`、`adjunctUrl=finalpage/2026-11-25/1225685351.PDF`。按项目本地时区转换，该时间戳为 `2026-11-25 00:00:00 +08:00`。巨潮[官方首页](https://www.cninfo.com.cn/new/index.jsp)同一公告行显示该代码、简称、公告标题和日期 `11-25`，因此页面日期与采集器输出日期吻合。

注意：保留期内 `raw_cninfo.json` 由 `collect_cninfo()` 保存 `cninfo_irm()` 的互动易问答，不包含 `get_strategic_announcements()` 的报告输出。它们不作为该公告 helper 的“url 缺失”阴性样本。本次旧路径处置依据当前解析器返回结构、同一官方响应字段和新增离线回归测试；缺少该 helper 的历史原始输出已作为证据边界记录。

## 裁决

1. `巨潮(cninfo)::title` 定义为巨潮公告标题文本（项目移除标题中的 HTML 标签后输出）。该完整路径可追溯到官方响应键 `announcementTitle`，与官方页面公告标题逐字相同，按来源契约核验。
2. `巨潮(cninfo)::date` 定义为公告日期：官方响应键 `announcementTime` 的毫秒时间戳，经项目按本地时区转换成 `YYYY-MM-DD`。该公告的输出日期与巨潮官方首页日期一致，按来源契约核验。它不是采集目录日期。
3. `巨潮(cninfo)::type` 暂不定案：30 条官方响应的 `announcementTypeName` 均为空，仅 `announcementType` 有编码值。空值无法验证名称含义或类别代码表；保持未知，待官方字段表或非空样本出现后再继续。
4. `巨潮(cninfo)::url` 是过时项目别名，不是当前解析器输出路径。旧参考表把 `announcementId` 错列为 `url`；当前解析器分别输出 `announcement_id` 和 `adjunct_url`。本次以 `retired_legacy_path` 退出该旧路径，保留原始历史记录；不把 ID 解释为 URL，也不把 ID 和 PDF 相对路径合并。

本次官方响应只用于字段定义和路径复核，不是项目日常采集，也没有运行采集器。注册表裁决与输出路径回归测试见同批文件。
