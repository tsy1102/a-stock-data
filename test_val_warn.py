import sys
import os
import warnings
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

warnings.filterwarnings("error", category=RuntimeWarning)

from get_val_report import run_discovery_async
import asyncio

async def test():
    try:
        await run_discovery_async(os.devnull)
    except Exception as e:
        print(f'错误类型: {type(e).__name__}')
        print(f'错误信息: {e}')
        import traceback
        traceback.print_exc()

asyncio.run(test())
