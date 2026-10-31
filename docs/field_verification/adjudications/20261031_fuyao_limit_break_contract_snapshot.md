# Fuyao limit-break pool contract snapshot

- Retrieved: 2026-10-31
- Authority: 同花顺 Fuyao official Financial-API documentation
- Live source: https://fuyao.aicubes.cn/llms-full.txt
- Endpoint: `GET /api/a-share/special-data/limit-break-pool`
- Locator: “炸板股票池” response example and `data.item[]` response-field table

The current official contract defines `first_seal_time` as the first time the
stock sealed at its upper limit and `last_seal_time` as its last such time.
Both are Shanghai-time strings in `HH:mm` format and may be `null` when absent.
The response fields belong to `data.item[]` of the limit-break-pool endpoint.

## Project path binding

`stock_common/sc_fuyao.py` defines `EP_LIMIT_BREAK_POOL` as
`/api/a-share/special-data/limit-break-pool`. The public
`get_fuyao_limit_pool(kind="break")` selects that endpoint and returns its
`data` object without renaming item keys. The field-probe collector stores this
response under `market.limit_break_pool.item[]`; the 2026-10-29 and 2026-10-30
raw captures both contain the two fields.

This snapshot confirms only the Fuyao source-path meanings. It does not declare
equivalence with another provider or create a cross-source mapping.
