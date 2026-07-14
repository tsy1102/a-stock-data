#!/usr/bin/env python3
"""zhb_client.py — 通达信 zhb.zip 全局配置总包下载与解析模块。

通过 0x06B9 协议从通达信服务器下载 zhb.zip，解压解析后提供：

**A级数据（结构性，季度/半年度更新）**：
    - spblock.dat: 大板块成分股（中证2000/沪深港通等，突破400只限制）
    - tdxzs3.cfg: 板块代码映射 + 申万行业分类（467个四级分类）
    - tdxzs.cfg / tdxbk.cfg: 板块简称↔全称映射
    - needini.dat: 节假日数据（1991-2030）
    - incon.dat: 证监会行业分类（3703个）
    - brkcomp.dat: 券商名称表（842家）

**B级数据（准时效，日线级别，可能有1-2天延迟）**：
    - tdxstat.cfg: 全市场个股统计快照（7938只，35字段：涨跌幅/PE/5-60日涨跌幅等）
    - tdxstat2.cfg: 全市场资金流向+板块归属（21字段：行业代码/52周高低价等）

**辅助数据（事件驱动/套利策略）**：
    - tipinfo.dat: 财报日历（5609只，EPS/财报披露日/除权除息日/分红日）
    - xgsg.cfg: 新股申购日历（近期新股）
    - tdxahrate.cfg: A+H股比价
    - tdxadr.cfg: 中概股ADR对应表（30只）
    - othersg.cfg: 可转债信息
    - pttab.dat: 股票代码对照表（含退市股）

缓存策略：
    - 原始 zip 保存到 cache/zhb/zhb_{YYYYMMDD}.zip
    - 内存缓存解析结果，同一进程内重复调用零成本
    - 自动清理 7 天前的旧文件

版本信息:
    V10.0  2026-07-14 - 全面升级：新增证监会行业/中概股ADR/可转债/退市股；进程安全文件锁；磁盘空间保护；节假日导出
    V9.6   2026-07-14 - 初始版本：基于 pytdx GetReportFile 下载 zhb.zip
"""
from __future__ import annotations

import os
import io
import zipfile
import time
import threading
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from stock_common import _debug_log

# ═══════════════════════════════════════
# 配置常量
# ═══════════════════════════════════════

_ZHB_CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache", "zhb")
_KEEP_DAYS = 7
_MIN_DISK_SPACE_MB = 100  # 最小保留磁盘空间（MB）
_LOCK_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache", "zhb", ".zhb.lock")

# 通达信行情节点（优先招商/国信主站，数据更新快）
_ZHB_HOSTS = [
    ("119.147.212.81", 7709),   # 招商证券深圳主站
    ("121.14.110.194", 7709),   # 国信证券深圳主站
    ("112.74.214.43", 7709),    # 招商深圳
    ("101.227.73.20", 7709),    # 国信上海
    ("101.227.77.254", 7709),   # 国信上海
    ("14.17.75.71", 7709),      # 广东电信
    ("120.76.152.87", 7709),    # 备用节点
]

# ═══════════════════════════════════════
# 全局状态
# ═══════════════════════════════════════

_zhb_memory_cache: Optional["ZhbData"] = None
_zhb_cache_lock = threading.Lock()


# ═══════════════════════════════════════
# 进程安全文件锁
# ═══════════════════════════════════════

def _acquire_file_lock(timeout: float = 30.0) -> bool:
    """获取文件锁（进程安全）。

    Args:
        timeout: 超时时间（秒）

    Returns:
        True if lock acquired, False if timeout
    """
    _ensure_cache_dir()
    lock_path = _LOCK_FILE

    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            # 尝试创建锁文件
            fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            # 写入进程ID
            os.write(fd, f"{os.getpid()}\n".encode())
            os.close(fd)
            return True
        except FileExistsError:
            # 锁文件已存在，检查是否过期（超过60秒）
            try:
                mtime = os.path.getmtime(lock_path)
                if time.time() - mtime > 60:
                    # 锁已过期，删除后重试
                    os.remove(lock_path)
                    continue
            except OSError:
                pass
            time.sleep(0.5)
        except OSError:
            time.sleep(0.5)
    return False


def _release_file_lock() -> None:
    """释放文件锁。仅删除属于当前进程的锁文件，防止误删其他进程的锁。"""
    try:
        if os.path.exists(_LOCK_FILE):
            with open(_LOCK_FILE, "r", encoding="utf-8") as f:
                lock_pid = f.read().strip()
            if lock_pid == str(os.getpid()):
                os.remove(_LOCK_FILE)
    except OSError:
        pass


def _check_disk_space() -> bool:
    """检查磁盘空间是否充足。

    Returns:
        True if space is sufficient, False otherwise
    """
    try:
        import shutil
        stat = shutil.disk_usage(_ZHB_CACHE_DIR)
        free_mb = stat.free / (1024 * 1024)
        if free_mb < _MIN_DISK_SPACE_MB:
            _debug_log(f"zhb: disk space low ({free_mb:.1f}MB < {_MIN_DISK_SPACE_MB}MB), cleaning...")
            # 紧急清理：保留最新的一个文件
            try:
                files = sorted(
                    [f for f in os.listdir(_ZHB_CACHE_DIR) if f.endswith(".zip")],
                    key=lambda x: os.path.getmtime(os.path.join(_ZHB_CACHE_DIR, x)),
                    reverse=True
                )
                for f in files[1:]:  # 保留最新的一个
                    try:
                        os.remove(os.path.join(_ZHB_CACHE_DIR, f))
                    except OSError:
                        pass
            except OSError:
                pass
            return free_mb >= _MIN_DISK_SPACE_MB
        return True
    except Exception as e:
        _debug_log(f"zhb: disk space check error: {e}")
        return True  # 检查失败时继续执行


