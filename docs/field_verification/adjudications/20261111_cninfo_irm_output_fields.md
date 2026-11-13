# 巨潮互动易采集输出字段语义定案

日期：2026-11-11

范围：`巨潮(cninfo)` 的 `cninfo_irm` 采集结果字段。此记录确认本项目适配器输出字段的来源内语义，不声明巨潮未公开 API 的完整契约，不建立跨源 `mappings`。

## 定案

`stock_common/sc_datasource/_holders.py::cninfo_irm` 将互动易问答响应中的字段映射为六个采集输出字段。官方互动易页面按上市公司展示股票代码/简称、投资者问题、上市公司回复和记录时间；深交所官方投资者服务页也将互动易列为投资者与上市公司在线沟通平台。适配器映射、保留期样本和官方页面相互吻合，足以确认以下六个精确 `(source, code)` 路径的来源内语义：

| 输出路径 | 上游响应字段 | 定案含义 | 单位/缺值 |
|---|---|---|---|
| `巨潮(cninfo)::code` | `stockCode` | 问答所属的六位股票代码 | 六位字符串；有效记录不缺失 |
| `巨潮(cninfo)::company` | `companyShortName` | 问答所属上市公司的简称 | 文本；有效记录不缺失 |
| `巨潮(cninfo)::question` | `mainContent` | 投资者提出的问题正文 | 文本；有效记录不缺失 |
| `巨潮(cninfo)::answer` | `attachedContent` | 上市公司对该问题的回复正文 | 文本；尚无回复时为空 |
| `巨潮(cninfo)::answerer` | `attachedAuthor` | 回复记录标注的答复主体/作者 | 文本；尚无回复时为空，不据此推断自然人身份 |
| `巨潮(cninfo)::ask_time` | `pubDate` | 问答记录的发布时间戳 | Unix 毫秒转换为本机本地时区的 `%Y-%m-%d %H:%M` 字符串，精度到分钟；不是采集目录日期 |

其中 `answer` 与 `answerer` 在未答复记录中同时为空。这是问答状态，不是字段定义缺失。

## 路径和样本核验

适配器先用 `queryKeyboardInfo` 查询 `secid`，再用 `company/question` 获取问答行；六个输出键及上游字段的映射均在 `cninfo_irm` 中逐项赋值。历史字段协议参考也列有对应关系，可作旁证；该历史表不单独替代当前运行代码和原始样本。

核验了保留期内 17 个目录的 `raw_cninfo.json`：2026-10-15 文件为空，随后 16 个采集日共 1,219 条原始记录。按请求股票键与响应 `code` 精确相等筛选后，得到 1,059 条有效记录，覆盖 10 只股票。有效记录中 `code`、`company`、`question`、`ask_time` 各 1,059 条非空；`answer` 和 `answerer` 各 932 条非空，另有 127 条两者同时为空。十个股票代码各自只对应一个 `company`，没有空问题，也没有 `answer` / `answerer` 单边缺失。

原始记录中另有 160 条错桶记录，全部挂在请求键 `920508` 下，但行内 `code` 属于其他股票、公司简称也与殷图网联不符。旧实现会在模糊检索未精确命中时接受唯一的模糊候选，导致把其他股票的问答放进 `920508` 桶。这 160 条不作为 `920508` 的样本，也不作为本次语义判定的逐股证据；历史 raw 文件保持原样。当前实现只接受检索结果中的精确代码，并在写出前再次过滤响应行代码不匹配项；测试覆盖模糊单结果拒绝和响应错码过滤。

各采集目录文件 SHA-256（原始文件未修改）：

```text
20261015 ea9e5f12543edd5a8da4a5417858aff5b8e6465a3b161b25f28be4755f673dad
20261016 61b43c96f9b3afb99418fd28bcef3b839276f950e0aa2178716df49b7fb0a22a
20261019 f2c314c67e0b4aff503565ec2b5a2409383d4c670bb09b91904198a097ca69ec
20261020 780c18cbe6c261c0d14ca0df090e3d833d6ba9263b544a0c1084205a537363f7
20261021 2bf2d68c9ba5319bcb9ce6d1545393856273645fb392b7aa19354816b06e9b88
20261023 02c98c76cb8627ce0e0379acba65ec599cfb9dd5ff37f4aa6e60bed1e85b5b89
20261026 88ed85c41e886dbd228351bbed3de36c46da16e8273de583f52da7c5b0ec4cce
20261028 306727f2a7af3fd4c2f7d60a539775f64535ef694843eb55d4dcaae5b08d89c7
20261029 11f2d21abc889a979725986ef96165e3aa2c90c62132d6c99cd8af0866124da4
20261030 d9ea44e68de1bfa52a91d2ec7591dc98b843d7ff68887cc723a1753601625e9b
20261102 f19da504d14981f6ee18eb4748775f886a96349094e6cd362b0f386ccac6d7b7
20261103 4cfdc2d10f6cb356a4f9331f42e782dfb287bca693b8273fabe6d1056d9bbbde
20261104 1e551b616f8f8dbf9790ada7f76bd4d473f890f2e935e9695c36c738ca664a9b
20261105 286864369c54bd51c5f33219ca7c3c410625708e6e453188db354f28535dc639
20261106 60913f9a9c1df08d03b5c92667c8bea228adb0bf0dd787e44fa166b9496a2636
20261109 b8647d20c37d588b9d15527d26937b2bfab44f6bc509acf39df65cd18c7f4d7c
20261110 9480659e0ad7fe8ecd504e7f68f7a1cb4b2fdf78c44985d5ea7f3526d7246def
```

## 官方资料和边界

- [深交所互动易](https://irm.cninfo.com.cn/newircs/) 当前页面展示问答记录中的公司简称/代码、问题正文、公司回复和记录时间；页面访问时间仅用于核对显示形态，不替代历史样本时间。
- [深交所投资者服务平台说明](https://www.szse.cn/marketServices/investor/) 将互动易列为投资者与上市公司在线互动沟通平台。
- [历史字段来源参考](../../field_source_reference.md) §12.8.15 曾列出 `stockCode`、`companyShortName`、`mainContent`、`attachedContent`、`attachedAuthor` 和 `pubDate` 的对应关系；作为历史旁证，不主张它是当前接口版本契约。

本结论仅限当前 `cninfo_irm` 输出路径和已核样本。它不扩展到注册表中同名的公告字段 `date`、`title`、`type`、`url`；这些字段不在当前问答输出中，仍需针对各自公告接口核验。它也不证明其他来源的同名字段等价或其来源独立性。
