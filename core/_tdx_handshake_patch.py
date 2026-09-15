"""TDX 新式握手固化补丁（2026-09 主站强制要求）。

上游 easy_tdx(1.32.6) 已撤下且不可 pip 安装，其静态三条握手对 2026-09 行情主站
失效（握手有响应，但连接上所有 K 线请求静默返回 2 字节空包 0x0320、市场统计 /
板块指数快照返回空、/market/stat 500——服务器不报错只是不给数据）。

本补丁在本进程首次 import easy_tdx 后，将握手续命为新式单条动态握手，确保即便
site-packages 中的 easy_tdx 被重装回静态握手，本项目运行时仍生效。

关键实现要点：
- 必须在 easy_tdx.transport 模块绑定 SETUP_COMMANDS *之前* 应用（故本模块在
  core/tdx_client.py 与 core/zhb_client.py 顶部 import，而二者对 easy_tdx 的引用均
  为函数内懒加载）。
- 同时回写 transport.sync / transport.async_ 的模块级 SETUP_COMMANDS 引用，
  以抵抗「transport 已被提前 import」的乱序场景。
- 幂等：重复调用无害；若 setup.py 本身已被直接 patch 为动态（见下方说明），
  本补丁仅重新生成一条等价的动态命令。

来源对齐：V0idk/easy_tdx_1（awayings 上游 re-host）build_handshake_command()。

数据来源：通达信行情主站实测；以上为运行时修复，不构成投资建议。
"""

import random
import struct

# 与 V0idk 对齐的新式握手：单条 0x000d 命令、payload 0x01、msg_id 每连接随机。
def build_handshake_command() -> bytes:
    msg_id = random.randint(1, 0xFFFFFFFE)
    return struct.pack("<HIHHH", 0x010C, msg_id, 0x0003, 0x0003, 0x000D) + b"\x01"


_PATCH_MARK = "_v17212_dynamic_handshake_patched"


def apply() -> None:
    """将 easy_tdx 握手替换为新式动态单条握手（幂等）。

    同时覆盖 setup 模块与已 import 的 transport 模块的绑定引用。
    """
    import easy_tdx.commands.setup as _setup

    if not getattr(_setup, _PATCH_MARK, False):
        # 确保函数存在（即使原包未定义）
        if not hasattr(_setup, "build_handshake_command"):
            _setup.build_handshake_command = build_handshake_command
        # 重写握手为单条动态命令（transport 遍历此处、ping/心跳取 [0] 均兼容）
        _setup.SETUP_COMMANDS = (_setup.build_handshake_command(),)
        setattr(_setup, _PATCH_MARK, True)

    # 回写已绑定的 transport 引用，抗乱序 import
    _dyn = _setup.SETUP_COMMANDS
    for _mod in ("easy_tdx.transport.sync", "easy_tdx.transport.async_"):
        try:
            __import__(_mod)
            _m = __import__(_mod, fromlist=["_"])
            if getattr(_m, "SETUP_COMMANDS", None) is not _dyn:
                _m.SETUP_COMMANDS = _dyn
        except Exception:
            # transport 未安装/不可导入时跳过；运行时首次真正使用时仍会走 setup 动态值
            pass


# import 即生效（core/tdx_client.py、core/zhb_client.py 顶部 import 本模块）
apply()
