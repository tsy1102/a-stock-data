# ZHB 字段字典与回溯核实记录（V16）

> 2026-08-01 建立。对应 `stock_common/sc_zhb.py`（连续 ZHB 回溯补充字段）。
> 用户需求："cache 下有连续的 zhb 文件，可以再次尝试获取未知的字段，并补充在字典中，
> 并且字段在各个 ai 中核实的内容都会发生一点变化，希望能落实。"

---

## 一、连续 ZHB 归档现状

`cache/zhb/` 每日一个 zip 包（实测 2026-08-01）：

| 项 | 值 |
|:---|:---|
| 归档数量 | 9 个 |
| 时间范围 | `zhb_20260721.zip` ~ `zhb_20260731.zip` |
| 包内文件 | 45+ cfg/dat（tdxstat.cfg / tdxstat2.cfg / profile.dat / tdxchain.cfg / neednote.dat / brkseat.dat / ...）|
| 解析入口 | `zhb_client._parse_zhb_data(bytes) -> ZhbData`（懒解析）|
| 数据日期 | 包名日期 = 上一交易日收盘数据（包 `zhb_20260731` 内 `ZhbData.date = "20260731"`）|

## 二、可回溯字段（tdxstat + tdxstat2 合并，以股票代码为 key）

`backtrack_stats(code)` 合并 `ZhbData.stock_stats`（tdxstat.cfg，35 字段）+ `stock_stats2`（tdxstat2.cfg，21 字段）。
实测 000100 合并出 **31 个字段**（当前包 20260731 缺失字段由 20260729 包回溯补充）。

| 字段类别 | 字段名（tdxstat key）| 跨天稳定性 | 允许回溯 |
|:---|:---|:---:|:---:|
| 估值 | `pe_ttm` / `pe_dynamic` / `pb` / `dividend_yield` | 高（T-1 可接受）| ✅ |
| 股本 | `total_shares` / `float_shares` / `market_cap` | 高 | ✅ |
| 阶段涨幅 | `change_5d` / `change_10d` / `change_30d` / `change_60d` / `change_ytd` | 中（跨日变化）| ⚠️ 需注意 |
| 52 周 | `high_52w` / `low_52w` | 高 | ✅ |
| 行业 | `industry_code` | 高 | ✅ |
| 资金流 | `main_net_buy` 等（tdxstat2）| 中 | ⚠️ 需注意 |
| **实时** | `price` / `change_pct` / `amount` / `volume` / `open` / `high` / `low` / `last_close` / `amount_wan` / `change_30d` / `change_60d` | 低 | ❌ **禁用**（sc_zhb 黑名单拦截）|

## 三、回溯 API

```python
from stock_common.sc_zhb import backtrack_field, backtrack_stats, backtrack_with_extractor

# 单字段: 先当前包，缺失回溯更早包（默认最多 5 个）
value, source_date, back_steps = backtrack_field("000100", "pe_ttm", max_back=5)
# → (21.7828, "20260731", 0)   # steps=0 当前包命中

# 整只股票合并: 缺失字段从旧包补齐
merged, source_date, back_steps = backtrack_stats("000100", max_back=5)
# → ({31 字段}, "20260729", 3)  # 3 = 回溯到 3 个包前补齐缺失

# 通用自定义提取器
value, src, steps = backtrack_with_extractor(code, lambda z, c: ..., max_back=5)
```

**回溯来源标记**（写入 `logs/fallback.log`，字段字典核实依据）：
```
zhb backtrack: 000100 field=pe_ttm <- zhb_20260729.zip (steps=3)
zhb backtrack merge: 000100 +5 fields <- zhb_20260729.zip
```

## 四、AI 核实记录（多源交叉）

> 各 AI/数据源对同一字段的口径可能有差异，此处记录已核实结论，避免重复踩坑。

