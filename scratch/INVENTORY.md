# scratch/ 调研沙盒目录清单

> V15.3 文档化: 此目录是用户的 A股数据调研沙盒，**不参与生产代码运行**。
> `.gitignore` 已 ignore `scratch/*`（除本 INVENTORY.md），不会污染主仓库。
> V16.3 B5 更新: 原 13 个子目录已全部清理。
> V16.3 E 更新: 8/5 字段破解实验产物（field_break*/field_verify*/profile_* 共 39 个）已删除——
> 全部结论已落库 docs/field_dict.md（V16.3 D2），当前仅存历史调研脚本。

## 当前文件（7 个，均在根层，全部 git 跟踪）

| 文件 | 用途 |
|:---|:---|
| `INVENTORY.md` | 本清单 |
| `get_real_data.py` | 拉真实数据调试 |
| `parse_zhb.py` | 解析 ZHB 数据集 |
| `query_tipinfo.py` | 查询个股提示信息 |
| `sample_all.py` | 全市场采样 |
| `search_mcap.py` | 按市值搜索 |

## 何时可以删除整个 scratch/

所有调研代码迁移到主仓库后整体删除；当前保留作为快速参考。
