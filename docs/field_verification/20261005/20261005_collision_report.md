# 全源对撞报告（20261005）

> 行情窗口：20260812 ~ 20260930（32 个不同交易日）｜字段 1558 个｜样本值 1203936 条
> 新闻/公告自然日窗口：20260812 ~ 20261005
> 主攻目标（unverified）=714｜新增 L1/L1-U 定案=275｜异号同义 419 / 同号镜像 0

> **规则**：每个定案日有效样本≥18，命中率≥90%，至少 3 个独立交易日/自然事件日；同一来源族不作为跨源证据；盘中快照不计入 L1。（详见 `COLLISION_RULES.md`）。本引擎只发现、不写字典；新定案经 field_dict.md 订正后由 sanctioned 管线 ingest。

---

## 一、L1 / L1-U 定案候选 — 异号同义（跨编号，高价值）(419)

| 左字段(unverified) | 右字段 | 等级 | 命中率 | 天数 | 样本 | 比值 | hub | registry |
|:--|:--|:--|--:|--:|--:|--:|:--|:--|
| `tencent[2]` | `ulist239.f12` | L1 | 100.00% | 28 | 557 | - |  | ✅ |
| `ulist239.f8` | `tencent[38]` | L1 | 100.00% | 28 | 557 | - |  | ✅ |
| `ulist239.f12` | `tencent[2]` | L1 | 100.00% | 28 | 557 | - |  | ✅ |
| `push2_full.f48` | `ulist239.f6` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f49` | `ulist239.f34` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f50` | `ulist239.f10` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f51` | `tencent[47]` | L1 | 100.00% | 24 | 477 | - |  | ✅ |
| `push2_full.f52` | `tencent[48]` | L1 | 100.00% | 24 | 477 | - |  | ✅ |
| `push2_full.f55` | `ulist239.f112` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f57` | `tencent[2]` | L1 | 100.00% | 24 | 477 | - |  | ✅ |
| `push2_full.f57` | `ulist239.f12` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f86` | `ulist239.f124` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f92` | `ulist239.f113` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f104` | `ulist239.f132` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f105` | `ulist239.f45` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f111` | `ulist239.f19` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f112` | `ulist239.f19` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f116` | `ulist239.f20` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f117` | `ulist239.f21` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f119` | `ulist239.f109` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f120` | `ulist239.f110` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f121` | `ulist239.f24` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f122` | `ulist239.f25` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f127` | `ulist239.f100` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f128` | `ulist239.f102` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f137` | `ulist239.f62` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f140` | `ulist239.f66` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f141` | `ulist239.f70` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f142` | `ulist239.f71` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f143` | `ulist239.f72` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f144` | `ulist239.f76` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f145` | `ulist239.f77` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f146` | `ulist239.f78` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f147` | `ulist239.f82` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f148` | `ulist239.f83` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f149` | `ulist239.f84` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f161` | `ulist239.f35` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f162` | `ulist239.f9` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f163` | `ulist239.f114` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f164` | `ulist239.f115` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f167` | `ulist239.f23` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f168` | `tencent[38]` | L1 | 100.00% | 24 | 477 | - |  | ✅ |
| `push2_full.f168` | `ulist239.f8` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f169` | `ulist239.f4` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f170` | `ulist239.f3` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f171` | `ulist239.f7` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f175` | `tencent[68]` | L1 | 100.00% | 24 | 477 | - |  | ✅ |
| `push2_full.f177` | `ulist239.f148` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f181` | `ulist239.f111` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f182` | `ulist239.f139` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f183` | `ulist239.f40` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f184` | `ulist239.f41` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f185` | `ulist239.f46` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f186` | `ulist239.f49` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f187` | `ulist239.f129` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f188` | `ulist239.f57` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f189` | `ulist239.f26` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f190` | `ulist239.f48` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f191` | `ulist239.f33` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f193` | `ulist239.f184` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f194` | `ulist239.f69` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f195` | `ulist239.f75` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f196` | `ulist239.f81` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f197` | `ulist239.f87` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `tencent[2]` | `push2_full.f57` | L1 | 100.00% | 24 | 477 | - |  | ✅ |
| `ulist239.f3` | `push2_full.f170` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `ulist239.f4` | `push2_full.f169` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `ulist239.f7` | `push2_full.f171` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `ulist239.f8` | `push2_full.f168` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `ulist239.f9` | `push2_full.f162` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `ulist239.f10` | `push2_full.f50` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `ulist239.f12` | `push2_full.f57` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `ulist239.f19` | `push2_full.f111` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `ulist239.f19` | `push2_full.f112` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `ulist239.f23` | `push2_full.f167` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `ulist239.f24` | `push2_full.f121` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `ulist239.f25` | `push2_full.f122` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `ulist239.f26` | `push2_full.f189` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `ulist239.f40` | `push2_full.f183` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `ulist239.f41` | `push2_full.f184` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `ulist239.f45` | `push2_full.f105` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `ulist239.f46` | `push2_full.f185` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `ulist239.f48` | `push2_full.f190` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `ulist239.f49` | `push2_full.f186` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `ulist239.f57` | `push2_full.f188` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `ulist239.f62` | `push2_full.f137` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `ulist239.f66` | `push2_full.f140` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `ulist239.f69` | `push2_full.f194` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `ulist239.f70` | `push2_full.f141` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `ulist239.f71` | `push2_full.f142` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `ulist239.f72` | `push2_full.f143` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `ulist239.f75` | `push2_full.f195` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `ulist239.f76` | `push2_full.f144` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `ulist239.f77` | `push2_full.f145` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `ulist239.f78` | `push2_full.f146` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `ulist239.f81` | `push2_full.f196` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `ulist239.f82` | `push2_full.f147` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `ulist239.f83` | `push2_full.f148` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `ulist239.f84` | `push2_full.f149` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `ulist239.f87` | `push2_full.f197` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `ulist239.f100` | `push2_full.f127` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `ulist239.f102` | `push2_full.f128` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `ulist239.f109` | `push2_full.f119` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `ulist239.f111` | `push2_full.f181` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `ulist239.f112` | `push2_full.f55` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `ulist239.f113` | `push2_full.f92` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `ulist239.f114` | `push2_full.f163` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `ulist239.f115` | `push2_full.f164` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `ulist239.f124` | `push2_full.f86` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `ulist239.f129` | `push2_full.f187` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `ulist239.f132` | `push2_full.f104` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `ulist239.f139` | `push2_full.f182` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `ulist239.f148` | `push2_full.f177` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `ulist239.f184` | `push2_full.f193` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `fuyao.valuation.pcf_ttm` | `ulist239.f131` | L1 | 100.00% | 23 | 460 | - |  | ✅ |
| `ulist239.f4` | `fuyao.snapshot.price_change` | L1 | 100.00% | 23 | 460 | - |  | ✅ |
| `ulist239.f131` | `fuyao.valuation.pcf_ttm` | L1 | 100.00% | 23 | 460 | - |  | ✅ |
| `ulist239.f109` | `zhb.full.change_5d` | L1 | 100.00% | 22 | 440 | - |  | ✅ |
| `ulist239.f109` | `zhb.stat.change_5d` | L1 | 100.00% | 22 | 440 | - |  | ✅ |
| `ulist239.f160` | `zhb.full.change_10d` | L1 | 100.00% | 22 | 440 | - |  | ✅ |
| `ulist239.f160` | `zhb.stat.change_10d` | L1 | 100.00% | 22 | 440 | - |  | ✅ |
| `push2_full.f119` | `zhb.full.change_5d` | L1 | 100.00% | 20 | 398 | - |  | ✅ |
| `push2_full.f119` | `zhb.stat.change_5d` | L1 | 100.00% | 20 | 398 | - |  | ✅ |
| `push2_full.f120` | `zhb.full.change_20d` | L1 | 100.00% | 20 | 398 | - |  | ✅ |
| `push2_full.f120` | `zhb.full.change_30d` | L1 | 100.00% | 20 | 398 | - |  | ✅ |
| `push2_full.f120` | `zhb.stat.change_20d` | L1 | 100.00% | 20 | 398 | - |  | ✅ |
| `push2_full.f120` | `zhb.stat.change_30d` | L1 | 100.00% | 20 | 398 | - |  | ✅ |
| `push2_full.f175` | `zhb.full.low_52w` | L1 | 100.00% | 20 | 398 | - |  | ✅ |
| `push2_full.f175` | `zhb.stat2.low_52w` | L1 | 100.00% | 20 | 398 | - |  | ✅ |
| `push2_full.f48` | `fuyao.snapshot.turnover` | L1 | 100.00% | 19 | 380 | - |  | ✅ |
| `push2_full.f169` | `fuyao.snapshot.price_change` | L1 | 100.00% | 19 | 380 | - |  | ✅ |
| `em_fund_flow.f137` | `ulist239.f62` | L1 | 100.00% | 14 | 280 | - |  | ✅ |
| `em_fund_flow.f140` | `ulist239.f66` | L1 | 100.00% | 14 | 280 | - |  | ✅ |
| `em_fund_flow.f141` | `ulist239.f70` | L1 | 100.00% | 14 | 280 | - |  | ✅ |
| `em_fund_flow.f142` | `ulist239.f71` | L1 | 100.00% | 14 | 280 | - |  | ✅ |
| `em_fund_flow.f143` | `ulist239.f72` | L1 | 100.00% | 14 | 280 | - |  | ✅ |
| `em_fund_flow.f144` | `ulist239.f76` | L1 | 100.00% | 14 | 280 | - |  | ✅ |
| `em_fund_flow.f145` | `ulist239.f77` | L1 | 100.00% | 14 | 280 | - |  | ✅ |
| `em_fund_flow.f146` | `ulist239.f78` | L1 | 100.00% | 14 | 280 | - |  | ✅ |
| `em_fund_flow.f149` | `ulist239.f84` | L1 | 100.00% | 14 | 280 | - |  | ✅ |
| `ulist239.f62` | `em_fund_flow.f137` | L1 | 100.00% | 14 | 280 | - |  | ✅ |
| `ulist239.f66` | `em_fund_flow.f140` | L1 | 100.00% | 14 | 280 | - |  | ✅ |
| `ulist239.f70` | `em_fund_flow.f141` | L1 | 100.00% | 14 | 280 | - |  | ✅ |
| `ulist239.f71` | `em_fund_flow.f142` | L1 | 100.00% | 14 | 280 | - |  | ✅ |
| `ulist239.f72` | `em_fund_flow.f143` | L1 | 100.00% | 14 | 280 | - |  | ✅ |
| `ulist239.f76` | `em_fund_flow.f144` | L1 | 100.00% | 14 | 280 | - |  | ✅ |
| `ulist239.f77` | `em_fund_flow.f145` | L1 | 100.00% | 14 | 280 | - |  | ✅ |
| `ulist239.f78` | `em_fund_flow.f146` | L1 | 100.00% | 14 | 280 | - |  | ✅ |
| `ulist239.f84` | `em_fund_flow.f149` | L1 | 100.00% | 14 | 280 | - |  | ✅ |
| `em_fund_flow.f147` | `ulist239.f82` | L1 | 100.00% | 11 | 220 | - |  | ✅ |
| `em_fund_flow.f148` | `ulist239.f83` | L1 | 100.00% | 11 | 220 | - |  | ✅ |
| `ulist239.f82` | `em_fund_flow.f147` | L1 | 100.00% | 11 | 220 | - |  | ✅ |
| `ulist239.f83` | `em_fund_flow.f148` | L1 | 100.00% | 11 | 220 | - |  | ✅ |
| `tdx.quote_full.limit_down_price` | `tencent[48]` | L1 | 100.00% | 9 | 178 | - |  | ✅ |
| `push2.f47` | `ulist239.f5` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f48` | `fuyao.snapshot.turnover` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f48` | `sina[9]` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f48` | `ulist239.f6` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f49` | `ulist239.f34` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f50` | `tencent[49]` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f50` | `ulist239.f10` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f51` | `tencent[47]` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f52` | `tencent[48]` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f55` | `ulist239.f112` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f57` | `tencent[2]` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f57` | `ulist239.f12` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f71` | `tencent[51]` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f86` | `ulist239.f124` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f92` | `ulist239.f113` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f104` | `ulist239.f132` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f105` | `ulist239.f45` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f111` | `ulist239.f19` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f112` | `ulist239.f19` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f116` | `ulist239.f20` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f117` | `ulist239.f21` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f119` | `tencent[63]` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f119` | `ulist239.f109` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f120` | `ulist239.f110` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f121` | `ulist239.f24` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f122` | `ulist239.f25` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f127` | `ulist239.f100` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f128` | `ulist239.f102` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f137` | `ulist239.f62` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f140` | `ulist239.f66` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f141` | `ulist239.f70` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f142` | `ulist239.f71` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f143` | `ulist239.f72` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f144` | `ulist239.f76` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f145` | `ulist239.f77` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f146` | `ulist239.f78` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f147` | `ulist239.f82` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f148` | `ulist239.f83` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f149` | `ulist239.f84` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f161` | `ulist239.f35` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f162` | `tencent[52]` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f162` | `ulist239.f9` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f163` | `tencent[53]` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f164` | `ulist239.f115` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f167` | `ulist239.f23` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f168` | `tencent[38]` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f168` | `ulist239.f8` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f169` | `fuyao.snapshot.price_change` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f169` | `tdx.quote_full.change_amt` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f169` | `tencent[31]` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f169` | `ulist239.f4` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f170` | `tencent[32]` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f170` | `ulist239.f3` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f171` | `tencent[43]` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f171` | `ulist239.f7` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f173` | `ulist239.f37` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f177` | `ulist239.f148` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f181` | `ulist239.f111` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f182` | `ulist239.f139` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f183` | `ulist239.f40` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f184` | `ulist239.f41` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f185` | `ulist239.f46` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f186` | `ulist239.f49` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f187` | `ulist239.f129` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f188` | `ulist239.f57` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f189` | `ulist239.f26` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f190` | `ulist239.f48` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f191` | `ulist239.f33` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f193` | `ulist239.f184` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f194` | `ulist239.f69` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f195` | `ulist239.f75` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f196` | `ulist239.f81` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f197` | `ulist239.f87` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `tencent[2]` | `push2.f57` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `tencent[31]` | `push2.f169` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `tencent[32]` | `push2.f170` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `ulist239.f3` | `push2.f170` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `ulist239.f4` | `push2.f169` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `ulist239.f7` | `push2.f171` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `ulist239.f8` | `push2.f168` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `ulist239.f9` | `push2.f162` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `ulist239.f10` | `push2.f50` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `ulist239.f12` | `push2.f57` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `ulist239.f19` | `push2.f111` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `ulist239.f19` | `push2.f112` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `ulist239.f23` | `push2.f167` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `ulist239.f24` | `push2.f121` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `ulist239.f25` | `push2.f122` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `ulist239.f26` | `push2.f189` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `ulist239.f37` | `push2.f173` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `ulist239.f40` | `push2.f183` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `ulist239.f41` | `push2.f184` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `ulist239.f45` | `push2.f105` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `ulist239.f46` | `push2.f185` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `ulist239.f48` | `push2.f190` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `ulist239.f49` | `push2.f186` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `ulist239.f57` | `push2.f188` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `ulist239.f62` | `push2.f137` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `ulist239.f66` | `push2.f140` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `ulist239.f69` | `push2.f194` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `ulist239.f70` | `push2.f141` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `ulist239.f71` | `push2.f142` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `ulist239.f72` | `push2.f143` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `ulist239.f75` | `push2.f195` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `ulist239.f76` | `push2.f144` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `ulist239.f77` | `push2.f145` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `ulist239.f78` | `push2.f146` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `ulist239.f81` | `push2.f196` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `ulist239.f82` | `push2.f147` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `ulist239.f83` | `push2.f148` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `ulist239.f84` | `push2.f149` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `ulist239.f87` | `push2.f197` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `ulist239.f100` | `push2.f127` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `ulist239.f102` | `push2.f128` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `ulist239.f109` | `push2.f119` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `ulist239.f111` | `push2.f181` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `ulist239.f112` | `push2.f55` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `ulist239.f113` | `push2.f92` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `ulist239.f115` | `push2.f164` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `ulist239.f124` | `push2.f86` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `ulist239.f129` | `push2.f187` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `ulist239.f132` | `push2.f104` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `ulist239.f139` | `push2.f182` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `ulist239.f148` | `push2.f177` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `ulist239.f184` | `push2.f193` | L1 | 100.00% | 6 | 120 | - |  | ✅ |
| `push2.f48` | `eltdx.quote_snapshot.amount` | L1 | 100.00% | 5 | 90 | - |  | ✅ |
| `push2.f119` | `zhb.full.change_5d` | L1 | 100.00% | 4 | 80 | - |  | ✅ |
| `push2.f119` | `zhb.stat.change_5d` | L1 | 100.00% | 4 | 80 | - |  | ✅ |
| `push2.f120` | `zhb.full.change_20d` | L1 | 100.00% | 4 | 80 | - |  | ✅ |
| `push2.f120` | `zhb.full.change_30d` | L1 | 100.00% | 4 | 80 | - |  | ✅ |
| `push2.f120` | `zhb.stat.change_20d` | L1 | 100.00% | 4 | 80 | - |  | ✅ |
| `push2.f120` | `zhb.stat.change_30d` | L1 | 100.00% | 4 | 80 | - |  | ✅ |
| `push2.f121` | `zhb.full.change_60d` | L1 | 100.00% | 4 | 80 | - |  | ✅ |
| `push2.f121` | `zhb.stat.change_60d` | L1 | 100.00% | 4 | 80 | - |  | ✅ |
| `push2.f170` | `zhb.full.change_pct` | L1 | 100.00% | 4 | 80 | - |  | ✅ |
| `push2.f170` | `zhb.stat.change_pct` | L1 | 100.00% | 4 | 80 | - |  | ✅ |
| `push2.f175` | `zhb.full.low_52w` | L1 | 100.00% | 4 | 80 | - |  | ✅ |
| `push2.f175` | `zhb.stat2.low_52w` | L1 | 100.00% | 4 | 80 | - |  | ✅ |
| `push2_full.f48` | `eltdx.quote_snapshot.amount` | L1 | 100.00% | 4 | 72 | - |  | ✅ |
| `tencent[32]` | `zhb.full.change_pct` | L1 | 99.78% | 23 | 457 | - |  | ✅ |
| `tencent[32]` | `zhb.stat.change_pct` | L1 | 99.78% | 23 | 457 | - |  | ✅ |
| `ulist239.f3` | `zhb.full.change_pct` | L1 | 99.77% | 22 | 440 | - |  | ✅ |
| `ulist239.f3` | `zhb.stat.change_pct` | L1 | 99.77% | 22 | 440 | - |  | ✅ |
| `push2_full.f170` | `zhb.full.change_pct` | L1 | 99.75% | 20 | 398 | - |  | ✅ |
| `push2_full.f170` | `zhb.stat.change_pct` | L1 | 99.75% | 20 | 398 | - |  | ✅ |
| `tencent[31]` | `ulist239.f4` | L1 | 99.64% | 28 | 557 | - |  | ✅ |
| `tencent[32]` | `ulist239.f3` | L1 | 99.64% | 28 | 557 | - |  | ✅ |
| `ulist239.f3` | `tencent[32]` | L1 | 99.64% | 28 | 557 | - |  | ✅ |
| `ulist239.f4` | `tencent[31]` | L1 | 99.64% | 28 | 557 | - |  | ✅ |
| `ulist239.f7` | `tencent[43]` | L1 | 99.64% | 28 | 557 | - |  | ✅ |
| `ulist239.f10` | `tencent[49]` | L1 | 99.64% | 28 | 557 | - |  | ✅ |
| `push2_full.f48` | `sina[9]` | L1 | 99.58% | 24 | 478 | - |  | ✅ |
| `push2_full.f50` | `tencent[49]` | L1 | 99.58% | 24 | 477 | - |  | ✅ |
| `push2_full.f71` | `tencent[51]` | L1 | 99.58% | 24 | 477 | - |  | ✅ |
| `push2_full.f162` | `tencent[52]` | L1 | 99.58% | 24 | 477 | - |  | ✅ |
| `push2_full.f169` | `tencent[31]` | L1 | 99.58% | 24 | 477 | - |  | ✅ |
| `push2_full.f170` | `tencent[32]` | L1 | 99.58% | 24 | 477 | - |  | ✅ |
| `push2_full.f171` | `tencent[43]` | L1 | 99.58% | 24 | 477 | - |  | ✅ |
| `tencent[31]` | `push2_full.f169` | L1 | 99.58% | 24 | 477 | - |  | ✅ |
| `tencent[32]` | `push2_full.f170` | L1 | 99.58% | 24 | 477 | - |  | ✅ |
| `ulist239.f9` | `tencent[52]` | L1 | 99.46% | 28 | 557 | - |  | ✅ |
| `ulist239.f109` | `tencent[63]` | L1 | 99.46% | 28 | 557 | - |  | ✅ |
| `push2_full.f119` | `tencent[63]` | L1 | 99.37% | 24 | 477 | - |  | ✅ |
| `push2.f163` | `ulist239.f114` | L1 | 99.17% | 6 | 120 | - |  | ✅ |
| `push2.f175` | `tencent[68]` | L1 | 99.17% | 6 | 120 | - |  | ✅ |
| `ulist239.f114` | `push2.f163` | L1 | 99.17% | 6 | 120 | - |  | ✅ |
| `push2_full.f163` | `tencent[53]` | L1 | 98.95% | 24 | 477 | - |  | ✅ |
| `ulist239.f160` | `tencent[69]` | L1 | 98.92% | 28 | 557 | - |  | ✅ |
| `ulist239.f114` | `tencent[53]` | L1 | 98.56% | 28 | 557 | - |  | ✅ |
| `tdx.quote_full.limit_up` | `tencent[47]` | L1 | 98.45% | 13 | 258 | - |  | ✅ |
| `ulist239.f115` | `tencent[39]` | L1 | 98.38% | 28 | 557 | - |  | ✅ |
| `push2.f120` | `tencent[70]` | L1 | 98.33% | 6 | 120 | - |  | ✅ |
| `push2_full.f164` | `tencent[39]` | L1 | 98.32% | 24 | 477 | - |  | ✅ |
| `push2_full.f51` | `tdx.quote_full.limit_up` | L1 | 98.17% | 11 | 218 | - |  | ✅ |
| `tdx.quote_full.limit_up` | `push2_full.f51` | L1 | 98.17% | 11 | 218 | - |  | ✅ |
| `push2_full.f173` | `ulist239.f37` | L1 | 98.12% | 24 | 478 | - |  | ✅ |
| `ulist239.f37` | `push2_full.f173` | L1 | 98.12% | 24 | 478 | - |  | ✅ |
| `tdx.quote_full.amplitude_pct` | `tencent[43]` | L1 | 97.75% | 9 | 178 | - |  | ✅ |
| `push2.f164` | `zhb.full.pe_dynamic` | L1 | 97.50% | 4 | 80 | - |  | ✅ |
| `push2.f164` | `zhb.stat.pe_dynamic` | L1 | 97.50% | 4 | 80 | - |  | ✅ |
| `tencent[31]` | `tdx.quote_full.change_amt` | L1 | 97.15% | 30 | 597 | - |  | ✅ |
| `sina[13]` | `tencent[11]` | L1 | 96.98% | 30 | 597 | - |  | ✅ |
| `sina[15]` | `tencent[13]` | L1 | 96.98% | 30 | 597 | - |  | ✅ |
| `sina[17]` | `tencent[15]` | L1 | 96.98% | 30 | 597 | - |  | ✅ |
| `sina[19]` | `tencent[17]` | L1 | 96.98% | 30 | 597 | - |  | ✅ |
| `sina[23]` | `tencent[21]` | L1 | 96.98% | 30 | 597 | - |  | ✅ |
| `sina[25]` | `tencent[23]` | L1 | 96.98% | 30 | 597 | - |  | ✅ |
| `sina[27]` | `tencent[25]` | L1 | 96.98% | 30 | 597 | - |  | ✅ |
| `sina[29]` | `tencent[27]` | L1 | 96.98% | 30 | 597 | - |  | ✅ |
| `tencent[11]` | `sina[13]` | L1 | 96.98% | 30 | 597 | - |  | ✅ |
| `tencent[13]` | `sina[15]` | L1 | 96.98% | 30 | 597 | - |  | ✅ |
| `tencent[15]` | `sina[17]` | L1 | 96.98% | 30 | 597 | - |  | ✅ |
| `tencent[17]` | `sina[19]` | L1 | 96.98% | 30 | 597 | - |  | ✅ |
| `tencent[21]` | `sina[23]` | L1 | 96.98% | 30 | 597 | - |  | ✅ |
| `tencent[23]` | `sina[25]` | L1 | 96.98% | 30 | 597 | - |  | ✅ |
| `tencent[25]` | `sina[27]` | L1 | 96.98% | 30 | 597 | - |  | ✅ |
| `tencent[27]` | `sina[29]` | L1 | 96.98% | 30 | 597 | - |  | ✅ |
| `push2.f164` | `tencent[39]` | L1 | 96.67% | 6 | 120 | - |  | ✅ |
| `ulist239.f4` | `tdx.quote_full.change_amt` | L1 | 96.61% | 28 | 560 | - |  | ✅ |
| `push2_full.f120` | `tencent[70]` | L1 | 96.44% | 24 | 477 | - |  | ✅ |
| `ulist239.f24` | `zhb.full.change_60d` | L1 | 96.36% | 22 | 440 | - |  | ✅ |
| `ulist239.f24` | `zhb.stat.change_60d` | L1 | 96.36% | 22 | 440 | - |  | ✅ |
| `push2_full.f121` | `zhb.full.change_60d` | L1 | 96.23% | 20 | 398 | - |  | ✅ |
| `push2_full.f121` | `zhb.stat.change_60d` | L1 | 96.23% | 20 | 398 | - |  | ✅ |
| `tencent[19]` | `sina[21]` | L1 | 96.15% | 30 | 597 | - |  | ✅ |
| `push2_full.f169` | `tdx.quote_full.change_amt` | L1 | 96.03% | 24 | 478 | - |  | ✅ |
| `sina[8]` | `fuyao.snapshot.volume` | L1 | 96.00% | 25 | 500 | - |  | ✅ |
| `tencent[31]` | `fuyao.snapshot.price_change` | L1 | 95.99% | 25 | 499 | - |  | ✅ |
| `sina[13]` | `ulist239.f142` | L1 | 95.71% | 28 | 560 | - |  | ✅ |
| `ulist239.f142` | `sina[13]` | L1 | 95.71% | 28 | 560 | - |  | ✅ |
| `push2.f167` | `tencent[46]` | L1 | 95.00% | 6 | 120 | - |  | ✅ |
| `push2.f122` | `zhb.full.change_ytd` | L1 | 95.00% | 4 | 80 | - |  | ✅ |
| `push2.f122` | `zhb.stat.change_ytd` | L1 | 95.00% | 4 | 80 | - |  | ✅ |
| `push2_full.f122` | `zhb.full.change_ytd` | L1 | 94.97% | 20 | 398 | - |  | ✅ |
| `push2_full.f122` | `zhb.stat.change_ytd` | L1 | 94.97% | 20 | 398 | - |  | ✅ |
| `ulist239.f115` | `zhb.full.pe_dynamic` | L1 | 94.75% | 20 | 400 | - |  | ✅ |
| `ulist239.f115` | `zhb.stat.pe_dynamic` | L1 | 94.75% | 20 | 400 | - |  | ✅ |
| `push2_full.f164` | `zhb.full.pe_dynamic` | L1 | 94.72% | 20 | 398 | - |  | ✅ |
| `push2_full.f164` | `zhb.stat.pe_dynamic` | L1 | 94.72% | 20 | 398 | - |  | ✅ |
| `ulist239.f25` | `zhb.full.change_ytd` | L1 | 94.55% | 22 | 440 | - |  | ✅ |
| `ulist239.f25` | `zhb.stat.change_ytd` | L1 | 94.55% | 22 | 440 | - |  | ✅ |
| `tdx.quote_full.pb` | `tencent[46]` | L1 | 93.82% | 9 | 178 | - |  | ✅ |
| `tencent[19]` | `tdx.quote_full.ask1` | L1 | 93.63% | 30 | 597 | - |  | ✅ |
| `tencent[10]` | `ulist239.f211` | L1 | 93.54% | 28 | 557 | - |  | ✅ |
| `sina[23]` | `ulist239.f143` | L1 | 92.86% | 28 | 560 | - |  | ✅ |
| `ulist239.f143` | `sina[23]` | L1 | 92.86% | 28 | 560 | - |  | ✅ |
| `tencent[11]` | `ulist239.f142` | L1 | 92.64% | 28 | 557 | - |  | ✅ |
| `ulist239.f142` | `tencent[11]` | L1 | 92.64% | 28 | 557 | - |  | ✅ |
| `push2.f121` | `tencent[71]` | L1 | 91.67% | 6 | 120 | - |  | ✅ |
| `ulist239.f23` | `tencent[46]` | L1 | 91.20% | 28 | 557 | - |  | ✅ |
| `tdx.quote_full.vol_ratio` | `tencent[49]` | L1 | 91.01% | 9 | 178 | - |  | ✅ |
| `push2_full.f167` | `tencent[46]` | L1 | 90.57% | 24 | 477 | - |  | ✅ |
| `tdx.quote_full.float_mcap_yi` | `tencent[44]` | L1 | 90.45% | 9 | 178 | - |  | ✅ |
| `tdx.quote_full.mcap_yi` | `tencent[45]` | L1 | 90.45% | 9 | 178 | - |  | ✅ |
| `sina[8]` | `ulist239.f5` | L1-U | 100.00% | 28 | 558 | 0.01 |  | — |
| `push2_full.f118` | `ulist239.f107` | L1 | 100.00% | 24 | 478 | - |  | — |
| `ulist239.f107` | `push2_full.f118` | L1 | 100.00% | 24 | 478 | - |  | — |
| `sina[8]` | `push2_full.f47` | L1-U | 100.00% | 23 | 459 | 0.01 |  | — |
| `axdata.data.symbol` | `push2_full.f57` | L1 | 100.00% | 11 | 198 | - |  | — |
| `axdata.data.symbol` | `ulist239.f12` | L1 | 100.00% | 11 | 198 | - |  | — |
| `push2_full.f57` | `axdata.data.symbol` | L1 | 100.00% | 11 | 198 | - |  | — |
| `ulist239.f12` | `axdata.data.symbol` | L1 | 100.00% | 11 | 198 | - |  | — |
| `axdata.data.symbol` | `tencent[2]` | L1 | 100.00% | 10 | 180 | - |  | — |
| `tencent[2]` | `axdata.data.symbol` | L1 | 100.00% | 10 | 180 | - |  | — |
| `sina[8]` | `eltdx.quote_snapshot.total_hand` | L1-U | 100.00% | 9 | 162 | 0.01 |  | — |
| `axdata.data.open_amount` | `zhb.full.main_net_buy_amount` | L1-U | 100.00% | 8 | 144 | 0.0001 |  | — |
| `axdata.data.open_amount` | `zhb.stat2.main_net_buy_amount` | L1-U | 100.00% | 8 | 144 | 0.0001 |  | — |
| `push2_full.f52` | `tdx.quote_full.limit_down_price` | L1 | 100.00% | 7 | 138 | - |  | — |
| `tdx.quote_full.limit_down_price` | `push2_full.f52` | L1 | 100.00% | 7 | 138 | - |  | — |
| `push2.f47` | `fuyao.snapshot.volume` | L1-U | 100.00% | 6 | 120 | 100 |  | — |
| `push2.f47` | `sina[8]` | L1-U | 100.00% | 6 | 120 | 100 |  | — |
| `sina[8]` | `push2.f47` | L1-U | 100.00% | 6 | 120 | 0.01 |  | — |
| `tdx.quote_full.pe_static` | `tencent[53]` | L1 | 100.00% | 4 | 78 | - |  | — |
| `push2_full.f163` | `tdx.quote_full.pe_static` | L1 | 98.72% | 4 | 78 | - |  | — |
| `tdx.quote_full.pe_static` | `push2_full.f163` | L1 | 98.72% | 4 | 78 | - |  | — |
| `push2_full.f52` | `tdx.quote_full.limit_down` | L1 | 97.50% | 6 | 120 | - |  | — |
| `tdx.quote_full.limit_down` | `push2_full.f52` | L1 | 97.50% | 6 | 120 | - |  | — |
| `tdx.quote_full.limit_down` | `tencent[48]` | L1 | 97.50% | 6 | 120 | - |  | — |
| `tdx.quote_full.pe_static` | `ulist239.f114` | L1 | 97.50% | 4 | 80 | - |  | — |
| `ulist239.f114` | `tdx.quote_full.pe_static` | L1 | 97.50% | 4 | 80 | - |  | — |
| `tdx.quote_full.amplitude_pct` | `ulist239.f7` | L1 | 96.88% | 8 | 160 | - |  | — |
| `ulist239.f7` | `tdx.quote_full.amplitude_pct` | L1 | 96.88% | 8 | 160 | - |  | — |
| `push2_full.f171` | `tdx.quote_full.amplitude_pct` | L1 | 96.38% | 7 | 138 | - |  | — |
| `tdx.quote_full.amplitude_pct` | `push2_full.f171` | L1 | 96.38% | 7 | 138 | - |  | — |
| `push2_full.f174` | `tencent[67]` | L1 | 90.78% | 24 | 477 | - |  | — |

## 二、L1 / L1-U 定案候选 — 同号镜像（同编号，低优先级）(0)

_本轮无同号镜像候选。_


## 三、L4 存疑候选（1695）

| 左字段 | 右字段 | 命中率 | 天数 | 样本 |
|:--|:--|--:|--:|--:|
| `axdata.data.symbol` | `push2.f57` | 100.00% | 1 | 8 |
| `axdata.data.open_price` | `fuyao.snapshot.open_price` | 100.00% | 6 | 108 |
| `axdata.data.open_price` | `fuyao.auction_final.auction_price` | 100.00% | 6 | 108 |
| `axdata.data.open_price` | `fuyao.auction_final.open_price` | 100.00% | 6 | 108 |
| `axdata.data.open_price` | `push2.f46` | 100.00% | 1 | 8 |
| `axdata.data.open_price` | `sina[1]` | 100.00% | 11 | 198 |
| `axdata.data.open_price` | `tdx.quote_full.open` | 100.00% | 10 | 180 |
| `axdata.data.open_price` | `tencent[5]` | 100.00% | 10 | 180 |
| `axdata.data.pre_close` | `fuyao.snapshot.prev_price` | 100.00% | 6 | 108 |
| `axdata.data.pre_close` | `fuyao.auction_final.pre_close_price` | 100.00% | 6 | 108 |
| `axdata.data.pre_close` | `push2.f60` | 100.00% | 1 | 8 |
| `axdata.data.pre_close` | `push2_full.f60` | 100.00% | 11 | 198 |
| `axdata.data.pre_close` | `sina[2]` | 100.00% | 11 | 198 |
| `axdata.data.pre_close` | `tdx.quote_full.last_close` | 100.00% | 11 | 198 |
| `axdata.data.pre_close` | `tencent[4]` | 100.00% | 10 | 180 |
| `axdata.data.pre_close` | `ulist239.f18` | 100.00% | 11 | 198 |
| `axdata.data.float_shares` | `push2.f85` | 100.00% | 1 | 8 |
| `axdata.data.float_shares` | `tdx.finance_info.liutong_guben` | 100.00% | 11 | 198 |
| `axdata.data.float_shares` | `tdx.finance_info.liutongguben` | 100.00% | 11 | 198 |
| `fuyao.auction_final.pre_close_price` | `axdata.data.pre_close` | 100.00% | 6 | 108 |
| `fuyao.auction_final.pre_close_price` | `eltdx.quote_snapshot.pre_close_price` | 100.00% | 10 | 180 |
| `fuyao.auction_final.pre_close_price` | `eltdx.shortline.pre_close` | 100.00% | 6 | 108 |
| `fuyao.auction_final.pre_close_price` | `push2.f60` | 100.00% | 6 | 120 |
| `fuyao.auction_final.pre_close_price` | `push2_full.f60` | 100.00% | 19 | 380 |
| `fuyao.auction_final.pre_close_price` | `ulist239.f18` | 100.00% | 23 | 460 |
| `push2.f43` | `eltdx.quote_snapshot.last_price` | 100.00% | 5 | 90 |
| `push2.f43` | `fuyao.snapshot.last_price` | 100.00% | 6 | 120 |
| `push2.f43` | `fuyao.auction_final.last_price` | 100.00% | 6 | 120 |
| `push2.f43` | `sina[3]` | 100.00% | 6 | 120 |
| `push2.f43` | `tdx.quote_full.price` | 100.00% | 6 | 120 |
| `push2.f43` | `tencent[3]` | 100.00% | 6 | 120 |
| `push2.f43` | `ulist239.f2` | 100.00% | 6 | 120 |
| `push2.f43` | `ulist239.f144` | 100.00% | 6 | 120 |
| `push2.f44` | `eltdx.quote_snapshot.high_price` | 100.00% | 5 | 90 |
| `push2.f44` | `fuyao.snapshot.high_price` | 100.00% | 6 | 120 |
| `push2.f44` | `sina[4]` | 100.00% | 6 | 120 |
| `push2.f44` | `tdx.quote_full.high` | 100.00% | 6 | 120 |
| `push2.f44` | `tencent[33]` | 100.00% | 6 | 120 |
| `push2.f44` | `tencent[41]` | 100.00% | 6 | 120 |
| `push2.f44` | `ulist239.f15` | 100.00% | 6 | 120 |
| `push2.f45` | `eltdx.quote_snapshot.low_price` | 100.00% | 5 | 90 |
| `push2.f45` | `fuyao.snapshot.low_price` | 100.00% | 6 | 120 |
| `push2.f45` | `sina[5]` | 100.00% | 6 | 120 |
| `push2.f45` | `tdx.quote_full.low` | 100.00% | 6 | 120 |
| `push2.f45` | `tencent[34]` | 100.00% | 6 | 120 |
| `push2.f45` | `tencent[42]` | 100.00% | 6 | 120 |
| `push2.f45` | `ulist239.f16` | 100.00% | 6 | 120 |
| `push2.f46` | `axdata.data.open_price` | 100.00% | 1 | 8 |
| `push2.f46` | `eltdx.quote_snapshot.open_price` | 100.00% | 5 | 90 |
| `push2.f46` | `eltdx.shortline.open_price` | 100.00% | 3 | 46 |
| `push2.f46` | `fuyao.snapshot.open_price` | 100.00% | 6 | 120 |
| `push2.f46` | `fuyao.auction_final.open_price` | 100.00% | 6 | 120 |
| `push2.f46` | `sina[1]` | 100.00% | 6 | 120 |
| `push2.f46` | `tdx.quote_full.open` | 100.00% | 6 | 120 |
| `push2.f46` | `tencent[5]` | 100.00% | 6 | 120 |
| `push2.f46` | `ulist239.f17` | 100.00% | 6 | 120 |
| `push2.f50` | `tdx.quote_full.vol_ratio` | 100.00% | 4 | 58 |
| `push2.f52` | `tdx.quote_full.limit_down_price` | 100.00% | 4 | 58 |
| `push2.f57` | `axdata.data.symbol` | 100.00% | 1 | 8 |
| `push2.f60` | `axdata.data.pre_close` | 100.00% | 1 | 8 |

_（仅显示前 60 / 共 1695）_

## 四、已证伪护栏命中（被拦截的伪结论候选）（0）

_本轮无护栏命中（未产出与已证伪结论冲突的候选）。_


## 五、主动方法候选（不直接定案）（500）

_候选可能来自稳健相关、仿射公式、逐股时间序列或字段标签线索；每项保留样本日期和来源，仍需人工复核并以独立证据终判。_

| 左字段 | 右字段 | 方法 | 样本 | 日期 | 来源 | 证据摘要 |
|:--|:--|:--|--:|:--|:--|:--|
| `push2ex.price` | `em_hot.price` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 858 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | em_hot, push2ex | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `push2ex.change_pct` | `em_hot.pct` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 858 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | em_hot, push2ex | Pearson=0.9999, Spearman=0.9969, LOO稳号=True |
| `em_hot.price` | `push2ex.price` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 858 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | em_hot, push2ex | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `em_hot.pct` | `push2ex.change_pct` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 858 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | em_hot, push2ex | Pearson=0.9999, Spearman=0.9969, LOO稳号=True |
| `axdata.data.open_price` | `tdx.quote_full.price` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 198 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | axdata, tdx | Pearson=0.9999, Spearman=0.9684, LOO稳号=True |
| `axdata.data.open_price` | `tdx.quote_full.open` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 197 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | axdata, tdx | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `fuyao.auction_final.pre_close_price` | `eltdx.quote_snapshot.pre_close_price` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 180 | T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923 | eltdx, fuyao | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tdx.quote_full.pb` | `fuyao.valuation.pb_mrq` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 140 | T:20260824, T:20260831, T:20260907, T:20260914, T:20260918, T:20260921 | fuyao, tdx | Pearson=1.0, Spearman=0.9997, LOO稳号=True |
| `fuyao.valuation.pb_mrq` | `tdx.quote_full.pb` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 140 | T:20260824, T:20260831, T:20260907, T:20260914, T:20260918, T:20260921 | fuyao, tdx | Pearson=1.0, Spearman=0.9997, LOO稳号=True |
| `fuyao.auction_final.pre_close_price` | `eltdx.shortline.pre_close` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 108 | T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260930 | eltdx, fuyao | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `fuyao.auction_final.pre_close_price` | `axdata.data.pre_close` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 108 | T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260903 | axdata, fuyao | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `fuyao.auction_final.auction_volume_ratio` | `eltdx.shortline.auction_prev_volume_ratio` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 108 | T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260930 | eltdx, fuyao | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `fuyao.auction_final.auction_volume_ratio` | `axdata.data.auction_prev_volume_ratio` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 108 | T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260903 | axdata, fuyao | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `axdata.data.pre_close` | `fuyao.auction_final.pre_close_price` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 108 | T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260903 | axdata, fuyao | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `axdata.data.open_price` | `fuyao.snapshot.open_price` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 108 | T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260903 | axdata, fuyao | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `axdata.data.open_price` | `fuyao.auction_final.open_price` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 108 | T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260903 | axdata, fuyao | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `axdata.data.auction_prev_volume_ratio` | `fuyao.auction_final.auction_volume_ratio` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 108 | T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260903 | axdata, fuyao | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `em_hot.pct` | `zhb.stat.change_pct` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 40 | T:20260819, T:20260821, T:20260824, T:20260901, T:20260902, T:20260904 | em_hot, zhb | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `em_hot.pct` | `zhb.full.change_pct` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 40 | T:20260819, T:20260821, T:20260824, T:20260901, T:20260902, T:20260904 | em_hot, zhb | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `push2ex.change_pct` | `zhb.stat.change_pct` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 35 | T:20260901, T:20260902, T:20260904, T:20260908, T:20260911, T:20260914 | push2ex, zhb | Pearson=1.0, Spearman=0.9982, LOO稳号=True |
| `push2ex.change_pct` | `zhb.full.change_pct` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 35 | T:20260901, T:20260902, T:20260904, T:20260908, T:20260911, T:20260914 | push2ex, zhb | Pearson=1.0, Spearman=0.9982, LOO稳号=True |
| `em_hot.price` | `tdx.quote_full.price` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 30 | T:20260819, T:20260820, T:20260821, T:20260824, T:20260901, T:20260902 | em_hot, tdx | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `em_hot.pct` | `tdx.quote_full.change_pct` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 30 | T:20260819, T:20260820, T:20260821, T:20260824, T:20260901, T:20260902 | em_hot, tdx | Pearson=1.0, Spearman=0.9988, LOO稳号=True |
| `em_hot.price` | `fuyao.snapshot.last_price` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 27 | T:20260824, T:20260901, T:20260902, T:20260904, T:20260914, T:20260915 | em_hot, fuyao | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `em_hot.price` | `fuyao.auction_final.last_price` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 27 | T:20260824, T:20260901, T:20260902, T:20260904, T:20260914, T:20260915 | em_hot, fuyao | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `sina[9]` | `tdx.quote_full.amount_wan` | robust_correlation, affine_formula, per_stock_time_series | 620 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9993, Spearman=0.9942, LOO稳号=True |
| `sina[7]` | `tdx.quote_full.price` | robust_correlation, affine_formula, per_stock_time_series | 620 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9998, Spearman=0.9206, LOO稳号=True |
| `sina[7]` | `tdx.quote_full.last_close` | robust_correlation, affine_formula, per_stock_time_series | 620 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9998, Spearman=0.9296, LOO稳号=True |
| `sina[7]` | `tdx.quote_full.ask1` | robust_correlation, affine_formula, per_stock_time_series | 620 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9999, Spearman=0.9719, LOO稳号=True |
| `sina[6]` | `tdx.quote_full.price` | robust_correlation, affine_formula, per_stock_time_series | 620 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9999, Spearman=0.972, LOO稳号=True |
| `sina[6]` | `tdx.quote_full.last_close` | robust_correlation, affine_formula, per_stock_time_series | 620 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9999, Spearman=0.9679, LOO稳号=True |
| `sina[6]` | `tdx.quote_full.bid1` | robust_correlation, affine_formula, per_stock_time_series | 620 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9803, Spearman=0.9681, LOO稳号=True |
| `sina[5]` | `tdx.quote_full.price` | robust_correlation, affine_formula, per_stock_time_series | 620 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=1.0, Spearman=0.9882, LOO稳号=True |
| `sina[5]` | `tdx.quote_full.last_close` | robust_correlation, affine_formula, per_stock_time_series | 620 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=1.0, Spearman=0.9878, LOO稳号=True |
| `sina[4]` | `tdx.quote_full.price` | robust_correlation, affine_formula, per_stock_time_series | 620 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=1.0, Spearman=0.9888, LOO稳号=True |
| `sina[4]` | `tdx.quote_full.last_close` | robust_correlation, affine_formula, per_stock_time_series | 620 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9999, Spearman=0.9876, LOO稳号=True |
| `sina[4]` | `tdx.quote_full.bid1` | robust_correlation, affine_formula, per_stock_time_series | 620 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9804, Spearman=0.9493, LOO稳号=True |
| `sina[3]` | `tdx.quote_full.price` | robust_correlation, affine_formula, per_stock_time_series | 620 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `sina[3]` | `tdx.quote_full.last_close` | robust_correlation, affine_formula, per_stock_time_series | 620 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9999, Spearman=0.997, LOO稳号=True |
| `sina[3]` | `tdx.quote_full.bid1` | robust_correlation, affine_formula, per_stock_time_series | 620 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9802, Spearman=0.9401, LOO稳号=True |
| `sina[2]` | `tdx.quote_full.price` | robust_correlation, affine_formula, per_stock_time_series | 620 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9999, Spearman=0.997, LOO稳号=True |
| `sina[2]` | `tdx.quote_full.last_close` | robust_correlation, affine_formula, per_stock_time_series | 620 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `sina[29]` | `tdx.quote_full.ask1` | robust_correlation, affine_formula, per_stock_time_series | 620 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9803, Spearman=0.966, LOO稳号=True |
| `sina[27]` | `tdx.quote_full.ask1` | robust_correlation, affine_formula, per_stock_time_series | 620 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9803, Spearman=0.966, LOO稳号=True |
| `sina[25]` | `tdx.quote_full.ask1` | robust_correlation, affine_formula, per_stock_time_series | 620 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9803, Spearman=0.966, LOO稳号=True |
| `sina[23]` | `tdx.quote_full.ask1` | robust_correlation, affine_formula, per_stock_time_series | 620 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9803, Spearman=0.9661, LOO稳号=True |
| `sina[21]` | `tdx.quote_full.ask1` | robust_correlation, affine_formula, per_stock_time_series | 620 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=1.0, Spearman=0.9934, LOO稳号=True |
| `sina[1]` | `tdx.quote_full.price` | robust_correlation, affine_formula, per_stock_time_series | 620 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9999, Spearman=0.9872, LOO稳号=True |
| `sina[1]` | `tdx.quote_full.last_close` | robust_correlation, affine_formula, per_stock_time_series | 620 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=1.0, Spearman=0.9886, LOO稳号=True |
| `sina[19]` | `tdx.quote_full.bid1` | robust_correlation, affine_formula, per_stock_time_series | 620 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9999, Spearman=0.9733, LOO稳号=True |
| `sina[17]` | `tdx.quote_full.bid1` | robust_correlation, affine_formula, per_stock_time_series | 620 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9999, Spearman=0.9733, LOO稳号=True |
| `sina[15]` | `tdx.quote_full.bid1` | robust_correlation, affine_formula, per_stock_time_series | 620 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9999, Spearman=0.9733, LOO稳号=True |
| `sina[13]` | `tdx.quote_full.bid1` | robust_correlation, affine_formula, per_stock_time_series | 620 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9999, Spearman=0.9733, LOO稳号=True |
| `sina[11]` | `tdx.quote_full.price` | robust_correlation, affine_formula, per_stock_time_series | 620 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9803, Spearman=0.947, LOO稳号=True |
| `sina[11]` | `tdx.quote_full.bid1` | robust_correlation, affine_formula, per_stock_time_series | 620 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=1.0, Spearman=0.993, LOO稳号=True |
| `sina[7]` | `tdx.quote_full.open` | robust_correlation, affine_formula, per_stock_time_series | 619 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9998, Spearman=0.934, LOO稳号=True |
| `sina[7]` | `tdx.quote_full.low` | robust_correlation, affine_formula, per_stock_time_series | 619 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9998, Spearman=0.9339, LOO稳号=True |
| `sina[7]` | `tdx.quote_full.high` | robust_correlation, affine_formula, per_stock_time_series | 619 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9998, Spearman=0.932, LOO稳号=True |
| `sina[6]` | `tdx.quote_full.open` | robust_correlation, affine_formula, per_stock_time_series | 619 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9999, Spearman=0.9794, LOO稳号=True |
| `sina[6]` | `tdx.quote_full.low` | robust_correlation, affine_formula, per_stock_time_series | 619 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9999, Spearman=0.9806, LOO稳号=True |
| `sina[6]` | `tdx.quote_full.high` | robust_correlation, affine_formula, per_stock_time_series | 619 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9999, Spearman=0.9813, LOO稳号=True |
| `sina[5]` | `tdx.quote_full.open` | robust_correlation, affine_formula, per_stock_time_series | 619 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=1.0, Spearman=0.999, LOO稳号=True |
| `sina[5]` | `tdx.quote_full.low` | robust_correlation, affine_formula, per_stock_time_series | 619 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `sina[5]` | `tdx.quote_full.high` | robust_correlation, affine_formula, per_stock_time_series | 619 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=1.0, Spearman=0.9985, LOO稳号=True |
| `sina[4]` | `tdx.quote_full.open` | robust_correlation, affine_formula, per_stock_time_series | 619 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=1.0, Spearman=0.9986, LOO稳号=True |
| `sina[4]` | `tdx.quote_full.low` | robust_correlation, affine_formula, per_stock_time_series | 619 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=1.0, Spearman=0.9985, LOO稳号=True |
| `sina[4]` | `tdx.quote_full.high` | robust_correlation, affine_formula, per_stock_time_series | 619 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `sina[3]` | `tdx.quote_full.open` | robust_correlation, affine_formula, per_stock_time_series | 619 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9999, Spearman=0.9924, LOO稳号=True |
| `sina[3]` | `tdx.quote_full.low` | robust_correlation, affine_formula, per_stock_time_series | 619 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=1.0, Spearman=0.9934, LOO稳号=True |
| `sina[3]` | `tdx.quote_full.high` | robust_correlation, affine_formula, per_stock_time_series | 619 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=1.0, Spearman=0.9939, LOO稳号=True |
| `sina[2]` | `tdx.quote_full.open` | robust_correlation, affine_formula, per_stock_time_series | 619 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=1.0, Spearman=0.9938, LOO稳号=True |
| `sina[2]` | `tdx.quote_full.low` | robust_correlation, affine_formula, per_stock_time_series | 619 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=1.0, Spearman=0.993, LOO稳号=True |
| `sina[2]` | `tdx.quote_full.high` | robust_correlation, affine_formula, per_stock_time_series | 619 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=1.0, Spearman=0.9928, LOO稳号=True |
| `sina[1]` | `tdx.quote_full.open` | robust_correlation, affine_formula, per_stock_time_series | 619 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `sina[1]` | `tdx.quote_full.low` | robust_correlation, affine_formula, per_stock_time_series | 619 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=1.0, Spearman=0.999, LOO稳号=True |
| `sina[1]` | `tdx.quote_full.high` | robust_correlation, affine_formula, per_stock_time_series | 619 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=1.0, Spearman=0.9986, LOO稳号=True |
| `sina[11]` | `tdx.quote_full.low` | robust_correlation, affine_formula, per_stock_time_series | 619 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9805, Spearman=0.9554, LOO稳号=True |
| `sina[11]` | `tdx.quote_full.high` | robust_correlation, affine_formula, per_stock_time_series | 619 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9804, Spearman=0.9561, LOO稳号=True |
| `tencent[5]` | `tdx.quote_full.price` | robust_correlation, affine_formula, per_stock_time_series | 617 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, tencent | Pearson=0.9999, Spearman=0.9872, LOO稳号=True |
| `tencent[5]` | `tdx.quote_full.last_close` | robust_correlation, affine_formula, per_stock_time_series | 617 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, tencent | Pearson=1.0, Spearman=0.9885, LOO稳号=True |
| `tencent[5]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 617 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9998, Spearman=0.9337, LOO稳号=True |
| `tencent[5]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 617 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9999, Spearman=0.9793, LOO稳号=True |
| `tencent[5]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 617 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=1.0, Spearman=0.999, LOO稳号=True |
| `tencent[5]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 617 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=1.0, Spearman=0.9986, LOO稳号=True |
| `tencent[5]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 617 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9999, Spearman=0.9872, LOO稳号=True |
| `tencent[5]` | `sina[2]` | robust_correlation, affine_formula, per_stock_time_series | 617 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=1.0, Spearman=0.9885, LOO稳号=True |
| `tencent[5]` | `sina[1]` | robust_correlation, affine_formula, per_stock_time_series | 617 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[4]` | `tdx.quote_full.price` | robust_correlation, affine_formula, per_stock_time_series | 617 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, tencent | Pearson=0.9999, Spearman=0.997, LOO稳号=True |
| `tencent[4]` | `tdx.quote_full.last_close` | robust_correlation, affine_formula, per_stock_time_series | 617 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[4]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 617 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9998, Spearman=0.9291, LOO稳号=True |
| `tencent[4]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 617 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9999, Spearman=0.9677, LOO稳号=True |
| `tencent[4]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 617 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=1.0, Spearman=0.9877, LOO稳号=True |
| `tencent[4]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 617 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9999, Spearman=0.9875, LOO稳号=True |
| `tencent[4]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 617 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9999, Spearman=0.997, LOO稳号=True |
| `tencent[4]` | `sina[2]` | robust_correlation, affine_formula, per_stock_time_series | 617 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[4]` | `sina[1]` | robust_correlation, affine_formula, per_stock_time_series | 617 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=1.0, Spearman=0.9885, LOO稳号=True |
| `tencent[3]` | `tdx.quote_full.price` | robust_correlation, affine_formula, per_stock_time_series | 617 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[3]` | `tdx.quote_full.last_close` | robust_correlation, affine_formula, per_stock_time_series | 617 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, tencent | Pearson=0.9999, Spearman=0.997, LOO稳号=True |
| `tencent[3]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 617 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9998, Spearman=0.92, LOO稳号=True |
| `tencent[3]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 617 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9999, Spearman=0.9718, LOO稳号=True |