| 字段 | 核实结论 | 来源/日期 |
|:---|:---|:---|
| 腾讯 `43` 字段 | **是振幅% 不是 PB**（网上大量教程写错）| 参考仓库 a-stock-data V3.6 FAQ，2026-07-31 |
| 腾讯 `46` 字段 | **是 PB** | 同上（实测校准）|
| `industry` | push2 `f128` 比 TDX boards 更准（"光学光电"非"光学光电子"）| V15.4 roadmap 15.55，2026-07-30 |
| `pe_ttm` | 项目 get_pe_ttm = **ZHB-only**（V12.6 决策，无 HTTP fallback）| data_provider.py L826 |
| `name` | ZHB tdxstat **不含 name**（用 profile.dat 或 get_stock_name_from_zhb）| 实测 2026-08-01 |
| 北交所老号段 | 43x/83x/87x 基本作废，已迁 920xxx；老码腾讯返僵尸报价 | 参考仓库 FAQ，2026-07-31 |
| **tdxstat Col[24]** | **9 天恒定不变（600519=4878669.14 等）→ 绝非成交量/成交额**，静态数据（疑似历史事件总股本）| 九日验证 2026-08-03（zhb_20260721~31）|
| **tdxstat Col[22]** | **9 天出现 5-6 种代码（非固定行业）**，动态板块归属代码 | 同上 |
| **tdxstat2 Col[11] vs tdxstat Col[17]** | **仅周一(20260727) 100% 相等，其余工作日 ~2%**——ZHB 周一对齐机制 | 同上（强化 7.3 节）|
| **tdxstat2 Col[12] vs tdxstat Col[19]** | 仅 1/9 天相等 → **非 change_60d 重复**，独立未知字段 | 同上 |
| **tdxstat Col[5] streak_days** | 000001 连涨 4→8 天递增（-1→1→2...→8）逻辑正确 | 同上 |
| **tdxstat Col[6/7/8] 涨跌幅滑动对** | 完美 1 日滞后（T/T-1/T-2），9 天全吻合 | 同上 |
| **tdxstat Col[3]/Col[9] PE** | 每日微变（茅台 19.49~20.58），确认 pe_dynamic/pe_ttm | 同上 |
| **结构性缺失** | ZHB 无 `pb`/`total_shares`/`amount_wan` 字段（需 TDX/HTTP），回溯无法补 | sc_zhb 实测 2026-08-03 |
| **backtrack 实测** | 600519 稳定字段当前包命中（steps=0）；000001 需回溯 5 步（src=20260727）| sc_zhb 实测 2026-08-03 |
| **tdxstat Col[14]** | ✅ **= 扣非净利润（万元）** — 14/14 公司与东财 KCFJCXSYJLR 比值=1.000 | **联网核实 2026-08-03**（腾讯+东财 F10）|
| **tdxstat Col[11]** | ❌ 非自由流通股本（Gemini 推断）— Col11/真实流通股本 比率 0.057~0.914 | 同上 |
| **tdxstat Col[24]** | ❌ 非总负债（Gemini 推断）— 30 家仅茅台巧合吻合；不同公司匹配不同报告期净资产/负债 → 报告期不一致快照 | 同上 |
| **tdxstat Col[34]** | ❌ 非优先股 — 工行非零但无优先股 | 同上 |
| **腾讯字段 44/45** | 44=流通市值(亿)、45=总市值(亿) | 同上（工行 44<45 验证）|

> **联网核实教训**：此前"25/28 匹配自由流通股本"基于自编估算值，用真实数据后证伪。
> 单公司巧合吻合（茅台 Col24=总负债 487.87亿）不可靠，必须多公司系统性验证。
> 方法：腾讯 qt.gtimg.cn（市值/价格）+ 东财 datacenter F10（KCFJCXSYJLR 扣非净利润等）。

## 五、与 fix-pipeline 的衔接

