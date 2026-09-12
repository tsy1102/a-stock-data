# 字段实测验证流水线(Field Verification)

> V16.4.1 建立。目标: 用固定股票池的**每日实测数据**,定位 `field_dict.md` 中
> 错误/未知/推测字段,发现统一层未发现的格式与单位错误。

## 原理

同一字段跨 20 只股票 × 多天的实测值呈规律分布(随状态/行业/日期变化);
字段解释错误时,实测值往往自相矛盾(单位差 10 倍/列错位/状态切换时突变)。
逐日记录 + 每日分析 = 让错误暴露。

## 目录结构

```
docs/field_verification/
├── pool.json          # 20 股股票池(固定 15 + 动态 5,动态层每日可换)
├── README.md          # 本文件
└── YYYYMMDD/          # 按天归档
    ├── raw_zhb.json       # ZHB full/stat/stat2/tipinfo 全字段(本地,零网络)
    ├── raw_tdx.json       # TDX TCP 行情/财务快照
    ├── raw_tencent.json   # 腾讯 qt.gtimg 全字段(~88 位)
    ├── raw_push2.json     # 东财 push2 stock/get 全字段(f1-f239)
    ├── meta.json          # 采集时间/各源状态/失败记录
    └── analysis.md        # 当日分析(每日对话产出)
```

## 采集命令

```powershell
python scripts/capture_field_probe.py                 # 采今天(用现有 ZHB 包)
python scripts/capture_field_probe.py --date 20260812 # 指定日期目录
python scripts/capture_field_probe.py --dry-run       # 只显示各源可用性,不发请求
```

注意: 东财 push2 为 0.4rps,20 只约 50s;脚本自动走 sc_network 全局限流。
若东财处于封禁冷却(20h),push2 源留空并在 meta.json 标注,不影响其他源。

## 每日核查流程(固定)

1. 跑采集脚本(约 3-5 分钟,含 ZHB 本地解析 + TDX + 腾讯 + push2)
   ```powershell
   python scripts/capture_field_probe.py                 # 采今天
   ```
2. **跑全源对撞(通用引擎, V17.2.9)**——每次运行自动查询对撞四铁律:
   ```powershell
   python scripts/collide.py                 # 默认近 7 天窗口，全源全字段完整对撞
   python scripts/collide.py --window 14     # 近 14 天窗口
   python scripts/collide.py --all           # 全部历史日期
   python scripts/collide.py --date 20260913 # 指定报告日期戳（默认今天）
   ```
   产物: `docs/field_verification/<date>/<date>_collision_report.md` + `.json`（仅证据/候选, 不改 `field_dict.md`；新定案经字典订正后由 sanctioned 管线 ingest）。
3. **⚠️ ZHB T-1 规则(2026-08-27 固化)**: 采集脚本产出的 `raw_zhb.json` 数据日期恒为
   **T-1(前一日)**。对撞破解时, 严禁拿"当日报告"直接对撞"当日采集的 ZHB"——须用
   **T-1 当日报告** 或验证字段实时性后对撞当日报告(详见 CRACKING_METHODOLOGY.md 〇节)
4. Agent 对昨日/今日数据做 diff(字段值变化、异常值、跨股矛盾)
4. 与 `field_dict.md` 对照,输出 `analysis.md`:
   - 新证据(实测值确认字段意义)
   - 疑点(与字典解释矛盾/单位可疑/数值异常)
   - 未知字段观察(如 zhb `unknown_24`)
5. 用户确认后,把结论回写 `field_dict.md`(状态: ✅实测 / ⚠️推测 / ❓未知 / ❌修正)
6. **⚠️ 命名仲裁守卫（强制阻断, 2026-09-09 固化）**: 回写 `field_dict.md` 前后均须运行
   `python scripts/lint_field_same_number.py --strict-naming`。
   该模式将 **R3 命名缺口升为阻断级（exit≠0）**；**若报 R3 缺口,禁止回写 field_dict.md**,
   须先补登 §12.8.12e 规范表或加数值二级复核标记,再重跑直到 exit 0。
   （默认不带 `--strict-naming` 为 warn 级、不阻断,用于日常检视。）

## 源与限流(依据 sc_network._DOMAIN_LIMITS)

| 源 | 限流 | 备注 |
|---|---|---|
| ZHB | 本地解析 | tdxstat 35 字段/tdxstat2 21 字段/tipinfo 22 字段 |
| TDX TCP | 100ms | 5 台 FULL 白名单 |
| TDX F10 | 100ms | 财务分析/股本/分红(V16.4.1 起) |
| 腾讯 qt.gtimg | 5rps | 批量 60 只/请求,单股 88 字段 |
| 东财 push2/push2delay | 0.4/1.0rps | 全字段 114 字段(f1-f250 显式,push2delay 兜底) |
| 新浪 hq.sinajs | 5rps | 34 字段,需 Referer |
| AxData | 零网络 | 短线指标 34 字段,直读项目 zhb.zip |
| 财联社/KPL/板块轮动 | 3/5rps | 市场级:情绪/涨停天梯/涨停明细/盘口异动 |
| thsdk | 正式账号 | 仅盘中可用(收盘后服务器拒绝) |

## 源覆盖状态(2026-08-26 更新, 19 raw 文件)

- ✅ 已采(19 源): ZHB / TDX(TCP+F10×6) / 腾讯 88 / push2_full(114) / ulist239(239 批量) / 新浪 34 / AxData 34 / 财联社(情绪+快讯) / KPL / 板块轮动 / thsdk(仅盘中) / push2ex 涨停炸板池 / 东财人气榜 / datacenter(两融/北向/解禁) / 巨潮互动易 / 研报 reportapi / 龙虎榜 / fuyao(竞价/池/财务指标/估值) / FTShare(千股千评/董监高/商誉/质押)
  - 已归档日期: 20260812~20260826(工作日连续, 8/16-18 缺采)