_仅显示前 100 / 共 500 条。_


## 六、日期与数据质量告警（232）

- 20260920: 旧式非交易日目录按前一交易日 20260918 归并；目录未改名
- 20260814: 行情数据日 20260814 属于配置的异常日，行情快照排除
- 20260812/thsdk: 没有可用记录，快照跳过
- 20260813/push2: 没有可用记录，快照跳过
- 20260813/thsdk: 没有可用记录，快照跳过
- 20260819/thsdk: 没有可用记录，快照跳过
- 20260820/thsdk: 没有可用记录，快照跳过
- 20260821/push2: 没有可用记录，快照跳过
- 20260821/thsdk: 没有可用记录，快照跳过
- 20260824/thsdk: 没有可用记录，快照跳过
- 20260825/push2: 没有可用记录，快照跳过
- 20260825/thsdk: 没有可用记录，快照跳过
- 20260826/push2: 没有可用记录，快照跳过
- 20260826/thsdk: 没有可用记录，快照跳过
- 20260827/thsdk: 没有可用记录，快照跳过
- 20260828/cninfo: 没有可用记录，快照跳过
- 20260828/push2: 没有可用记录，快照跳过
- 20260828/thsdk: 没有可用记录，快照跳过
- 20260901/axdata: 采集时段未知，保留为候选样本但不计入 L1
- 20260901/datacenter: 采集时段未知，保留为候选样本但不计入 L1
- 20260901/em_fund_flow: 采集时段未知，保留为候选样本但不计入 L1
- 20260901/em_hot: 采集时段未知，保留为候选样本但不计入 L1
- 20260901/em_kline_f61: 没有可用记录，快照跳过
- 20260901/fuyao: 采集时段未知，保留为候选样本但不计入 L1
- 20260901/market_sources: 采集时段未知，保留为候选样本但不计入 L1
- 20260901/push2: 采集时段未知，保留为候选样本但不计入 L1
- 20260901/push2_full: 采集时段未知，保留为候选样本但不计入 L1
- 20260901/push2ex: 采集时段未知，保留为候选样本但不计入 L1
- 20260901/sina: 采集时段未知，保留为候选样本但不计入 L1
- 20260901/tdx: 采集时段未知，保留为候选样本但不计入 L1
- 20260901/tdx_f10: 采集时段未知，保留为候选样本但不计入 L1
- 20260901/tdx_f10_more: 采集时段未知，保留为候选样本但不计入 L1
- 20260901/tencent: 采集时段未知，保留为候选样本但不计入 L1
- 20260901/thsdk: 采集时段未知，保留为候选样本但不计入 L1
- 20260901/ulist239: 采集时段未知，保留为候选样本但不计入 L1
- 20260902/push2: 没有可用记录，快照跳过
- 20260903/em_kline_f61: 没有可用记录，快照跳过
- 20260903/push2: 没有可用记录，快照跳过
- 20260903/thsdk: 没有可用记录，快照跳过
- 20260904/em_kline_f61: 没有可用记录，快照跳过
- 20260904/push2: 没有可用记录，快照跳过
- 20260907/em_kline_f61: 没有可用记录，快照跳过
- 20260907/push2: 没有可用记录，快照跳过
- 20260908/push2: 没有可用记录，快照跳过
- 20260909/em_kline_f61: 没有可用记录，快照跳过
- 20260909/push2: 没有可用记录，快照跳过
- 20260910/push2: 没有可用记录，快照跳过
- 20260910/tdx_f10_more: 没有可用记录，快照跳过
- 20260911/em_kline_f61: 采集状态 failed
- 20260911/em_kline_f61: 来源状态为 failed，快照跳过
- 20260911/push2: 没有可用记录，快照跳过
- 20260911/tdx_f10_more: 没有可用记录，快照跳过
- 20260914/em_kline_f61: 采集状态 partial
- 20260914/em_kline_f61: 来源状态为 partial，样本按部分快照参与
- 20260914/em_kline_f61: 没有可用记录，快照跳过
- 20260914/tdx_f10_more: 没有可用记录，快照跳过
- 20260915/eltdx: 采集状态 partial
- 20260915/em_kline_f61: 采集状态 partial
- 20260915/eltdx: 来源状态为 partial，样本按部分快照参与
- 20260915/em_kline_f61: 来源状态为 partial，样本按部分快照参与
- 20260915/tdx_f10: 没有可用记录，快照跳过
- 20260915/tdx_f10_more: 没有可用记录，快照跳过
- 20260916/eltdx: 采集状态 partial
- 20260916/em_kline_f61: 采集状态 partial
- 20260916/eltdx: 来源状态为 partial，样本按部分快照参与
- 20260916/em_kline_f61: 来源状态为 partial，样本按部分快照参与
- 20260916/tdx_f10_more: 没有可用记录，快照跳过
- 20260917/eltdx: 采集状态 partial
- 20260917/em_kline_f61: 采集状态 partial
- 20260917/eltdx: 来源状态为 partial，样本按部分快照参与
- 20260917/em_kline_f61: 来源状态为 partial，样本按部分快照参与
- 20260917/tdx_f10: 没有可用记录，快照跳过
- 20260917/tdx_f10_more: 没有可用记录，快照跳过
- 20260918/eltdx: 采集状态 partial
- 20260918/em_kline_f61: 采集状态 failed
- 20260918/eltdx: 来源状态为 partial，样本按部分快照参与
- 20260918/em_kline_f61: 来源状态为 failed，快照跳过
- 20260918/tdx_f10: 没有可用记录，快照跳过
- 20260918/tdx_f10_more: 没有可用记录，快照跳过
- 20260920/eltdx: 采集状态 partial
- 20260920/em_kline_f61: 采集状态 partial
- 20260920/eltdx: 来源状态为 partial，样本按部分快照参与
- 20260920/em_kline_f61: 来源状态为 partial，样本按部分快照参与
- 20260920/tdx_f10: 没有可用记录，快照跳过
- 20260920/tdx_f10_more: 没有可用记录，快照跳过
- 20260921/eltdx: 采集状态 partial
- 20260921/push2: 采集状态 failed
- 20260921/push2_full: 采集状态 failed
- 20260921/em_kline_f61: 采集状态 failed
- 20260921/em_fund_flow: 采集状态 failed
- 20260921/ulist239: 采集状态 failed
- 20260921/clist: 采集状态 partial
- 20260921/clist: 来源状态为 partial，样本按部分快照参与
- 20260921/clist: 没有可用记录，快照跳过
- 20260921/eltdx: 来源状态为 partial，样本按部分快照参与
- 20260921/em_fund_flow: 来源状态为 failed，快照跳过
- 20260921/em_hot: 没有可用记录，快照跳过
- 20260921/em_kline_f61: 来源状态为 failed，快照跳过
- 20260921/push2: 来源状态为 failed，快照跳过
- 20260921/push2_full: 来源状态为 failed，快照跳过
- 另有 132 条告警，详见同名 JSON 报告。

---

> 数据来源：通达信 / 项目字段对撞体系。以上为方法论梳理，不构成投资建议。
