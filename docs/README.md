# docs 文档目录说明

> **架构（V16.4.0 字典重构）**：主字典=决策层（字段定义/结论），附录=实证层（实测值/样本/破解数据）。
> 查询字段先看 field_dict（主字典），未找到再看 verify/ 对应附录。

## 目录结构

```
docs/
├── field_dict.md            # 主字段字典（决策层——字段定义/来源/优先级/破解结论）
├── script_data_dict.md      # 脚本应用字典（5 大脚本逐字段获取矩阵/fallback 链）
├── architecture.md          # 项目架构与数据流（Mermaid）
├── roadmap.md               # 版本路线图 + ADR 决策记录
├── domain_glossary.md       # 领域词汇表（术语口径统一）
├── field_verification/      # 字段实测验证流水线（V16.4.1,按天归档）
│   ├── pool.json            # 20 股固定股票池（固定 15 + 动态 5）
│   ├── README.md            # 采集/核查流程说明
│   └── YYYYMMDD/            # 每日:raw_*.json × 18 源 + meta + analysis + field_analysis
├── session_notes/           # 每日会话纪要锚点（V16.4.1,按天归档）
│   ├── README.md            # 纪要保存逻辑与模板
│   └── YYYYMMDD.md          # 当日全部改动/决策/成果/待办
└── verify/                  # 附录（实证层——实测值/样本/破解数据）
    ├── push2_verify.md      # push2 114 字段破解全表（主字典 §12.9.1）
    ├── axdata_verify.md     # AxData 666 字段补齐矩阵（§12.14）
    ├── samples_verify.md    # 24 股样本核实矩阵 + 未知字段破解数据（§12.19）
    ├── tencent_verify.md    # 腾讯 88 字段全复核 + 未知位矩阵（§12.1）
    ├── levistock_field_verify.md  # levistock 26/38 接口实测字段
    ├── thsdk_field_verify.md      # THS SDK 395 ID 字段核实
    ├── client_fields_enum.md      # 客户端字段枚举全景（东财/通达信/同花顺逆向）
    ├── network_servers.md         # 三源服务器清单 + 移动线路实测
    └── data/                # 附录数据文件（JSON）
        ├── tdx_connect_cfg.json           # 通达信 connect.cfg 全表
        ├── ths_dns_cache_20260811.json    # 同花顺 123ths 域名族
        └── tdx_full_retest_20260811.json  # TDX 74 台复测结果
```

## 使用原则

| 场景 | 查阅 |
|:---|:---|
| 字段定义/来源/优先级 | field_dict.md（主字典）|
| 脚本调整前 | script_data_dict.md（逐字段矩阵）|
| 字段实测值/破解数据 | verify/ 对应附录（主字典引用处有链接）|
| 当日采集数据/字段分析 | field_verification/YYYYMMDD/（18 源 raw + field_analysis）|
| 跨日会话上下文恢复 | session_notes/YYYYMMDD.md（每日记忆锚点）|
| 服务器选择/网络诊断 | verify/network_servers.md |
| 客户端字段逆向 | verify/client_fields_enum.md |

## 维护约定

- **新增破解/实测数据** → 写对应附录（不膨胀主字典），主字典加摘要+链接
- **附录索引**：主字典 §12.15.9 登记所有附录（新增附录必须登记）
- **数据文件**（JSON）统一放 `verify/data/`（cache/ 是运行时目录不入库）
- **规范变更**（单位/结构）→ 递增对应缓存 schema 版本（见 cache/README.md）