# ═══════════════════════════════════════
# ZhbData 数据类
# ═══════════════════════════════════════

class ZhbData:
    """zhb.zip 解析后的数据容器。"""

    def __init__(self) -> None:
        self.date: str = ""
        self.raw_files: Dict[str, bytes] = {}
        self._sp_blocks: Optional[Dict[str, List[str]]] = None
        self._sw_industries: Optional[Dict[str, str]] = None
        self._industry_map: Optional[Dict[str, str]] = None
        self._holidays: Optional[List[str]] = None
        self._stock_stats: Optional[Dict[str, Dict[str, Any]]] = None
        self._stock_stats2: Optional[Dict[str, Dict[str, Any]]] = None
        self._tip_info: Optional[Dict[str, Dict[str, Any]]] = None
        self._ipo_list: Optional[List[Dict[str, Any]]] = None
        self._ah_stocks: Optional[List[Dict[str, str]]] = None
        self._brokers: Optional[Dict[str, str]] = None
        self._csrc_industries: Optional[Dict[str, str]] = None
        self._adr_stocks: Optional[List[Dict[str, str]]] = None
        self._convertible_bonds: Optional[List[Dict[str, Any]]] = None
        self._delisted_stocks: Optional[Dict[str, str]] = None

    # ── spblock 大板块 ──

    @property
    def sp_blocks(self) -> Dict[str, List[str]]:
        if self._sp_blocks is None:
            self._sp_blocks = self._parse_spblock()
        return self._sp_blocks

    def _parse_spblock(self) -> Dict[str, List[str]]:
        data = self.raw_files.get("spblock.dat", b"")
        if not data:
            return {}
        text = data.decode("gbk", errors="ignore")
        blocks: Dict[str, List[str]] = {}
        current_name = ""
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith("#"):
                current_name = line[1:].strip()
                blocks[current_name] = []
            elif current_name:
                code = line.strip()
                if len(code) >= 6:
                    # spblock.dat 中代码是7位（首字节是市场代码：0深/1沪/2北）
                    # 转换为标准6位代码
                    code = code[-6:]
                if code:
                    blocks[current_name].append(code)
        return blocks

    def get_sp_block(self, name: str) -> List[str]:
        """获取指定大板块的成分股列表。支持模糊匹配（包含子串）。"""
        if name in self.sp_blocks:
            return self.sp_blocks[name]
        for k, v in self.sp_blocks.items():
            if name in k:
                return v
        return []

    def list_sp_blocks(self) -> List[tuple]:
        """列出所有大板块 (名称, 成分股数)。"""
        return [(k, len(v)) for k, v in self.sp_blocks.items()]

    # ── 申万行业 ──

    @property
    def sw_industries(self) -> Dict[str, str]:
        if self._sw_industries is None:
            self._sw_industries = self._parse_sw_industries()
        return self._sw_industries

    def _parse_sw_industries(self) -> Dict[str, str]:
        """从 tdxzs3.cfg 提取申万行业（类型12）。
        返回: {板块代码: 板块名称}
        """
        data = self.raw_files.get("tdxzs3.cfg", b"")
        if not data:
            return {}
        text = data.decode("gbk", errors="ignore")
        result: Dict[str, str] = {}
        for line in text.splitlines():
            parts = line.split("|")
            if len(parts) >= 3 and parts[2] == "12":
                name = parts[0].strip()
                code = parts[1].strip()
                if code:
                    result[code] = name
        return result

    # ── 行业映射表（所有类型） ──

    @property
    def industry_map(self) -> Dict[str, str]:
        if self._industry_map is None:
            self._industry_map = self._parse_industry_map()
        return self._industry_map

    def _parse_industry_map(self) -> Dict[str, str]:
        """从 tdxzs3.cfg 提取所有板块的 代码→名称 映射。"""
        data = self.raw_files.get("tdxzs3.cfg", b"")
        if not data:
            return {}
        text = data.decode("gbk", errors="ignore")
        result: Dict[str, str] = {}
        for line in text.splitlines():
            parts = line.split("|")
            if len(parts) >= 2:
                name = parts[0].strip()
                code = parts[1].strip()
                if code and name:
                    result[code] = name
        return result

    # ── 节假日 ──

    @property
    def holidays(self) -> List[str]:
        if self._holidays is None:
            self._holidays = self._parse_holidays()
        return self._holidays

    def _parse_holidays(self) -> List[str]:
        """从 needini.dat 解析节假日列表（格式：Y{n}=YYYY,MMDD,MMDD,...）。

        注意：中国节假日每年由国务院假日办发布，zhb中未来年份数据是预设值，不可信。
        因此只提取当前年份和前一年的数据，未来年份数据丢弃。
        """
        data = self.raw_files.get("needini.dat", b"")
        if not data:
            return []
        text = data.decode("gbk", errors="ignore")
        result: List[str] = []
        
        current_year = datetime.now().year
        trustable_years = {current_year - 1, current_year}
        
        for line in text.splitlines():
            line = line.strip()
            if line.startswith("Y") and "=" in line:
                parts = line.split("=")
                if len(parts) >= 2:
                    values = parts[1].split(",")
                    if values:
                        try:
                            year = int(values[0])
                            if year not in trustable_years:
                                continue
                            for v in values[1:]:
                                v = v.strip()
                                if len(v) == 4:
                                    date_str = f"{year}{v}"
                                    try:
                                        datetime.strptime(date_str, "%Y%m%d")
                                        result.append(date_str)
                                    except ValueError:
                                        pass
                        except ValueError:
                            continue
        return sorted(set(result))

    # ── tdxstat 全市场统计快照 ──

    @property
    def stock_stats(self) -> Dict[str, Dict[str, Any]]:
        """全市场个股统计快照 {code: {字段名: 值}}。"""
        if self._stock_stats is None:
            self._stock_stats = self._parse_tdxstat()
        return self._stock_stats

    def _parse_tdxstat(self) -> Dict[str, Dict[str, Any]]:
        """解析 tdxstat.cfg（35字段，7938只股票）。

        字段映射（通过对比实时行情验证）：
            [0]  market          市场代码 (0=SZ, 1=SH)
            [1]  code            股票代码
            [2]  change_pct      涨跌幅(%)
            [3]  pe_dynamic      市盈率(动态)
            [4]  date            数据日期
            [5]  unknown_5       未知(小整数)
            [6]  unknown_6       未知
            [7]  unknown_7       未知
            [8]  unknown_8       未知
            [9]  pe_ttm          市盈率TTM
            [10] unknown_10      未知(可能是股息率/ROE)
            [11] unknown_11      未知(大数值)
            [12] unknown_12      未知(部分为日期)
            [13] unknown_13      未知(小整数)
            [14] unknown_14      未知(大数值)
            [15] unknown_15      未知(可能是股东人数)
            [16] unknown_16      未知
            [17] change_5d       5日涨跌幅(%)
            [18] change_10d      10日涨跌幅(%)
            [19] change_20d      20日涨跌幅(%)
            [20] change_30d      30日涨跌幅(%)
            [21] change_60d      60日涨跌幅(%)
            [22] unknown_22      未知
            [23] unknown_23      未知
            [24] volume          成交量(股)
            [25] amount          成交额(万元)
            [26] unknown_26      未知
            [27] unknown_27      未知
            [28] unknown_28      未知
            [29] unknown_29      未知
            [30] unknown_30      未知
            [31-33]              通常为空
            [34] unknown_34      未知
        """
        data = self.raw_files.get("tdxstat.cfg", b"")
        if not data:
            return {}
        text = data.decode("gbk", errors="ignore")
        result: Dict[str, Dict[str, Any]] = {}
        for line in text.splitlines():
            parts = line.split("|")
            if len(parts) < 5:
                continue
            code = parts[1].strip()
            if not code:
                continue

            def _f(idx: int, cast: type = float) -> Any:
                """安全取值并转换类型。"""
                if idx >= len(parts):
                    return None
                v = parts[idx].strip()
                if not v:
                    return None
                try:
                    return cast(v)
                except (ValueError, TypeError):
                    return v

            result[code] = {
                "market": _f(0, int),
                "code": code,
                "change_pct": _f(2, float),
                "pe_dynamic": _f(3, float),
                "date": parts[4].strip() if len(parts) > 4 else "",
                "pe_ttm": _f(9, float),
                "change_5d": _f(17, float),
                "change_10d": _f(18, float),
                "change_20d": _f(19, float),
                "change_30d": _f(20, float),
                "change_60d": _f(21, float),
                "volume": _f(24, float),
                "amount": _f(25, float),
            }
        return result

    def get_stock_stat(self, code: str) -> Optional[Dict[str, Any]]:
        """获取指定股票的统计快照。"""
        return self.stock_stats.get(code)

    # ── tdxstat2 资金流向+板块归属 ──

    @property
    def stock_stats2(self) -> Dict[str, Dict[str, Any]]:
        """全市场资金流向+板块归属 {code: {字段名: 值}}。"""
        if self._stock_stats2 is None:
            self._stock_stats2 = self._parse_tdxstat2()
        return self._stock_stats2

    def _parse_tdxstat2(self) -> Dict[str, Dict[str, Any]]:
        """解析 tdxstat2.cfg（21字段，7938只股票）。

        字段映射（通过对比实时行情验证）：
            [0]  market          市场代码
            [1]  code            股票代码
            [2]  date            数据日期
            [3]  main_inflow     主力净流入(万) - 推测
            [5]  total_amount    总成交额(万) - 推测
            [7]  retail_inflow   散户净流入(万) - 推测
            [9]  big_order_cnt   大单笔数 - 推测
            [10] small_order_cnt 小单笔数 - 推测
            [11] change_pct_alt  涨跌幅(与tdxstat[29]相同)
            [12] change_long     长期涨跌幅(%)
            [13] industry_code   行业板块代码
            [14] unknown_14      未知
            [15] unknown_15      未知
            [16] unknown_16      未知(可能是换手率)
            [17] high_52w        52周最高价 (已验证)
            [18] low_52w         52周最低价 (已验证)
            [19] unknown_19      未知
            [20] unknown_20      未知
        """
        data = self.raw_files.get("tdxstat2.cfg", b"")
        if not data:
            return {}
        text = data.decode("gbk", errors="ignore")
        result: Dict[str, Dict[str, Any]] = {}
        for line in text.splitlines():
            parts = line.split("|")
            if len(parts) < 5:
                continue
            code = parts[1].strip()
            if not code:
                continue

            def _f(idx: int, cast: type = float) -> Any:
                if idx >= len(parts):
                    return None
                v = parts[idx].strip()
                if not v:
                    return None
                try:
                    return cast(v)
                except (ValueError, TypeError):
                    return v

            result[code] = {
                "market": _f(0, int),
                "code": code,
                "date": parts[2].strip() if len(parts) > 2 else "",
                "main_inflow": _f(3, float),
                "total_amount": _f(5, float),
                "retail_inflow": _f(7, float),
                "big_order_cnt": _f(9, int),
                "small_order_cnt": _f(10, int),
                "industry_code": parts[13].strip() if len(parts) > 13 else "",
                "high_52w": _f(17, float),
                "low_52w": _f(18, float),
            }
        return result

    def get_stock_stat2(self, code: str) -> Optional[Dict[str, Any]]:
        """获取指定股票的资金流向和板块归属。"""
        return self.stock_stats2.get(code)

    def get_industry_code(self, code: str) -> str:
        """获取股票的行业板块代码。"""
        s2 = self.stock_stats2.get(code)
        if s2:
            return s2.get("industry_code", "")
        return ""

    # ── tipinfo 财报日历 ──

    @property
    def tip_info(self) -> Dict[str, Dict[str, Any]]:
        """财报日历 {code: {字段名: 值}}。"""
        if self._tip_info is None:
            self._tip_info = self._parse_tipinfo()
        return self._tip_info

    def _parse_tipinfo(self) -> Dict[str, Dict[str, Any]]:
        """解析 tipinfo.dat（22字段，5609只股票）。

        字段映射：
            [0]  market          市场代码
            [1]  code            股票代码
            [2]  report_period   财报期 (如 20260331 = 2026Q1)
            [3]  eps             每股收益(元)
            [4]  disclose_date   财报披露日
            [5]  ex_date_1       除权除息日1
            [6]  ex_date_2       除权除息日2
            [8]  div_date        分红日
            [9]  div_amount      分红金额(每10股, 元)
            [10] unknown_10      未知(日期)
            [11] unknown_11      未知(日期)
            [13] record_date     登记日
            [14] record_amount   登记金额
        """
        data = self.raw_files.get("tipinfo.dat", b"")
        if not data:
            return {}
        text = data.decode("gbk", errors="ignore")
        result: Dict[str, Dict[str, Any]] = {}
        for line in text.splitlines():
            parts = line.split("|")
            if len(parts) < 5:
                continue
            code = parts[1].strip()
            if not code:
                continue

            def _f(idx: int, cast: type = float) -> Any:
                if idx >= len(parts):
                    return None
                v = parts[idx].strip()
                if not v:
                    return None
                try:
                    return cast(v)
                except (ValueError, TypeError):
                    return v

            result[code] = {
                "code": code,
                "report_period": parts[2].strip() if len(parts) > 2 else "",
                "eps": _f(3, float),
                "disclose_date": parts[4].strip() if len(parts) > 4 else "",
                "ex_date": parts[5].strip() if len(parts) > 5 else "",
                "div_date": parts[8].strip() if len(parts) > 8 else "",
                "div_amount": _f(9, float),
            }
        return result

    def get_tip_info(self, code: str) -> Optional[Dict[str, Any]]:
        """获取指定股票的财报日历信息。"""
        return self.tip_info.get(code)

    # ── xgsg 新股申购 ──

    @property
    def ipo_list(self) -> List[Dict[str, Any]]:
        """新股申购日历列表。"""
        if self._ipo_list is None:
            self._ipo_list = self._parse_xgsg()
        return self._ipo_list

    def _parse_xgsg(self) -> List[Dict[str, Any]]:
        """解析 xgsg.cfg（新股申购日历）。

        字段映射：
            [0]  type            类型 (0=申购, 1=上市, 2=已上市)
            [1]  code            股票代码
            [2]  date            申购/上市日期
            [3]  issue_price     发行价
            [4]  issue_volume    发行量(万股)
            [5]  online_volume   上网发行量(万股)
            [14] name            股票名称
            [15] buy_price       申购价
            [16] list_price      上市价
        """
        data = self.raw_files.get("xgsg.cfg", b"")
        if not data:
            return []
        text = data.decode("gbk", errors="ignore")
        result: List[Dict[str, Any]] = []
        for line in text.splitlines():
            parts = line.split("|")
            if len(parts) < 5:
                continue

            def _f(idx: int, cast: type = float) -> Any:
                if idx >= len(parts):
                    return None
                v = parts[idx].strip()
                if not v:
                    return None
                try:
                    return cast(v)
                except (ValueError, TypeError):
                    return v

            result.append({
                "type": _f(0, int),
                "code": parts[1].strip(),
                "date": parts[2].strip(),
                "issue_price": _f(3, float),
                "issue_volume": _f(4, float),
                "online_volume": _f(5, float),
                "name": parts[14].strip() if len(parts) > 14 else "",
                "buy_price": _f(15, float),
                "list_price": _f(16, float),
            })
        return result

    # ── tdxahrate A+H股比价 ──

    @property
    def ah_stocks(self) -> List[Dict[str, str]]:
        """A+H股列表。"""
        if self._ah_stocks is None:
            self._ah_stocks = self._parse_ahrate()
        return self._ah_stocks

    def _parse_ahrate(self) -> List[Dict[str, str]]:
        """解析 tdxahrate.cfg（A+H股比价）。

        格式: A股名称|A股代码|H股代码|类型
        """
        data = self.raw_files.get("tdxahrate.cfg", b"")
        if not data:
            return []
        text = data.decode("gbk", errors="ignore")
        result: List[Dict[str, str]] = []
        for line in text.splitlines():
            parts = line.split("|")
            if len(parts) >= 3:
                result.append({
                    "name": parts[0].strip(),
                    "a_code": parts[1].strip(),
                    "h_code": parts[2].strip(),
                })
        return result

    # ── brkcomp 券商名称表 ──

    @property
    def brokers(self) -> Dict[str, str]:
        """券商ID→简称映射。"""
        if self._brokers is None:
            self._brokers = self._parse_brokers()
        return self._brokers

    def _parse_brokers(self) -> Dict[str, str]:
        """解析 brkcomp.dat（券商名称表）。

        格式: 券商ID|简称|全称
        """
        data = self.raw_files.get("brkcomp.dat", b"")
        if not data:
            return {}
        text = data.decode("gbk", errors="ignore")
        result: Dict[str, str] = {}
        for line in text.splitlines():
            parts = line.split("|")
            if len(parts) >= 2:
                broker_id = parts[0].strip()
                short_name = parts[1].strip()
                if broker_id:
                    result[broker_id] = short_name
        return result

    def get_broker_name(self, broker_id: str) -> str:
        """获取券商简称。"""
        return self.brokers.get(broker_id, broker_id)

    # ── 证监会行业分类（incon.dat）──

    @property
    def csrc_industries(self) -> Dict[str, str]:
        """证监会行业分类 {代码: 名称}。"""
        if self._csrc_industries is None:
            self._csrc_industries = self._parse_csrc_industries()
        return self._csrc_industries

    def _parse_csrc_industries(self) -> Dict[str, str]:
        """解析 incon.dat（证监会行业分类，3703行）。

        格式: 行业代码|行业名称|门类代码|门类名称
        门类: A-农林牧渔, B-采矿业, C-制造业, ... S-综合
        """
        data = self.raw_files.get("incon.dat", b"")
        if not data:
            return {}
        text = data.decode("gbk", errors="ignore")
        result: Dict[str, str] = {}
        for line in text.splitlines():
            parts = line.split("|")
            if len(parts) >= 2:
                code = parts[0].strip()
                name = parts[1].strip()
                if code:
                    result[code] = name
        return result

    # ── 中概股ADR（tdxadr.cfg）──

    @property
    def adr_stocks(self) -> List[Dict[str, str]]:
        """中概股ADR列表。"""
        if self._adr_stocks is None:
            self._adr_stocks = self._parse_adr()
        return self._adr_stocks

    def _parse_adr(self) -> List[Dict[str, str]]:
        """解析 tdxadr.cfg（中概股ADR，30只）。

        格式: A股代码|A股名称|ADR代码|ADR名称
        """
        data = self.raw_files.get("tdxadr.cfg", b"")
        if not data:
            return []
        text = data.decode("gbk", errors="ignore")
        result: List[Dict[str, str]] = []
        for line in text.splitlines():
            parts = line.split("|")
            if len(parts) >= 4:
                result.append({
                    "a_code": parts[0].strip(),
                    "a_name": parts[1].strip(),
                    "adr_code": parts[2].strip(),
                    "adr_name": parts[3].strip(),
                })
        return result

    # ── 可转债（othersg.cfg）──

    @property
    def convertible_bonds(self) -> List[Dict[str, Any]]:
        """可转债列表。"""
        if self._convertible_bonds is None:
            self._convertible_bonds = self._parse_convertible_bonds()
        return self._convertible_bonds

    def _parse_convertible_bonds(self) -> List[Dict[str, Any]]:
        """解析 othersg.cfg（可转债信息）。"""
        data = self.raw_files.get("othersg.cfg", b"")
        if not data:
            return []
        text = data.decode("gbk", errors="ignore")
        result: List[Dict[str, Any]] = []
        for line in text.splitlines():
            parts = line.split("|")
            if len(parts) >= 2:
                result.append({
                    "code": parts[0].strip(),
                    "name": parts[1].strip() if len(parts) > 1 else "",
                })
        return result

    # ── 退市股票对照表（pttab.dat）──

    @property
    def delisted_stocks(self) -> Dict[str, str]:
        """退市股票代码→名称映射。"""
        if self._delisted_stocks is None:
            self._delisted_stocks = self._parse_delisted()
        return self._delisted_stocks

    def _parse_delisted(self) -> Dict[str, str]:
        """解析 pttab.dat（股票代码对照表，含退市股）。"""
        data = self.raw_files.get("pttab.dat", b"")
        if not data:
            return {}
        text = data.decode("gbk", errors="ignore")
        result: Dict[str, str] = {}
        for line in text.splitlines():
            parts = line.split("|")
            if len(parts) >= 2:
                code = parts[0].strip()
                name = parts[1].strip()
                if code:
                    result[code] = name
        return result

    # ── 数据新鲜度 ──

    def is_fresh(self, max_delay_days: int = 3) -> bool:
        """检查数据是否新鲜（延迟在 max_delay_days 天以内）。"""
        if not self.date:
            return False
        try:
            data_date = datetime.strptime(self.date, "%Y%m%d").date()
            today = date.today()
            delay = (today - data_date).days
            return delay <= max_delay_days
        except ValueError:
            return False
