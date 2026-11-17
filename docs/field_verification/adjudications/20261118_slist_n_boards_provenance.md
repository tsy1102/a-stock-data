# 东方财富 slist `n_boards` 来源路径裁决

复核日期：2026-11-18。未运行采集。本次只核查 `东财-slist::n_boards` 的项目输出血缘，不为 Eastmoney `slist/get` 推断未公开的业务字段定义，也不建立跨源映射。

## 裁决

碰撞报告中的 `slist.n_boards` 是项目派生的板块列表条目数，不是 Eastmoney 响应字段。将精确来源身份 `东财-slist::n_boards` 登记为 `disproved` / `project_derived_capture_output`，从未知上游字段队列退出。这里的 `disproved` 只否定“这是提供方原始字段”的身份；项目输出的计数本身仍可供分析使用。

## 代码链

- [`collect_slist()`](../../../scripts/capture_http_collectors.py) 请求 `https://push2delay.eastmoney.com/api/qt/slist/get`（失败时回退 `push2.eastmoney.com`），读取响应 `data.diff`；若它是对象则转为列表。
- 成功分支直接构造项目输出 `{"secid": secid, "n_boards": len(diff), "boards": diff}`。`n_boards` 是在读取响应后计算并新增的键，不是从响应对象透传。
- 空列表分支也写入 `n_boards: 0`，同时附上 `__error__`；因此它被标为采集异常，不应当解释为真实的零板块观测。
- 该适配器请求的上游叶字段是 `f12,f14,f3,f128,f140`。采集契约和完整路径清单见 [`field_source_reference.md` §12.8.5](../../field_source_reference.md) 与 [`capture_catalog.py`](../../../scripts/capture_catalog.py)。

## 保留期样本审计

样本下限遵循 [`capture_retention.py`](../../../scripts/capture_retention.py) 的 `MIN_CAPTURE_DATE=2026-10-15`。对该日之后所有含成功 `raw_slist.json` 的目录核查，`meta.data_date` 与目录日期一致；共 **8 个来源归档日、160 条成功股票记录**，每一条均满足 `n_boards == len(boards)`，不一致 **0 条**。日期与行数：20261102 (20 条), 20261103 (20 条), 20261104 (20 条), 20261105 (20 条), 20261106 (20 条), 20261109 (20 条), 20261110 (20 条), 20261117 (20 条)。

逐行结果、来源状态、原始归档 SHA-256 和元数据 SHA-256 见 [结构审计 CSV](../research/20261118_slist_n_boards_provenance_samples.csv)，其 SHA-256 为 `8656e42b596927be2608cef69479471ce17871ec5a8760efbfe7cfd71809636a`。采集器当前代码 SHA-256 为 `8ac6f32a374650366aaa6cafb3bcc67f554fce88255cd1a712711e0ad9f235ac`。

### 原始文件摘要

- `docs/field_verification/20261102/raw_slist.json` SHA-256 `6ccdd17f81864e7d53454ebc1f0da961b37a4ad7a2328edd741c0b684cdf7f3e`；`docs/field_verification/20261102/meta.json` SHA-256 `569955a6f0388bc0be8329d88d56f2d1d7aec366dbc3a12f79cd6619c6cd5b8b`。
- `docs/field_verification/20261103/raw_slist.json` SHA-256 `e93e0c70fb421679e6094ead87dcf26df75f2972ea5485f0c42b5fbbfdb89b0a`；`docs/field_verification/20261103/meta.json` SHA-256 `6dd7808d6d62454c1a78d0298dbd233920733d9ccf6ee04c3b5396a4f903452d`。
- `docs/field_verification/20261104/raw_slist.json` SHA-256 `2ca178d4580b62564be461e3457a2952afc5ec7d19ad626d332d639555f41f18`；`docs/field_verification/20261104/meta.json` SHA-256 `219e56df06512482208f262d30a6f79b7f5799bfaf8e5a3ab87c978668c50b45`。
- `docs/field_verification/20261105/raw_slist.json` SHA-256 `e5de7fc9fbe7457d4141d70c234a3d6b008d8032a0e25e5f110c7f629cb423df`；`docs/field_verification/20261105/meta.json` SHA-256 `3530efbb830252640474890a991c2b4d63b7fddd4593f75a03914bd155536616`。
- `docs/field_verification/20261106/raw_slist.json` SHA-256 `9c457e3841521bf0897ca19ee17abe578507d84eb12ee75814f1a3c79d4e05e8`；`docs/field_verification/20261106/meta.json` SHA-256 `30e26e64e400f79338a694530d04031f2f7694e7ad57deb0c46b454c8b6e1c00`。
- `docs/field_verification/20261109/raw_slist.json` SHA-256 `a9e79c9b8a05b35059c623cdf903c3d6c7d82866ad7064e8ea093884778657f9`；`docs/field_verification/20261109/meta.json` SHA-256 `53a85f72981f520355ed4713e7e6965bb177fe777163d14cdadc3625d3458945`。
- `docs/field_verification/20261110/raw_slist.json` SHA-256 `2f3dfb3829e0be3dfd69bb05654b7efb029ebf62fd368285a25bb014e4cb2f7b`；`docs/field_verification/20261110/meta.json` SHA-256 `904a33f00bb0a672d0f1f316835af8d4597cff23857e0d25e40d8959ea5cfa58`。
- `docs/field_verification/20261117/raw_slist.json` SHA-256 `c77c0234021acb2e57ecee111894a2921707203279a0ce7cb9c405e7b15b169f`；`docs/field_verification/20261117/meta.json` SHA-256 `7cc638e8bc506dfe02a2835d8641d01cc8106cb9aee94e3aebbef5d5c5154f73`。

## 注册表范围

记录代码派生血缘和精确来源身份；不把 `n_boards` 当作 Eastmoney 上游定义字段，不建立映射，不修改采集行为或历史 raw。审计前 `field_registry.json.source_fields` 中不存在 `东财-slist::n_boards`，这一点作为未登记状态快照保留；字段状态不会被解释为其业务计数无效。
