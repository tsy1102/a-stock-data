# E3 证据摘要复核（2026-11-15）

## 发现

合并前的 registry parity 回放发现两份既有 E3 决策引用的证据摘要不匹配当前证据文档。经 `scripts/evidence_hash.py` 与 `text_file_sha256_candidates()` 核对，旧摘要既不匹配当前文件字节，也不匹配规范 LF 或 CRLF 表示，因此不是 Git 换行转换造成的差异。当前 Markdown 与其 Git 提交内容一致；本次未恢复旧文本，也没有证据表明字段裁决文字被后续修改。

## 证据复核

- ELTDX 行情证据：逐行将 360 条 CSV 对回保留期 `raw_eltdx.json`、`raw_tencent.json` 与来源日期元数据。腾讯时间戳日期、报价价与腾讯字段 `[3]`、报价价与同日 TDX K 线收盘价、成交额与同日 TDX K 线成交额均为 360/360 一致。359 组正成交额用于跨源量级核对，另 1 组双方为零；最大绝对差 487 元，最大相对差约 `1.6215963e-7`。本次仅复算现有归档与证据表，没有扩张到其他行情字段。
- Fuyao 固定资产同比证据：逐行重算 20 家公司的官方报告金额变化公式，计算值与证据 CSV 一致；Fuyao 值 20/20 同方向，15/20 与复算值相差不超过 `0.0000005` 个百分点，5 个残差保留，最大绝对残差约 `0.2538839372` 个百分点。本次没有重新下载 40 份发行人 PDF；报告 URL 与 PDF 摘要仍以原证据 CSV 为准。

## 摘要修正

| 文件 | 原摘要 | 修正后摘要（规范 LF） |
|---|---|---|
| [`20261114_eltdx_adapter_quote_semantics_evidence.md`](20261114_eltdx_adapter_quote_semantics_evidence.md) | `aa56e934cdbb8a2211a4f7fd98d29b24a130c321a0f1e82d2339f4539961675e` | `28be9cb637e12b56250d624b2e1d174e97c0df021389e59e2ad90c82a1633980` |
| [`20261114_fuyao_fixed_asset_growth_evidence.md`](20261114_fuyao_fixed_asset_growth_evidence.md) | `d1ba77a9a58a879a17f7d3a8dcd4f909819b405eed048fd855c4f3be95f9b59e` | `df1e99baf02effb90fd945c6cc766116e06a39ee436d30089069259705570124` |

ELTDX 样本表中原记录的摘要也不匹配当前 CSV；已将 [`20261114_eltdx_adapter_quote_samples.csv`](../research/20261114_eltdx_adapter_quote_samples.csv) 的摘要修正为规范 LF SHA-256 `4de7e3a4b3204a2384a1afe990a163e59ac20660a27bd23cfd1bd51d27cf7b6c`。

决策含义、字段状态、单位、映射关系和样本裁决均未更改；只同步修正决策 JSON 与 registry 中对应 E3 证据引用的摘要。逐项复算脚本只用于本次本地审计，没有作为项目运行依赖。