# ═══════════════════════════════════════

def _download_zhb_zip() -> Optional[bytes]:
    """从通达信服务器下载 zhb.zip 原始二进制数据。"""
    try:
        from pytdx.hq import TdxHq_API
        from pytdx.parser.get_report_file import GetReportFile
    except ImportError as e:
        _debug_log(f"zhb: pytdx not available: {e}")
        return None

    api = TdxHq_API(auto_retry=True)
    filename = "zhb.zip"

    for ip, port in _ZHB_HOSTS:
        try:
            _debug_log(f"zhb: trying {ip}:{port}")
            if not api.connect(ip, port):
                _debug_log(f"zhb: connect failed {ip}")
                continue

            offset = 0
            chunks: List[bytes] = []

            while True:
                cmd = GetReportFile(api.client)
                cmd.setParams(filename, offset)
                res = cmd.call_api()

                if not res or "chunksize" not in res or res["chunksize"] == 0:
                    break

                chunk_data = res["chunkdata"]
                chunks.append(chunk_data)
                offset += res["chunksize"]

                if res["chunksize"] < 0x7530:
                    break

            api.disconnect()

            if chunks:
                data = b"".join(chunks)
                # 验证是否是有效的 zip
                try:
                    with zipfile.ZipFile(io.BytesIO(data)):
                        pass
                    _debug_log(f"zhb: downloaded {len(data)} bytes from {ip}")
                    return data
                except zipfile.BadZipFile:
                    _debug_log(f"zhb: invalid zip from {ip}, trying next")
                    continue

        except Exception as e:
            _debug_log(f"zhb: download error from {ip}: {e}")
            try:
                api.disconnect()
            except Exception:
                pass
            continue

    _debug_log("zhb: all hosts failed")
    return None


