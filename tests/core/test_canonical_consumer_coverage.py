from __future__ import annotations

import unittest

from scripts.canonical_consumer_coverage import find_canonical_consumer_reads


class TestCanonicalConsumerCoverage(unittest.TestCase):
    def test_follows_aliases_helpers_dynamic_getattr_and_serialized_keys(self):
        sources = {
            "helpers.py": '''
def read_dynamic_field(value, name):
    return getattr(value, name)

def _v(value, name):
    return getattr(value, name)
''',
            "report.py": '''
from core.data_provider import get_canonical_stock_data as load
from helpers import _v
from helpers import read_dynamic_field as fetch

def read_selected_fields(value):
    for name in ("pe_ttm", "pb"):
        fetch(value, name)
    return _v(value, "change_pct")

def build_report(code):
    quote = load(code)
    alias = quote
    read_selected_fields(alias)
    payload = alias.to_dict()
    payload.get("price")
    payload["amount_wan"]
    unrelated = {"quote_date": "2026-10-21"}
    unrelated.get("quote_date")
''',
        }
        reads = find_canonical_consumer_reads(
            sources,
            {"pe_ttm", "pb", "change_pct", "price", "amount_wan", "quote_date"},
        )

        self.assertEqual(set(reads), {"pe_ttm", "pb", "change_pct", "price", "amount_wan"})
        self.assertNotIn("quote_date", reads)

    def test_does_not_count_unrelated_same_named_attributes(self):
        source = '''
def build_report(stock):
    return stock.price

def unrelated(value):
    return value.price
'''
        reads = find_canonical_consumer_reads({"report.py": source}, {"price"})

        self.assertEqual(reads, {})


if __name__ == "__main__":
    unittest.main()
