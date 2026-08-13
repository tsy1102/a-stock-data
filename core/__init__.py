"""core 包 — 项目核心模块(V17.0 目录整理)

包含 7 个支撑模块: config / data_provider / gd_uploader / stock_cache /
tdx_client / zhb_client / zhb_sync。

设计约束(V17.0):
- __init__.py 必须保持为空(仅 docstring)——任何子模块都不在此导入,
  防止 core ↔ stock_common 顶层循环依赖(stock_common 懒 import 全仓既有保护,
  见 AGENTS.md §12 循环依赖踩坑记录)。
- 报告脚本(get_*_report.py)/ main.py 留在仓库根目录作为入口,
  以 `from core import X` 绝对导入引用本包。
"""