- ⏳ 待采 / 已知限制:
  - **TdxQuant(官方)**: 需**启动通达信客户端登录**(C:\new_tdx64\TdxW.exe)后在 PYPlugins 环境运行 `user\field_verify_tdxquant.py`(模板已就绪)——8/4 字典 Col[11]/[24]/[25]/[34] 官方确认即此通道
  - **thsdk**: 仅盘中 9:30-15:00 可用(非交易时段行情网关关闭, 服务器策略)
  - **push2 主域**: 偶发 20h 封禁冷却(2026-08-26 实测全 __error__), push2delay 镜像域正常
  - **ZHB 盘后**: 数据日期恒为 T-1(20260826 采集时=20260825), 需盘后强制同步才刷新

## 破解里程碑

- **2026-08-29 (完整复破解轮)**: 2 项旧假设证伪 + 1 项新结论 + 1 项**自我撤回**（数据 `zhb_20260828` + `20260828/` 19 源）
  - ❌ **腾讯[86]: 恢复 ❓未知**——"主力净买/大单净量(手)"**证伪**(符号∝涨跌仅 40%; \|[86]\|/总手 0.0011);
    **第一版误判的"委差"已撤回**(Pearson +0.965 系 601288 单点绑架: Spearman **−0.012**、留一 Pearson **−0.863 翻号**、对撞精确/1% 均 **0/20**)
  - ❌ **tdxstat[2]: 资金净流入强度证伪**，"量比/换手率"降为 **L4 极弱候选**(Pearson +0.082 / Spearman **−0.371** 异号, 不达标)
  - ✅ **tipinfo[7] = 价格异动标记日 L3**(涨停15.1%/放量33.7% vs 基线1.3%/8%; 除权除息·解禁·财报披露日全 0%)
  - ⚠️ **腾讯[85]: 收紧为"价格类字段" L3 弱**(精确对撞 0/20; 1% 容差 16/20 命中卖一/卖二价族 → 仅证明价格族, 不等于参考价/结算价)
  - ✅ 清理陈旧条目: P1-3([20]/[22]/[23])·P1-4([26]) 实为**已破解**字段, 非未知
  - 🔧 **规则校正**: 对撞规则(用户定义, 唯一一条) = **扫描同日不同源返回的相同数字的字段, 其一已破解则反推同值未知字段即该字段**; 即**同日跨源逐股精确数值相等**(≥8/20), 非"相关性"; 相关性须 Pearson+Spearman 同号且 \|ρ\|>0.6 且留一不翻号
  - 🔧 **表述撤回**: 曾把"**同序号 ≠ 同字段**"写成用户设定的规则 —— **已撤回**。用户未设此规则; 序号只是字段的一种表现形式, "不能单独因序号/字段名一致就默认不同源同序号代表同一字段"属于对对撞规则的**边界澄清**, 不是独立规则
  - 详情: `20260829/analysis.md` | 主程序: `scratch/crack_0829_v3.py` | 对撞扫描器: `scratch/collide_0829.py`
- **2026-08-28 (V17.0.11)**: push2 f86 **破解 = 当日收盘/最后行情时间戳**（Unix 秒）
  - 多日序列逐日+86400(600519: 1787645498→1787904720); 全 20 股换算=当日收盘时刻
  - 复核: f85=流通股本(股)(F10 实际流通A股 1.0000 精确)、f173=加权ROE(fuyao H1 三样本精确)
  - 中报指标入库 18 只(tx65/tx66 终判条件达成)
  - 详情: `20260828/analysis.md`
- **2026-08-27 (V17.0.10b)**: tdxstat Col[33] **破解 = 连板数**（原"涨停类型族 ztlx"证伪）
  - 日期对齐对撞法（用户指引）: 今日采集 ZHB(8/26) 与 8/27 报告天梯对撞, type **20/20 完全匹配**
  - 当日涨停时 Col[31]/[32]/[33] 三字段一致=连板数; 非涨停日 type=None/0, count=累计次数, lianban=历史高位
  - 同步: field_dict Col[31]/[32]/[33] 对撞补强
  - 详情: `20260827/analysis.md`
- **2026-08-26 (V17.0.9)**: tdxstat Col[24] **终极破解 = 货币资金(万元) cash_reserve_wan**
  - F10 资产负债表「货币资金」逐股对照: 600519=535.188亿(100%一致), 17 只有数据全匹配(14 最新期精确+2 报告期差)
  - 跨日恒定根因: 财报季度才更新(静态财务字段); 历史"成交量/总负债/股本"三假设全部证伪
  - 同步: zhb_client 正名 / data_provider·tdx_client 注释 / test_data_zhb 断言 / field_dict 7.3 节+P0-1 关闭
  - 详情: `20260826/analysis.md`

## 已确认待办

- [x] 2026-08-12 首次采集(20 股,4 源;push2 半恢复 8/20,见当日 analysis.md)
- [x] 2026-08-12 源补强(10 源: +push2_full 114 字段/新浪/AxData/财联社/KPL/板块轮动/TDX-F10)
- [x] 2026-08-26 tdxstat Col[24] 破解=货币资金 cash_reserve_wan(V17.0.9)
- [ ] 中报(2026H1)全面披露后复查 600675/688500 cash_reserve_wan 翻期
- [ ] thsdk 盘中补采(9:30-15:00)
- [ ] push2 主域封禁解除后补采对照 f162/f167 估值字段
