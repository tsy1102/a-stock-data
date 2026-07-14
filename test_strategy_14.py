import traceback
import get_val_report
import asyncio

get_val_report.tencent_quote_batch = lambda codes: {
    "510300": {"name": "沪深300ETF", "change_pct": 5.0},
    "511010": {"name": "国债ETF", "change_pct": 0.5}
}

async def main():
    try:
        res = await asyncio.to_thread(get_val_report.strategy_14_asset_rebalance)
        print("Success:", res)
    except Exception as e:
        traceback.print_exc()

asyncio.run(main())