# ═══════════════════════════════════════
# 解析 zhb.zip
# ═══════════════════════════════════════

def _parse_zhb_data(data: bytes) -> Optional[ZhbData]:
    """解析 zhb.zip 二进制数据为 ZhbData 对象。"""
    try:
        zhb = ZhbData()
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            for fname in zf.namelist():
                zhb.raw_files[fname] = zf.read(fname)

        # 从 tdxstat.cfg 提取数据日期
        stat_data = zhb.raw_files.get("tdxstat.cfg", b"")
        if stat_data:
            text = stat_data.decode("gbk", errors="ignore")
            first_line = text.splitlines()[0] if text.splitlines() else ""
            parts = first_line.split("|")
            if len(parts) >= 5:
                zhb.date = parts[4].strip()

        if not zhb.date:
            zhb.date = date.today().strftime("%Y%m%d")

        return zhb
    except Exception as e:
        _debug_log(f"zhb: parse error: {e}")
        return None


# ═══════════════════════════════════════
# 缓存管理
# ═══════════════════════════════════════

def _ensure_cache_dir() -> None:
    if not os.path.exists(_ZHB_CACHE_DIR):
        os.makedirs(_ZHB_CACHE_DIR, exist_ok=True)


def _get_cache_path(date_str: str) -> str:
    return os.path.join(_ZHB_CACHE_DIR, f"zhb_{date_str}.zip")