- 本模块回溯出的字段可直接用于 `diff_specs/` 中"字段缺失"类 spec 的快速补数
- `backtrack_stats` 的 `back_steps > 0` 表示用到旧包——报告输出可标注 `(ZHB T-2)` 提示数据时效
- 字段核实结论（第四节）应同步到 `docs/field_dict.md` 主字典

## 六、浏览器核对工具（V16.0.2 新增）

> **目的**：通过 Playwright MCP 登录通达信官网，查询个股页面真实数据，与 ZHB 字段逐一对比，
> 为未知字段（Col[11]/Col[22]/Col[24]/Col[34] 等）提供网页级证据。

### 配置（opencode.jsonc mcp 节）

```jsonc
"mcp": {
  "playwright": {
    "type": "local",
    "command": ["npx", "@playwright/mcp@latest"],
    "enabled": true
  }
}
```

- 依赖：Node.js ≥18（本机 v24.15.0）、`npm install -g @playwright/mcp`、`playwright install chromium`
- 浏览器操作权限设为 `ask`（有副作用），快照/截图/控制台为 `allow`（只读）
- 已实测：MCP 服务器启动正常、端口监听正常、Chromium 114.5MiB 已下载

### 核对工作流建议

1. 导航：`browser_navigate` → `https://quote.tdx.com.cn/`（或个股页面）
2. 快照：`browser_snapshot` 提取页面字段（总市值/流通股本/行业/每股收益等）
3. 登录：如需要（`browser_fill` + `browser_click`），会话可持久化
4. 对比：页面值 vs `get_zhb_single_stock_data(code)` 返回值，记录差异到第四节核实表
5. 截图存档：`browser_screenshot` 保存为字段核对证据

### 注意

- 通达信官网数据量有限（核心数据在客户端软件），网页字段不能覆盖全部 ZHB 字段
- 浏览器核对是**补充手段**，主证据链仍是：多公司 API 交叉（腾讯/东财 F10）+ 9日连续验证
- 网页可能需登录/验证码，首次使用需人工介入

## 七、TdxQuant 官方数据接口（V16.0.3 新增，最强验证手段）

> **2026-08-04 打通**：安装通达信金融终端 64 位 V7.73（支持 TQ 策略），
> 通过 HTTP 接口获取**官方行情/财务/股本数据**，与 ZHB 逐一印证——比 API/浏览器更权威。

### 接入方式（HTTP）

```bash
POST http://127.0.0.1:17709/
{"id": 1, "method": "get_more_info", "params": {"stock_code": "600519.SH", "codestr": "600519.SH"}}
```

- **前提**：安装并登录支持 TQ 的客户端（64位金融终端 V7.73 或量化模拟版）
- 客户端安装：官网 → 下载中心 → 金融终端 64位（"支持TQ策略"标注）
- **Python 方式**：`sys.path.append('D:/new_tdx64/PYPlugins/user')` + `from tqcenter import tq`
- 核心函数：`get_more_info`(88字段) / `get_market_data`(K线) / `get_gb_info`(每日股本)

### 已破解字段（官方 88 字段 vs ZHB）

| ZHB 列 | 官方字段 | 含义 | 验证 |
|:---|:---|:---|:---:|
| Col[11] | FreeLtgb | 自由流通股本(万股) | ✓✓ |
| Col[14] | KfEarnMoney | 扣非净利润(万元) | ✓✓ |
| Col[24] | CashZJ | 现金总额(元) | ✓✓ |
| Col[16] | RDInputFee | 研发投入(万元) | ✓✓ |
| Col[25] | PreReceiveZJ | 预收资金(万元) | ✓✓ |
| Col[34] | OtherQYJzc | 其他权益净资产(元) | ✓（工行）|
| Col[22] | ShapeValue | 形态/板块代码 | ~（同日异动）|
| Col[15] | StaffNum | 员工数 | ✓✓ |
| Col[2] | BetaValue | Beta 系数 | ✓（茅台/工行）|

### 官方字段中文含义速查（45+）

