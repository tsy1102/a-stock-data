# Bug修复路线图 V9.2

> 基于代码质量审查报告的修复计划
> 生成日期：2026-07-05
> 范围：53项问题 → 筛选后约30项需修复

---

## 一、前置核查结论

### 1.1 P0 安全问题 — 已处理
| 问题 | 状态 | 说明 |
|------|------|------|
| credentials.json / client_secrets.json 入库 | ✅ 无需修复 | 已在 `.gitignore` 第2、5行，无泄露隐患 |

### 1.2 P0 日历数据问题 — 现状分析
**问题**：stock_calendar.py 内置数据仅到 2026 年，2027 年后节假日会误判

**当前降级链**（[sc_datasource.py:2104-2154](file:///d:/GitHub/test/stock_common/sc_datasource.py#L2104-L2154)）：
```
本地 stock_calendar.is_workday()
    ↓ 年份超出 → NotImplementedError
chinese-calendar 库 is_workday()
    ↓ 同样超出 → NotImplementedError
_try_upgrade_calendar() 自动 pip 升级
    ↓ 升级失败（无外网/内网环境）
d.weekday() < 5  ← 节假日误判为交易日
```

**核查结论**：
- stock_calendar.py **无 CLI 入口**（无 `__main__`），不能直接运行更新
- 仓库中**无** generate_calendar / update_calendar / build_calendar 等更新脚本
- 自动升级依赖外网，内网/离线环境不可用
- **需要新增**：从 chinese-calendar 库提取数据并更新 stock_calendar.py 的脚本

---

## 二、修复优先级与分类

### P0 — 数据正确性（必须修）
| # | 问题 | 影响 | 方案 |
|---|------|------|------|
| P0-1 | 日历数据 2026 后过期 → 节假日误判 | 影响 F10 交易日缓存、所有交易日判断 | 新增日历更新脚本 + 启动时自动检查 + 降级时警告日志 |

### P1 — 功能缺陷（影响使用）
| # | 问题 | 影响 | 方案 |
|---|------|------|------|
| P1-1 | seat_db.py 硬编码 seats-2026.json | 跨年后席位识别降级 | 改为 seats.json 或自动按年份选择 |
| P1-2 | gd_uploader.py _make_stock_folder_name 重复定义 | ST 股票文件夹命名错误 | 删除第二版，保留第一版（含 ST 处理） |
| P1-3 | sc_scoring.py 亏损股评分封顶被突破 | 亏损股评分可能 >20 分 | 把 min(score, 20.0) 移到 return 前最终裁剪 |
| P1-4 | tests 9个文件硬编码 d:\GitHub\test 路径 | 换机器/C I 无法运行 | 统一改为 `os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` |

### P2 — 稳定性（易出问题）
| # | 问题 | 影响 | 方案 |
|---|------|------|------|
| P2-1 | 13处裸 `except:` 捕获 BaseException | Ctrl+C 无法终止脚本 | 全部改为 `except Exception:` + 日志 |
| P2-2 | 15+处 `except Exception: pass` 静默吞异常 | 调试困难，问题被掩盖 | 加 `_debug_log` 记录异常来源和信息 |
| P2-3 | stock_cache.py get/set_cache 无锁保护 | cross_verify 竞态丢失更新 | set_cache 加锁保护 SELECT-then-UPDATE |
| P2-4 | stock_cache.py 异步连接不复用 | 高频异步访问性能差 | 引入模块级 _async_db 单例 |
| P2-5 | stock_cache.py create_task 未保存引用 | 后台任务可能被 GC | 用 set 持有 task 引用，done 后移除 |
| P2-6 | tdx_client.py 重连不 close 旧连接 | socket fd / 心跳线程泄漏 | 异常重连前先 close 旧 client |
| P2-7 | main.py check_dependencies 模块级执行 | import main 触发 sys.exit | 移到 `if __name__ == "__main__":` 内 |

### P3 — 代码质量（低优先级）
| # | 问题 | 方案 |
|---|------|------|
| P3-1 | sc_utils.py:363 `import time` 在文件末尾 | 移到顶部 import 区 |
| P3-2 | __init__.py:154-178 _legacy 死代码 + _MIGRATION_STATUS | 删除 legacy 相关死代码 |
| P3-3 | stock_cache.py:691,748 `# type: ignore` | 优化类型标注，移除 ignore |
| P3-4 | sc_network.py 死代码：_DOMAIN_SEMAPHORES / 两个 Semaphore(3) | 删除或标注 deprecated |
| P3-5 | tdx_client.py monkey-patch 异常静默 | 补丁失败时加警告日志 |
| P3-6 | conftest.py monkeypatch 失败静默 | 加日志提示 mock 未生效 |
| P3-7 | test_cache.py:64 time.sleep(1.5) 脆性测试 | 改用 mock time 或缩短 TTL |
| P3-8 | test_cache_verify.py tearDown 静默 | 删除失败加 debug 日志 |
| P3-9 | sc_datasource.py:2127 静默降级 | 加 debug 日志记录降级事件 |
| P3-10 | analyze_history.py:508 OSError 静默 | 删除失败加 debug 日志 |
| P3-11 | sc_datasource.py:2593 类型标注错误 | 改为 `Optional[List[float]]` |

---

## 三、各阶段详细方案

### 阶段 1：P0 日历数据修复（最高优先级）

**目标**：解决 2027 年后日历数据过期问题

**任务清单**：
1. **新增 `scripts/update_calendar.py`**
   - 从已安装的 chinese-calendar 库提取 holidays / workdays 数据
   - 生成新的 stock_calendar.py 文件内容
   - 自动备份旧文件
   - 支持指定年份范围

2. **修改 `stock_common/stock_calendar.py`**
   - 新增 `__main__` CLI 入口（调用 update 脚本）
   - 或新增 `update_data()` 函数

3. **修改 `sc_datasource.py:is_trading_day()`**
   - 降级到 `weekday < 5` 时，打印警告日志（仅首次）
   - 避免静默误判

**验收标准**：
- 运行 `python -m stock_common.stock_calendar --update` 可更新数据
- 降级时控制台输出明确警告

---

### 阶段 2：P1 功能缺陷修复

#### 2.1 seat_db.py 硬编码年份
- 文件：[stock_common/seat_db.py:14](file:///d:/GitHub/test/stock_common/seat_db.py#L14)
- 方案：将 `seats-2026.json` 改为 `seats.json`
- 同步：重命名 `stock_common/seats-2026.json` → `seats.json`
- 注意：确保所有引用处同步修改

#### 2.2 gd_uploader.py 函数重定义
- 文件：[gd_uploader.py:337](file:///d:/GitHub/test/gd_uploader.py#L337) 和 [gd_uploader.py:503](file:///d:/GitHub/test/gd_uploader.py#L503)
- 方案：删除第 503 行的第二版定义，保留第一版（含 ST 处理）
- 验证：检查 upload_stock_report_by_code 调用处是否兼容

#### 2.3 sc_scoring.py 亏损股评分
- 文件：[stock_common/sc_scoring.py:195](file:///d:/GitHub/test/stock_common/sc_scoring.py#L195)
- 方案：将 `score = min(score, 20.0)` 从 ROE 分支内移到函数末尾（return 前）
- 确保：最终返回前统一裁剪 `max(0, min(100, score))` 后，再对亏损股应用 20 分上限

#### 2.4 tests 硬编码路径修复
涉及文件（9个）：
- [tests/test_f10_debug_000001.py](file:///d:/GitHub/test/tests/test_f10_debug_000001.py)
- [tests/test_f10_debug_find.py](file:///d:/GitHub/test/tests/test_f10_debug_find.py)
- [tests/test_f10_explore.py](file:///d:/GitHub/test/tests/test_f10_explore.py)
- [tests/test_f10_explore2.py](file:///d:/GitHub/test/tests/test_f10_explore2.py)
- [tests/test_f10_explore_f3.py](file:///d:/GitHub/test/tests/test_f10_explore_f3.py)
- [tests/test_f10_explore_f3_000001.py](file:///d:/GitHub/test/tests/test_f10_explore_f3_000001.py)
- [tests/test_f10_explore_p1.py](file:///d:/GitHub/test/tests/test_f10_explore_p1.py)
- [tests/test_f10_financial.py](file:///d:/GitHub/test/tests/test_f10_financial.py)
- [tests/test_f10_reminders.py](file:///d:/GitHub/test/tests/test_f10_reminders.py)

方案：统一替换为：
```python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

---

### 阶段 3：P2 稳定性修复

#### 3.1 裸 except: → except Exception: + 日志

**原则**：
- 所有 `except:` 改为 `except Exception:`（允许 KeyboardInterrupt/SystemExit 穿透）
- 能明确异常类型的，精确捕获
- 不能明确的，加 `_debug_log` 记录来源和异常信息

**裸 except: 清单（13处）**：

| 文件 | 行 | 上下文 | 修复方案 |
|------|----|--------|---------|
| get_val_report.py | 298 | `p = 0` 兜底 | `except Exception:` + 保留 p=0 |
| get_sht_report.py | 1310 | `pass` | `except Exception as e:` + _debug_log |
| get_lng_report.py | 245 | 赋值"N/A" | `except Exception:` + 保留赋值 |
| get_lng_report.py | 293 | `pass` | `except Exception as e:` + _debug_log |
| get_lng_report.py | 429 | `pass` | `except Exception as e:` + _debug_log |
| get_med_report.py | 270 | 赋值"N/A" | `except Exception:` + 保留赋值 |
| get_med_report.py | 297 | `return 0.0` | `except Exception:` + 保留 return |
| get_med_report.py | 353 | `pass` | `except Exception as e:` + _debug_log |
| get_med_report.py | 379 | `pass` | `except Exception as e:` + _debug_log |
| get_med_report.py | 446 | `pass` | `except Exception as e:` + _debug_log |
| get_mak_report.py | 404 | `return ""` | `except Exception:` + 保留 return |
| tests/test_datasource.py | 114 | 测试用例 | `except Exception:` |
| tests/test_em_rate_limit.py | 107 | 测试用例 | `except Exception:` |

**新增工具函数**（建议放在 sc_utils.py）：
```python
import logging
_debug_logger = logging.getLogger("stock_debug")

def _debug_log(source: str, e: Exception) -> None:
    """调试用异常日志，默认仅在 DEBUG 级别输出。"""
    _debug_logger.debug(f"[{source}] {type(e).__name__}: {e}")
```

#### 3.2 except Exception: pass → 加日志

**清单（15处）**：

| 文件 | 行 | 修复方案 |
|------|----|---------|
| tdx_client.py | 471 | + _debug_log |
| tdx_client.py | 589 | + _debug_log |
| tdx_client.py | 615 | + _debug_log |
| tdx_client.py | 639 | + _debug_log |
| get_lng_report.py | 172 | + _debug_log |
| get_lng_report.py | 213 | + _debug_log |
| get_lng_report.py | 230 | + _debug_log |
| get_lng_report.py | 317 | + _debug_log |
| get_lng_report.py | 330 | + _debug_log |
| get_lng_report.py | 403 | + _debug_log |
| get_lng_report.py | 469 | + _debug_log |
| get_med_report.py | 457 | + _debug_log |
| get_mak_report.py | 107 | + _debug_log |
| get_mak_report.py | 180 | + _debug_log |
| get_mak_report.py | 594 | + _debug_log |

> 注：get_ful_report.py 约 24 处 `except Exception: pass` 也需同步处理，需逐行核查。

#### 3.3 stock_cache.py 并发安全
- 方案：`set_cache` 中 cross_verify 分支的 SELECT-then-UPDATE 用 `_db_lock` 包裹
- 范围：仅 cross_verify 分支加锁，普通模式保持无锁

#### 3.4 stock_cache.py 异步连接复用
- 方案：新增模块级 `_async_db = None`，首次连接后复用
- 注意：aiosqlite 连接不是线程安全的，但在单线程 asyncio loop 内可复用

#### 3.5 stock_cache.py task 引用
- 方案：
```python
_bg_tasks: set = set()

def _hold_bg_task(coro):
    t = asyncio.create_task(coro)
    _bg_tasks.add(t)
    t.add_done_callback(_bg_tasks.discard)
    return t
```

#### 3.6 tdx_client.py 重连泄漏
- 文件：[tdx_client.py:295-302](file:///d:/GitHub/test/tdx_client.py#L295-L302) 和 [tdx_client.py:347-355](file:///d:/GitHub/test/tdx_client.py#L347-L355)
- 方案：`_TDX_CLIENT = None` 前先调用 `_TDX_CLIENT.close()` 或 `stop_heartbeat()`

#### 3.7 main.py 模块级副作用
- 文件：[main.py:80](file:///d:/GitHub/test/main.py#L80)
- 方案：将 `check_dependencies()` 调用移到 `if __name__ == "__main__":` 块内

---

### 阶段 4：P3 代码质量修复

批量处理低优先级问题，包括：
- import 位置修正
- 死代码清理
- 类型标注改进
- 静默异常加日志
- 测试代码优化

详见上表 P3 清单（11项）。

---

## 四、不在本次修复范围的问题

以下问题经核查**不成立**或**属于设计取舍**，暂不修复：

| 问题 | 原因 |
|------|------|
| _has_zero_price 误判 pe/volume=0 | 按键名精确匹配 price/close，不会误判 |
| _ensure_async_locks 非 async 上下文报错 | 仅在 async 函数内调用，且 Python 3.10+ 无此问题 |
| RLock 跨线程死锁 | 无 run_in_executor，RLock 同线程配对使用无死锁 |
| 交叉验证"永不更新" | TTL 到期后自动重新验证，数据会更新 |
| tdx_get_quote_full 返回 None 崩溃 | 函数从不返回 None，且外层有 try/except 保护 |
| _SNAPSHOT_DATA 全局变量污染 | 单进程 CLI 无影响，累积保存是设计意图 |
| 交叉验证相同错误数据通过 | 机制固有局限，valid_if 可缓解 |
| MD5 碰撞风险 | 概率 2^-128，非安全场景可忽略 |
| sc_network.py 文件锁瓶颈 | 主请求路径不调用这两个函数 |
| 429 退避 7秒 | 实际是 3秒，无告警属实但影响有限 |
| valuation_methods.py:139 逻辑缺陷 | 是冗余调用但非缺陷，verdict 已标记需要价格 |

---

## 五、验收标准

### 功能验证
- [ ] 日历更新脚本可正常运行并生成新数据
- [ ] 所有报告脚本运行不报错
- [ ] 9个 f10 测试文件在其他路径下可正常 import
- [ ] 席位识别功能正常

### 代码质量验证
- [ ] 无裸 `except:`（grep `^except:` 返回 0 条 .py 文件）
- [ ] 无 `except Exception: pass`（或全部已加日志）
- [ ] Ctrl+C 能正常终止所有脚本
- [ ] import main 不会触发 sys.exit

### 测试验证
- [ ] test_cache_verify.py 7个测试全部通过
- [ ] test_cache.py 全部通过
- [ ] test_scoring.py 全部通过

---

## 六、实施顺序建议

```
阶段1（P0）→ 阶段2（P1）→ 阶段3.1（裸except）→ 阶段3.2（静默except）
    → 阶段3其余 → 阶段4（P3代码质量）
```

**预计工作量**：
- 阶段1：~2小时
- 阶段2：~1小时
- 阶段3.1-3.2：~2小时（50+处逐行修改）
- 阶段3.3-3.7：~2小时
- 阶段4：~1小时
- 测试验证：~1小时
- **合计：约 9-10 小时**
