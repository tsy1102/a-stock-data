# ZHB `tipinfo.dat` market code adjudication (2026-11-08)

## Decision

`ZHB-tipinfo::[0]` is the TDX market code. For the retained A-share universe, the observed values mean `0=SZ`, `1=SH`, and `2=BJ`. This decision verifies the source field only; it creates no cross-source mapping.

## Local source and sample checks

The audit read only date-named archives on or after the project retention boundary, `2026-10-15`, from `cache/zhb/zhb_YYYYMMDD.zip`. It inspected 15 archives dated 2026-10-15 through 2026-11-06. Every `tipinfo.dat` record had 22 pipe-delimited columns.

- Across the 15 retained archives, 84,815 records had a nonempty value in column `[0]`. The only observed values were `0` (44,133 records), `1` (35,389), and `2` (5,293).
- In the latest archive, `zhb_20261106.zip`, all 5,656 records had column `[0]`: `0` occurred 2,942 times, `1` 2,359 times, and `2` 355 times.
- Representative listed codes matched the expected exchanges: Shenzhen examples `000007` and `002034` had `0`; Shanghai examples `600519` and `688553` had `1`; Beijing example `920118` had `2`.
- As an internal consistency check, `tipinfo.dat` column `[0]` matched `tdxstat.cfg` column `[0]` for all 5,579 overlapping securities in the latest archive; there were no mismatches. This is same-package corroboration, not an independent source.
- For the 20 stocks in the retained 2026-11-06 `raw_zhb.json` sample, parser output matched raw `tipinfo.dat` values for every mapped field checked; the audit found zero mismatches. The parser currently discards column `[0]`, so the field is adjudicated from the preserved source archive rather than a runtime output key.

## Upstream reference

The official TDX Quant market-type enumeration defines `.SZ=0` (Shenzhen), `.SH=1` (Shanghai), and `.BJ=2` (Beijing) in its [market type table](https://help.tdx.com.cn/quant/docs/markdown/Dict.html). Official exchange materials independently identify the relevant code families: the [SZSE securities code range table](https://www.szse.cn/marketServices/technicalservice/doc/P020240510623040090566.pdf), the [SSE market factbook](https://www.sse.com.cn/aboutus/publication/factbook/documents/c/10170562/files/da4f403a0b7443fa9b2ba2e002d38f10.pdf), and the [BSE code compilation guideline](https://www.bse.cn/jygl_list/200021626.html).

The match between the exact column values and TDX's published market enum across all retained records supports the field definition and value mapping. The dated raw archives are retained in the local cache; the counts above preserve the reviewed evidence summary without copying the raw data into the repository.

## Limits

This adjudication covers only `ZHB-tipinfo::[0]` in the retained stock records. It does not infer values for other product classes or create a market-code equivalence mapping to unrelated sources. Columns `[17]` and `[18]` were empty in all 84,815 retained records, but their intended roles remain unknown; they stay unresolved.