def _save_to_cache(date_str: str, data: bytes) -> None:
    _ensure_cache_dir()
    tmp_path = _get_cache_path(date_str) + ".tmp"
    final_path = _get_cache_path(date_str)
    try:
        with open(tmp_path, "wb") as f:
            f.write(data)
        os.replace(tmp_path, final_path)
    except Exception as e:
        _debug_log(f"zhb: save cache failed: {e}")
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass


def _cleanup_old_files() -> None:
    """清理 N 天前的旧 zhb 文件。"""
    try:
        _ensure_cache_dir()
        cutoff = time.time() - _KEEP_DAYS * 86400
        for fname in os.listdir(_ZHB_CACHE_DIR):
            fpath = os.path.join(_ZHB_CACHE_DIR, fname)
            if not os.path.isfile(fpath):
                continue
            if not (fname.endswith(".zip") or fname.endswith(".pkl") or fname.endswith(".tmp")):
                continue
            try:
                if os.path.getmtime(fpath) < cutoff:
                    os.remove(fpath)
            except Exception:
                pass
    except Exception as e:
        _debug_log(f"zhb: cleanup error: {e}")


# ═══════════════════════════════════════
# 对外主接口
# ═══════════════════════════════════════

def get_zhb() -> Optional[ZhbData]:
    """获取 zhb 数据（带缓存）。

    优先内存缓存 → 文件缓存 → 在线下载
    下载失败返回 None（调用方需降级处理）。

    V10.0 新增：
        - 进程安全文件锁（防止多进程同时下载）
        - 磁盘空间保护（空间不足时紧急清理）
    """
    global _zhb_memory_cache

    # 内存缓存命中
    with _zhb_cache_lock:
        if _zhb_memory_cache is not None:
            return _zhb_memory_cache

    # 检查磁盘空间
    if not _check_disk_space():
        _debug_log("zhb: disk space insufficient after cleanup")
        # 即使空间不足也尝试加载缓存

    # 获取文件锁（进程安全）
    if not _acquire_file_lock(timeout=30.0):
        _debug_log("zhb: failed to acquire file lock, loading from cache")
    else:
        try:
            # 尝试从服务器下载（拿到的数据日期可能是昨天或更早）
            data = _download_zhb_zip()

            if data:
                zhb = _parse_zhb_data(data)
                if zhb:
                    _save_to_cache(zhb.date, data)
                    _cleanup_old_files()
                    with _zhb_cache_lock:
                        _zhb_memory_cache = zhb
                    return zhb
        finally:
            _release_file_lock()

    # 下载失败，尝试加载最新的缓存文件
    _ensure_cache_dir()
    try:
        cached_files = sorted(
            [f for f in os.listdir(_ZHB_CACHE_DIR) if f.endswith(".zip")],
            reverse=True,
        )
        for fname in cached_files[:3]:  # 试最近的3个
            fpath = os.path.join(_ZHB_CACHE_DIR, fname)
            try:
                with open(fpath, "rb") as f:
                    data = f.read()
                zhb = _parse_zhb_data(data)
                if zhb:
                    _debug_log(f"zhb: using cached {fname}")
                    with _zhb_cache_lock:
                        _zhb_memory_cache = zhb
                    return zhb
            except Exception:
                continue
    except Exception as e:
        _debug_log(f"zhb: load cache fallback failed: {e}")

    return None


