"""config.py — 全局配置集中管理

V12.2: 将分散在各模块中的硬编码常量集中到此处，便于统一调优和维护。

使用方式：
    from core.config import HTTP_TIMEOUT_SECONDS, MAX_RETRY_COUNT
"""
from __future__ import annotations

# ═══════════════════════════════════════
# 网络配置
# ═══════════════════════════════════════
HTTP_TIMEOUT_SECONDS = 15
"""HTTP 请求默认超时时间（秒）"""

# ═══════════════════════════════════════
# 限流配置
# ═══════════════════════════════════════
TDX_MIN_INTERVAL = 0.1
"""TDX 请求最小间隔（秒），防止过快请求被服务器断开"""

EM_MIN_INTERVAL = 1.0
"""东财请求最小间隔（秒），防止高频被封IP"""

# ═══════════════════════════════════════
# 重试配置
# ═══════════════════════════════════════
MAX_RETRY_COUNT = 3
"""默认最大重试次数"""

RETRY_DELAY_SECONDS = 0.5
"""重试基础延迟（秒），实际延迟为 delay * (2 ** attempt)"""

# ═══════════════════════════════════════
# 容错配置
# ═══════════════════════════════════════
CIRCUIT_BREAKER_FAILURE_THRESHOLD = 10
"""熔断器失败阈值：连续失败多少次后触发断路"""

CIRCUIT_BREAKER_RESET_TIMEOUT_SECONDS = 60
"""熔断器重置时间（秒）：断路后等待多久进入半开状态"""

# V16.4.1: 原 TOKEN_BUCKET_RPS_EASTMONEY / TOKEN_BUCKET_RPS_TENCENT 为死配置
# （无任何调用方）——令牌桶 rps 实际全部由 sc_network._DOMAIN_LIMITS 分域管理
# （push2 系 0.4rps 最严，其余东财域 1.0rps，腾讯/新浪 5rps）。
# V16.4.1 审查清理: 另删 8 个 0 引用常量(HTTP_TIMEOUT_LONG/CACHE_*/MARKET_*/PRE_MARKET_CUTOFF)
