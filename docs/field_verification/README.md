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
2. Agent 对昨日/今日数据做 diff(字段值变化、异常值、跨股矛盾)
3. 与 `field_dict.md` 对照,输出 `analysis.md`:
   - 新证据(实测值确认字段意义)
   - 疑点(与字典解释矛盾/单位可疑/数值异常)
   - 未知字段观察(如 zhb `unknown_24`)
4. 用户确认后,把结论回写 `field_dict.md`(状态: ✅实测 / ⚠️推测 / ❓未知 / ❌修正)

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

## 源覆盖状态(2026-08-20 更新, 18 raw 文件)

- ✅ 已采(18 源): ZHB / TDX(TCP+F10×6) / 腾讯 88 / push2(58) / push2_full(114) / ulist239(239 批量) / 新浪 34 / AxData 34 / 财联社(情绪+快讯) / KPL / 板块轮动 / thsdk(仅盘中) / push2ex 涨停炸板池 / 东财人气榜 / datacenter(两融/北向/解禁) / 巨潮互动易 / 研报 reportapi / 龙虎榜
  - 已归档日期: 20260812/13/14/15/19/20(8/16-18 缺采, 8/19 起恢复每日采集)
- ⏳ 待采 / 已知限制:
  - **TdxQuant(官方)**: 需**启动通达信客户端登录**(C:\new_tdx64\TdxW.exe)后在 PYPlugins 环境运行 `user\field_verify_tdxquant.py`(模板已就绪)——8/4 字典 Col[11]/[24]/[25]/[34] 官方确认即此通道
  - **thsdk**: 仅盘中 9:30-15:00 可用(非交易时段行情网关关闭, 服务器策略, 2026-08-19 实测)
  - **东财跌停池 getTopicDTPool**: 明细接口 tc>0 但 pool=[] 空(8/17/8/18/8/19 实测)——数量可用 ZHB 涨跌幅口径兜底, 明细暂缺
  - push2 5 主机字段差异对比: 待 push2 系稳定窗口

## 已确认待办

- [x] 2026-08-12 首次采集(20 股,4 源;push2 半恢复 8/20,见当日 analysis.md)
- [x] 2026-08-12 源补强(10 源: +push2_full 114 字段/新浪/AxData/财联社/KPL/板块轮动/TDX-F10)
- [ ] 巨潮/cninfo 公告分红接入(待采)
- [ ] thsdk 盘中补采(9:30-15:00)
- [ ] push2delay 镜像域估值字段语义核查(f162/f167 与 push2 主域对照)
- [ ] 首轮分析: 重点核对 ZHB Col[12]/Col[14](已完成,见 field_analysis.md);[26]/[31-33] 窗口破解待 9+ 天序列
