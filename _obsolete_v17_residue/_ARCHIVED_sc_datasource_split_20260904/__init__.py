"""stock_common/sc_datasource — V17.1 拆包 Facade 包。
原单文件 sc_datasource.py(7617 行) 按域拆分为 _shared/_holders/_eastmoney/_quotes/
_industry/_financials/_pools/_zhb/_misc，本 __init__ 把全部名字注入各子模块命名空间
（等价原单文件全局命名空间），并对外重导出，保证所有 import 站点零破坏。
"""
from . import _shared
from . import (_holders, _eastmoney, _quotes, _industry,
               _financials, _pools, _zhb, _misc)

_SUBMODULES = [_shared, _holders, _eastmoney, _quotes, _industry,
              _financials, _pools, _zhb, _misc]

# 收集全部公开名字（函数 + 常量 + import 块名）
_ALL = {}
for _m in _SUBMODULES:
    for _k, _v in vars(_m).items():
        if _k.startswith("__"):
            continue
        _ALL[_k] = _v

# 注入每个子模块命名空间：使跨模块调用（含私有常量引用）在运行时解析，等价原单文件
for _m in _SUBMODULES:
    _m.__dict__.update(_ALL)

# 对外重导出：from stock_common.sc_datasource import X
globals().update(_ALL)

del _m, _k, _v, _SUBMODULES, _ALL
