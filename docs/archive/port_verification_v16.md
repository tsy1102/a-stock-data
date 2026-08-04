# 端口连通性验证报告（V16 联网实测）

- 验证时间: 2026-08-01 15:14:59
- 测试股票: 600519

| 端口 | 状态 | 详情 | 耗时 |
|:---|:---:|:---|:---:|
| tencent_quote | ✅ | HTTP 200 字段样例: ['贵州茅台', '600519', '1350.60', '1361.76', '1330.03'] | 653.7ms |
| mootdx_tcp | ❌ | RuntimeError: _get_tdx_client 返回 None（服务器探测失败） | 5883.3ms |
| sina_quote | ✅ | HTTP 200 | 376.3ms |
| push2_stock | ❌ | ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote en | 384.2ms |
| datacenter_lhb | ✅ | HTTP 200 | 292.8ms |

## 结论与行动

| 发现 | 影响 | 行动 |
|:---|:---|:---|
| push2 连接级 RemoteDisconnected（HTTP 000 场景）| 参考仓库 FAQ 明确描述：大陆住宅宽带 IP 会被 push2 连接级间歇风控 | ✅ 本系列已把 push2 降为末位（TDX→腾讯→push2）；403/连接退避 max 60s 生效 |
| mootdx TCP 探测失败（_check_tdx 返回 False）| 通达信服务器在此网络不可达/列表失效 | V15.5 计划（15.146 注入 50+ 候选服务器 + 15.148/15.149 空数据换台）必要性确认 |
| 腾讯/新浪/datacenter 正常 | 不封 IP 首选端口与备胎可用 | 端口优先级设计正确：腾讯优先于 push2 |

**验证脚本**: `python scripts/verify_ports.py`（每端口 1-2 请求，可安全重复执行）