def invalidate_cache() -> None:
    """强制失效内存缓存，下次调用重新下载/读取。"""
    global _zhb_memory_cache
    with _zhb_cache_lock:
        _zhb_memory_cache = None


# ═══════════════════════════════════════
# 便捷函数
# ═══════════════════════════════════════

def get_sp_block(name: str) -> List[str]:
    """获取大板块成分股列表（便捷函数）。"""
    zhb = get_zhb()
    if zhb is None:
        return []
    return zhb.get_sp_block(name)


def list_sp_blocks() -> List[tuple]:
    """列出所有大板块（便捷函数）。"""
    zhb = get_zhb()
    if zhb is None:
        return []
    return zhb.list_sp_blocks()


def get_sw_industries() -> Dict[str, str]:
    """获取申万行业列表 {代码: 名称}（便捷函数）。"""
    zhb = get_zhb()
    if zhb is None:
        return {}
    return zhb.sw_industries


def get_industry_map() -> Dict[str, str]:
    """获取行业代码→名称映射（便捷函数）。"""
    zhb = get_zhb()
    if zhb is None:
        return {}
    return zhb.industry_map


# ═══════════════════════════════════════
# 阶段二：B级数据便捷函数
# ═══════════════════════════════════════

def market_stat_snapshot(codes: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
    """全市场（或指定股票）统计快照。

    Args:
        codes: 股票代码列表，None 表示全市场

    Returns:
        {code: {change_pct, pe_dynamic, pe_ttm, change_5d..60d, volume, amount, ...}}
    """
    zhb = get_zhb()
    if zhb is None:
        return {}
    if codes is None:
        return zhb.stock_stats
    return {c: zhb.stock_stats[c] for c in codes if c in zhb.stock_stats}


def get_stock_stat(code: str) -> Optional[Dict[str, Any]]:
    """获取指定股票的统计快照（便捷函数）。"""
    zhb = get_zhb()
    if zhb is None:
        return None
    return zhb.get_stock_stat(code)


def get_stock_stat2(code: str) -> Optional[Dict[str, Any]]:
    """获取指定股票的资金流向和板块归属（便捷函数）。"""
    zhb = get_zhb()
    if zhb is None:
        return None
    return zhb.get_stock_stat2(code)


def get_industry_code(code: str) -> str:
    """获取股票的行业板块代码（便捷函数）。"""
    zhb = get_zhb()
    if zhb is None:
        return ""
    return zhb.get_industry_code(code)


def get_high_52w(code: str) -> Optional[float]:
    """获取52周最高价。"""
    zhb = get_zhb()
    if zhb is None:
        return None
    s2 = zhb.get_stock_stat2(code)
    return s2.get("high_52w") if s2 else None


def get_low_52w(code: str) -> Optional[float]:
    """获取52周最低价。"""
    zhb = get_zhb()
    if zhb is None:
        return None
    s2 = zhb.get_stock_stat2(code)
    return s2.get("low_52w") if s2 else None


def is_data_fresh(max_delay_days: int = 3) -> bool:
    """检查zhb数据是否新鲜。"""
    zhb = get_zhb()
    if zhb is None:
        return False
    return zhb.is_fresh(max_delay_days)


# ═══════════════════════════════════════
# 阶段三：辅助数据便捷函数
# ═══════════════════════════════════════

def get_tip_info(code: str) -> Optional[Dict[str, Any]]:
    """获取指定股票的财报日历信息（便捷函数）。"""
    zhb = get_zhb()
    if zhb is None:
        return None
    return zhb.get_tip_info(code)


def get_ipo_list() -> List[Dict[str, Any]]:
    """获取新股申购日历（便捷函数）。"""
    zhb = get_zhb()
    if zhb is None:
        return []
    return zhb.ipo_list


def get_ah_stocks() -> List[Dict[str, str]]:
    """获取A+H股列表（便捷函数）。"""
    zhb = get_zhb()
    if zhb is None:
        return []
    return zhb.ah_stocks


def get_broker_name(broker_id: str) -> str:
    """获取券商简称（便捷函数）。"""
    zhb = get_zhb()
    if zhb is None:
        return broker_id
    return zhb.get_broker_name(broker_id)


# ═══════════════════════════════════════
# V10.0 新增便捷函数
# ═══════════════════════════════════════

def get_holidays() -> List[str]:
    """获取节假日列表（1991-2030，便捷函数）。

    返回格式为 YYYYMMDD 字符串列表。
    注意：仅作参考，主用 stock_calendar 模块。
    """
    zhb = get_zhb()
    if zhb is None:
        return []
    return zhb.holidays


def get_csrc_industries() -> Dict[str, str]:
    """获取证监会行业分类 {代码: 名称}（便捷函数）。

    共3703个行业分类，涵盖A-S门类。
    """
    zhb = get_zhb()
    if zhb is None:
        return {}
    return zhb.csrc_industries


def get_adr_stocks() -> List[Dict[str, str]]:
    """获取中概股ADR列表（便捷函数）。

    返回: [{'a_code': A股代码, 'a_name': A股名称, 'adr_code': ADR代码, 'adr_name': ADR名称}, ...]
    """
    zhb = get_zhb()
    if zhb is None:
        return []
    return zhb.adr_stocks


def get_convertible_bonds() -> List[Dict[str, Any]]:
    """获取可转债列表（便捷函数）。"""
    zhb = get_zhb()
    if zhb is None:
        return []
    return zhb.convertible_bonds


def get_delisted_stocks() -> Dict[str, str]:
    """获取退市股票代码→名称映射（便捷函数）。"""
    zhb = get_zhb()
    if zhb is None:
        return {}
    return zhb.delisted_stocks


# ═══════════════════════════════════════
# V10.0 智能日期筛选
# ═══════════════════════════════════════

def should_use_zhb_data() -> tuple[bool, str]:
    """根据当前时机判断是否应使用zhb数据。

    Returns:
        (should_use, expected_date): 是否使用zhb，期望的数据日期(YYYYMMDD)

    时间逻辑：
        - 收盘后(15:00后): 使用当日数据
        - 开盘前(9:30前): 使用上一交易日数据
        - 休市日: 使用上一交易日数据
        - 盘中(9:30-15:00): 必须实时获取，返回(False, "")
    """
    from datetime import date, datetime, time
    from stock_common.sc_datasource import is_trading_day
    from stock_common.stock_calendar import get_last_trading_day as get_previous_trading_day

    now = datetime.now()
    today = date.today()
    current_time = now.time()

    if not is_trading_day(today):
        expected = get_previous_trading_day(today)
        return (True, expected.strftime("%Y%m%d"))

    if current_time >= time(15, 0):
        return (True, today.strftime("%Y%m%d"))
    elif current_time < time(9, 30):
        expected = get_previous_trading_day(today)
        return (True, expected.strftime("%Y%m%d"))
    else:
        return (False, "")


def is_zhb_date_matching() -> bool:
    """判断当前zhb数据日期是否符合预期。"""
    zhb = get_zhb()
    if zhb is None or not zhb.date:
        return False
    should_use, expected_date = should_use_zhb_data()
    if not should_use:
        return False
    return zhb.date == expected_date


if __name__ == "__main__":
    print("=== zhb_client.py 自测 ===")
    zhb = get_zhb()
    if zhb is None:
        print("❌ 获取失败")
    else:
        print(f"✅ 数据日期: {zhb.date}")
        print(f"✅ 原始文件数: {len(zhb.raw_files)}")
        print()
        print("=== 大板块列表 ===")
        for name, count in zhb.list_sp_blocks():
            print(f"  {name:20s}  {count:5d} 只")
        print()
        print(f"=== 申万行业数量: {len(zhb.sw_industries)} ===")
        for i, (code, name) in enumerate(list(zhb.sw_industries.items())[:10]):
            print(f"  {code}  {name}")
        if len(zhb.sw_industries) > 10:
            print(f"  ... 共 {len(zhb.sw_industries)} 个")
        print()
        print(f"=== 行业映射总数: {len(zhb.industry_map)} ===")
