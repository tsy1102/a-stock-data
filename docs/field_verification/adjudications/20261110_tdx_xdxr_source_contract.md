# TDX 0x000f XDXR category 1 source contract

Reviewed: 2026-11-10

## Decision

The pinned ELTDX v3.3.2 `CapitalChangeRecord` reference identifies the four category 1 values in order: cash dividend per 10 shares, allotment price, transfer shares per 10 shares, and allotment shares per 10 shares. The project adapter maps those values to `fenhong`, `peigu_price`, `songzhuangu`, and `peigu` respectively. The four TDX source paths are now source-contract verified; no cross-source mappings were added.

| TDX source path | Verified meaning | Source unit | Project adapter output |
|---|---|---:|---|
| `fenhong` | Cash dividend amount per 10 shares | CNY/10 shares | `bonus_rmb`: CNY/share |
| `peigujia` | Allotment price | CNY/share | `peigu_price`: CNY/share |
| `songzhuangu` | Transfer/bonus share count per 10 shares | shares/10 shares | `transfer_ratio`: shares/share |
| `peigu` | Rights-allotment share count per 10 shares | shares/10 shares | `bonus_ratio`: shares/share |

For the last three paths, this round confirms meaning and unit from the pinned source contract. It did not find a nonzero live event sample to cross-check those values individually.

## Evidence

ELTDX v3.3.2 documents `CapitalChangeRecord` as the decoded result of TDX `0x000f`; for category 1 it lists the four values in the order above and states that the quantity values are in shares. The project maps `c1_value` through `c4_value` to the four named columns in `core/eltdx_adapter.py`.

Two public issuer/exchange notices cross-check `fenhong` against the live project adapter:

| Code | Ex-date | Adapter `fenhong` | Issuer/exchange value | Result |
|---|---|---:|---:|---|
| `600519` | 2026-06-26 | 280.2423095703125 | CNY 28.02423/share | Adapter value rounds to CNY 280.2423/10 shares |
| `000858` | 2026-07-16 | 25.796852111816406 | CNY 25.796852/10 shares | Matches to the published precision |

The small residuals are float32 representation noise. The raw observed values and exact comparison notes are retained in [`20261110_tdx_xdxr_unit_audit.csv`](20261110_tdx_xdxr_unit_audit.csv).

Sources:

- [ELTDX v3.3.2 `CapitalChangeRecord` field reference](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/FIELD_REFERENCE.md), §CapitalChangeRecord.
- [Kweichow Moutai official 2025 annual distribution implementation notice](https://www.moutai.com.cn/mtgf/articleFileDir/2026-06/22/f7c1dbdf7142475d84269482757fd72d.pdf), states CNY 28.02423 per share and ex-date 2026-06-26.
- [Shenzhen Stock Exchange 2025 Wuliangye distribution implementation notice](https://disc.static.szse.cn/download/disc/disk03/finalpage/2026-07-10/469435ce-3d6d-4b42-8691-75b03f142f90.PDF), states CNY 25.796852 per 10 shares and ex-date 2026-07-16.

## Runtime correction

The ELTDX adapter previously copied its per-10-share values directly into the mootdx-compatible columns. The `easy_tdx` fallback already normalizes those three fields to per-share values. Consequently the primary ELTDX path returned `bonus_rmb` ten times larger than the report contract: SHT displayed it as “每股” and LNG/VAL divided it by a per-share stock price to calculate yields. The adapter now divides `fenhong`, `songzhuangu`, and `peigu` by 10 while leaving `peigu_price` unchanged. The returned dictionary shape is unchanged, and its cache category was bumped from `dividend_tdx_v2` to `dividend_tdx_v3` so pre-fix values cannot be reused.

## Scope limits

- ELTDX is the project's pinned protocol implementation and documents the decoded field contract; this record does not claim the library is an official TDX specification.
- Issuer/exchange samples independently verify the dividend amount and its unit. The three other field values are contract-verified only because this sample set contained no nonzero allotment or transfer event.
- No cross-source equivalence is inferred. The registry records source identity and source semantics only.
