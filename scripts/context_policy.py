"""Shared policy for optional market-context capture and collision records."""

CONTEXT_ONLY_SOURCES = frozenset({"exchange", "em_hot"})
CONTEXT_RECORD_PATHS = {
    "market_sources": (("dragon_tiger_today",),),
    "fuyao": (("market", "dragon_tiger"), ("market", "hot_list_hour")),
}
CONTEXT_REQUIRED_PATHS = {
    "market_sources": [("dragon_tiger_today",)],
    "exchange": [("records",)],
}
CONTEXT_EXCLUDED_PATHS = {
    source: [".".join(path) for path in paths] for source, paths in CONTEXT_RECORD_PATHS.items()
}
CONTEXT_EXCLUDED_PATHS.update(
    {
        "exchange": ["records", "sse_raw"],
        "em_hot": ["hot_rank"],
    }
)