| 字段 | 含义 | 字段 | 含义 |
|:---|:---|:---|:---|
| DynaPE | 动态PE | StaticPE_TTM | 静态PE(TTM) |
| DYRatio | 股息率(%) | PB_MRQ | 市净率 |
| HisHigh/HisLow | 52周高/低 | IPO_Price | IPO发行价 |
| Ltsz/Zsz | 流通/总市值(亿) | fHSL | 换手率 |
| ZAF | 当日涨跌幅 | ZAFPre5/10/20/30/60 | 5/10/20/30/60日涨幅 |
| ZAFYear | 年初涨幅 | ZAFPreOneYear | 年度涨幅 |
| MA5Value | 5日均线 | MainBusiness | 主营业务 |
| ReportDate | 报告期 | StaffNum | 员工数 |
| BetaValue | Beta系数 | OpenAmo | 开盘成交额 |
| fLianB | 连板数 | vzangsu | 涨速 |

## 八、限流经验总结（2026-08-04 实测，重要！）

### 8.1 TdxQuant HTTP 接口的限流特性

**实测发现（关键）**：
1. **同进程连续调用会失败**：`requests.post` 在同一 python 进程内连续调用 3 次，第 2 次起返回空/None——**TQ 会话状态与进程绑定**
2. **独立进程每次成功**：每次调用用新 python 进程（subprocess），100% 成功
3. **需要双参数**：`get_more_info` 必须同时传 `stock_code` + `codestr`（只传一个报 "codestr error"）
4. **间隔要求**：进程间调用建议间隔 ≥3 秒
5. **run_id 递增**：HTTP 请求的 `id` 字段应递增（固定 id=1 在同一连接中可能冲突）

**正确调用模式**：
```python
# 每次独立进程（可靠）
subprocess.run([sys.executable, '-c', '''
    import requests
    r = requests.post("http://127.0.0.1:17709/", 
        json={"id": 1, "method": "get_more_info",
              "params": {"stock_code": "600519.SH", "codestr": "600519.SH"}}, timeout=30)
    print(r.text)
'''], capture_output=True, timeout=40)
```

### 8.2 对脚本 tdx 接口的影响评估

**当前项目脚本（get_*_report.py）的 TDX 调用**：
- `tdx_get_security_bars` / `tdx_get_quote_full` 等走 **mootdx TCP 协议**（直连 7709 端口行情服务器），**不经过 TdxQuant HTTP**——不受此限流影响 ✅
- `_TDX_CALL_LOCK` + `_tdx_throttle()`（`TDX_MIN_INTERVAL=0.1s`，config.py:22）已保护 TCP 调用 ✅
- 东财接口另有 `EM_MIN_INTERVAL=1.0s`（config.py:25）+ `sc_network._DOMAIN_LIMITS` 18 域名分级限流 ✅

**结论**：**现有脚本无需调整**——它们用 mootdx TCP，不是 TdxQuant HTTP。

**若未来接入 TdxQuant（建议）**：
1. 封装独立模块 `tdx_quant_client.py`：每次调用 subprocess + 3s 间隔
2. 或复用 tqcenter 的 `_auto_initialize` 机制（同进程内自动重连）
3. 批量取数时串行 + 间隔（参考本项目东财限流经验）
4. 复用 `sc_network` 的限流框架（`_DOMAIN_LIMITS` 加 127.0.0.1:17709 条目）

### 8.3 通用限流教训（跨数据源）

| 教训 | 来源 |
|:---|:---|
| 同进程连续调用可能失败 → 独立进程更可靠 | TdxQuant |
| 双参数/正确参数名是硬要求（codestr+stock_code） | TdxQuant |
| 密集请求触发 IP 封禁 → 换 IP 恢复 | 东财 push2 |
| 接口抖动 vs 代码 bug 要区分（风控跳过而非失败） | 东财/腾讯 |
| 每次请求用递增 id | TdxQuant |

