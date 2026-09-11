"""原子补做 mak 审查建议 1-4 的标注（edits 1-4 此前并行 Edit 竞态丢写）。

单次读全文件 -> 内存 4 处替换 -> 单次写回，避免多 Edit 覆盖丢写。
每个 old 必须恰好命中 1 次，否则报错中止，绝不静默部分写入。
"""
import sys

PATH = r"c:\Tencent\WorkBuddy\a-stock-data\get_mak_report.py"
src = open(PATH, encoding="utf-8").read()

reps = []

# 编辑1: 同花顺交叉验证段空时标注"数据源受限"
reps.append((
    '            for _h in _ths_only[:10]:\n'
    '                L(f"| {_h.get(\'code\',\'\')} | {_h.get(\'name\',\'\')}{_name_mark(_h.get(\'name\',\'\'))} | {_safe_float(_h.get(\'zhangfu\',0)):+.2f}% | {str(_h.get(\'reason\',\'\'))[:40]} |")\n'
    '\n'
    '    L("## 【C. 板块-异动集中度分析】")',
    '            for _h in _ths_only[:10]:\n'
    '                L(f"| {_h.get(\'code\',\'\')} | {_h.get(\'name\',\'\')}{_name_mark(_h.get(\'name\',\'\'))} | {_safe_float(_h.get(\'zhangfu\',0)):+.2f}% | {str(_h.get(\'reason\',\'\'))[:40]} |")\n'
    '    else:\n'
    '        L(\'\')\n'
    '        L("  ⚠️ 同花顺独家交叉验证：数据源受限（同花顺网页接口 401 反爬），强势股热池暂无法获取，交叉验证增量视角缺失。")\n'
    '\n'
    '    L("## 【C. 板块-异动集中度分析】")',
    "edit1 同花顺段 else",
))

# 编辑2: A段竞价风向标 fuyao 未启用标注
reps.append((
    '                    elif _pos_a / _n < 0.3:\n'
    '                        L("    ⚠️ 竞价红盘占比不足三成，开盘防御为上")\n'
    '    except Exception as _e:\n'
    '        _debug_log(f"mak fuyao auction benchmark: {_e}")',
    '                    elif _pos_a / _n < 0.3:\n'
    '                        L("    ⚠️ 竞价红盘占比不足三成，开盘防御为上")\n'
    '        else:\n'
    '            L("  ⚠️ 竞价风向标：fuyao 竞价数据未启用（无盘前 9:25 短线情绪基准，开盘氛围判断缺失）")\n'
    '    except Exception as _e:\n'
    '        _debug_log(f"mak fuyao auction benchmark: {_e}")',
    "edit2 A段竞价风向标 else",
))

# 编辑3: B+ 连板矩阵 fuyao 未启用标注（加 is_fuyao_enabled 守卫）
reps.append((
    '    # V17.0.5 P1: fuyao 连板天梯互校(boards 六档矩阵+seal_nextday 次日封板率——独有字段)\n'
    '    try:\n'
    '        from stock_common import get_fuyao_limit_up_ladder as _f_ladder\n'
    '\n'
    '        _lad = await asyncio.to_thread(_f_ladder)\n'
    '        _lad_items = ((_lad or {}).get("item") or [])\n'
    '        if _lad_items and isinstance(_lad_items, list):\n'
    '            _latest = _lad_items[0] if isinstance(_lad_items[0], dict) else {}\n'
    '            _boards = _latest.get("boards") or {}\n'
    '            _summary = []\n'
    '            for _bk in ("two_board", "three_board", "four_board", "five_board", "six_board", "seven_over"):\n'
    '                _lst = _boards.get(_bk) or []\n'
    '                if _lst:\n'
    '                    _sealed_next = sum(1 for x in _lst if x.get("seal_nextday"))\n'
    '                    _summary.append(f"{_bk.replace(\'_board\',\'\')}板{len(_lst)}只(次日续封{_sealed_next})")\n'
    '            if _summary:\n'
    '                L("\\n  🪜 fuyao 连板矩阵互校（30 日窗口最新日）:")\n'
    '                L("    " + " | ".join(_summary))\n'
    '    except Exception as _e:\n'
    '        _debug_log(f"mak fuyao ladder: {_e}")',
    '    # V17.0.5 P1: fuyao 连板天梯互校(boards 六档矩阵+seal_nextday 次日封板率——独有字段)\n'
    '    try:\n'
    '        from stock_common import get_fuyao_limit_up_ladder as _f_ladder, is_fuyao_enabled as _f_lad_on\n'
    '\n'
    '        if _f_lad_on():\n'
    '            _lad = await asyncio.to_thread(_f_ladder)\n'
    '            _lad_items = ((_lad or {}).get("item") or [])\n'
    '            if _lad_items and isinstance(_lad_items, list):\n'
    '                _latest = _lad_items[0] if isinstance(_lad_items[0], dict) else {}\n'
    '                _boards = _latest.get("boards") or {}\n'
    '                _summary = []\n'
    '                for _bk in ("two_board", "three_board", "four_board", "five_board", "six_board", "seven_over"):\n'
    '                    _lst = _boards.get(_bk) or []\n'
    '                    if _lst:\n'
    '                        _sealed_next = sum(1 for x in _lst if x.get("seal_nextday"))\n'
    '                        _summary.append(f"{_bk.replace(\'_board\',\'\')}板{len(_lst)}只(次日续封{_sealed_next})")\n'
    '                if _summary:\n'
    '                    L("\\n  🪜 fuyao 连板矩阵互校（30 日窗口最新日）:")\n'
    '                    L("    " + " | ".join(_summary))\n'
    '        else:\n'
    '            L("  ⚠️ fuyao 连板矩阵互校：竞价数据未启用（无连板六档矩阵 / 次日封板率互校）")\n'
    '    except Exception as _e:\n'
    '        _debug_log(f"mak fuyao ladder: {_e}")',
    "edit3 B+连板矩阵 guard+else",
))

# 编辑4: F段跌停明细 fuyao 未启用标注
reps.append((
    '                            f" | {_it.get(\'turnover_ratio_pct\',0):.2f}% |"\n'
    '                        )\n'
    '        except Exception as _e:\n'
    '            _debug_log(f"mak fuyao limit_down detail: {_e}")',
    '                            f" | {_it.get(\'turnover_ratio_pct\',0):.2f}% |"\n'
    '                        )\n'
    '            else:\n'
    '                L("  跌停明细：fuyao 数据未启用（无官方首次/最后跌停时刻与换手，仅保留涨停池口径跌停数）")\n'
    '        except Exception as _e:\n'
    '            _debug_log(f"mak fuyao limit_down detail: {_e}")',
    "edit4 F段跌停明细 else",
))

ok = True
for old, new, label in reps:
    cnt = src.count(old)
    if cnt != 1:
        print(f"[FAIL] {label}: expected 1 match, got {cnt}")
        ok = False
        continue
    src = src.replace(old, new, 1)
    print(f"[OK]   {label}")

if not ok:
    print("ABORT: 存在不匹配的 old 串，未写入任何内容")
    sys.exit(1)

with open(PATH, "w", encoding="utf-8") as f:
    f.write(src)
print("WRITTEN: get_mak_report.py (4 edits applied atomically)")
