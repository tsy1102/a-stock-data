import json

import pytest

from scripts import public_web_adjudications as adjudications

REPORTS = "reports"
DATA_DATE = "20261109"
SOURCE_FILE = f"{DATA_DATE}/raw_reports.json"
PAGE_URLS = {
    "600519": "https://data.eastmoney.com/report/600519.html",
    "601288": "https://data.eastmoney.com/report/601288.html",
    "600309": "https://data.eastmoney.com/report/600309.html",
}
DETAIL_URLS = {
    "600519": "https://data.eastmoney.com/report/info/AP202611081831533384.html",
    "601288": "https://data.eastmoney.com/report/info/AP202611011831293587.html",
    "600309": "https://data.eastmoney.com/report/info/AP202610281831068169.html",
}
REPORTS_BY_STOCK = {
    "600519": {
        "title": "贵州茅台26Q3点评：市场化改革持续兑现",
        "publishDate": "2026-11-08 00:00:00.000",
        "infoCode": "AP202611081831533384",
        "author": ["11000276538.邓欣", "11000474034.郑少轩"],
        "researcher": "邓欣,郑少轩",
        "authorID": ["11000276538", "11000474034"],
        "emRatingName": "买入",
        "lastEmRatingName": "买入",
        "emRatingCode": "007",
        "ratingChange": 3,
        "orgSName": "华安证券",
        "sRatingCode": "0101",
        "sRatingName": "买入",
    },
    "601288": {
        "title": "2026年三季报点评：营收利润增速回升",
        "publishDate": "2026-11-01 00:00:00.000",
        "infoCode": "AP202611011831293587",
        "author": ["11000257641.陈俊良", "11000209220.王剑"],
        "researcher": "陈俊良,王剑",
        "authorID": ["11000257641", "11000209220"],
        "emRatingName": "增持",
        "lastEmRatingName": "增持",
        "emRatingCode": "006",
        "ratingChange": 3,
        "orgSName": "国信证券",
        "sRatingCode": "0301",
        "sRatingName": "优于大市",
    },
    "600309": {
        "title": "公司信息更新报告：Q3归母净利润超预期，新建磷酸铁锂产能加速打开成长空间",
        "publishDate": "2026-10-28 00:00:00.000",
        "infoCode": "AP202610281831068169",
        "author": [
            "11000267432.金益腾",
            "11000338335.张晓锋",
            "11000444537.李思佳",
        ],
        "researcher": "金益腾,张晓锋,李思佳",
        "authorID": ["11000267432", "11000338335", "11000444537"],
        "emRatingName": "买入",
        "lastEmRatingName": "买入",
        "emRatingCode": "007",
        "ratingChange": 3,
        "orgSName": "开源证券",
        "sRatingCode": "0201",
        "sRatingName": "买入(Buy)",
    },
}


def _write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


def _fixture(tmp_path):
    verification = tmp_path / "docs" / "field_verification"
    _write_json(
        verification / "source_lineage.json",
        {
            "sources": {
                REPORTS: {
                    "provider": "Eastmoney",
                    "independence_status": "confirmed",
                    "runtime_aliases": ["reports"],
                }
            }
        },
    )
    stocks = {
        stock_code: [{"stockCode": stock_code, **record}]
        for stock_code, record in REPORTS_BY_STOCK.items()
    }
    stocks["000001"] = [
        {
            "stockCode": "000001",
            "orgSName": "其他机构",
            "sRatingCode": "0101",
            "sRatingName": "强烈推荐",
        },
        {
            "stockCode": "000001",
            "orgSName": "其他机构",
            "sRatingCode": "0301",
            "sRatingName": "买入",
        },
        {
            "stockCode": "000001",
            "orgSName": "其他机构",
            "sRatingCode": "0201",
            "sRatingName": "推荐",
        },
    ]
    _write_json(verification / SOURCE_FILE, {"stocks": stocks, "scheme": "reports"})

    conflicts = {
        "author": {
            "canonical": ["author", "researcher / author"],
            "meaning": ["作者数组", "研究员姓名"],
        },
        "researcher": {"canonical": ["researcher", "researcher / author"]},
        "lastEmRatingName": {"meaning": ["上次东财统一评级名称", "待破解"]},
        "emRatingCode": {
            "canonical": ["emRatingCode", "emRatingCode / emRatingValue"],
            "meaning": ["统一", "评级代码/值"],
        },
        "sRatingCode": {},
    }
    previous_meaning = {"author": "", "researcher": "研究员姓名", "emRatingCode": ""}
    previous_meaning["lastEmRatingName"] = ""
    previous_meaning["sRatingCode"] = "待破解"
    previous_canonical = {
        "author": "",
        "researcher": "",
        "lastEmRatingName": "lastEmRatingName",
        "emRatingCode": "",
        "sRatingCode": "sRatingCode",
    }
    registry_rows = [
        {
            "source": REPORTS,
            "code": code,
            "identity": f"reports::{code}",
            "canonical": previous_canonical[code],
            "meaning": previous_meaning[code],
            "unit": "",
            "status": "unverified" if code == "sRatingCode" else "conflict",
            "status_resolution": (
                "registry_status_only_single_source"
                if code == "sRatingCode"
                else "reference_status_conflict"
            ),
            "status_evidence": {},
            "reference_evidence": [],
            "attribute_conflicts": conflicts[code],
            "adjudications": [],
        }
        for code in (
            "author",
            "researcher",
            "lastEmRatingName",
            "emRatingCode",
            "sRatingCode",
        )
    ]
    registry = {"source_fields": registry_rows, "fields": [], "mappings": []}

    observations = {
        "author": [],
        "researcher": [],
        "lastEmRatingName": [],
        "emRatingCode": [],
        "sRatingCode": [],
    }
    for stock_code, record in REPORTS_BY_STOCK.items():
        page_authors = [
            {"author_id": item.split(".", 1)[0], "name": item.split(".", 1)[1]}
            for item in record["author"]
        ]
        for code in observations:
            if code == "lastEmRatingName":
                observations[code].append(
                    {
                        "observation_type": adjudications.REPORT_RATING_OBSERVATION_TYPE,
                        "stock_code": stock_code,
                        "data_date": DATA_DATE,
                        "source_file": SOURCE_FILE,
                        "record_identity": {
                            "infoCode": record["infoCode"],
                            "title": record["title"],
                            "publishDate": record["publishDate"],
                        },
                        "raw_value": record[code],
                        "page_current_rating": record["emRatingName"],
                        "page_rating_change": "维持",
                        "page_url": PAGE_URLS[stock_code],
                        "page_metric": "研报明细 > 东财评级 / 评级变动",
                        "display_text": f"{record['emRatingName']} / 维持",
                    }
                )
                continue
            if code == "emRatingCode":
                observations[code].append(
                    {
                        "observation_type": adjudications.REPORT_EASTMONEY_RATING_CODE_OBSERVATION_TYPE,
                        "stock_code": stock_code,
                        "data_date": DATA_DATE,
                        "source_file": SOURCE_FILE,
                        "record_identity": {
                            "infoCode": record["infoCode"],
                            "title": record["title"],
                            "publishDate": record["publishDate"],
                        },
                        "raw_value": record[code],
                        "page_current_rating": record["emRatingName"],
                        "page_url": PAGE_URLS[stock_code],
                        "page_metric": "研报明细 > 东财评级",
                        "display_text": record["emRatingName"],
                    }
                )
                continue
            if code == "sRatingCode":
                page_source_ratings = {
                    "600519": ("买入", "exact", "维持“买入”评级"),
                    "601288": ("优于大市", "exact", "维持‘优于大市’评级"),
                    "600309": ("买入", "approximate", "维持‘买入’评级"),
                }
                page_source_rating, match_type, display_text = page_source_ratings[stock_code]
                observations[code].append(
                    {
                        "observation_type": adjudications.REPORT_SOURCE_RATING_CODE_OBSERVATION_TYPE,
                        "stock_code": stock_code,
                        "data_date": DATA_DATE,
                        "source_file": SOURCE_FILE,
                        "record_identity": {
                            "infoCode": record["infoCode"],
                            "title": record["title"],
                            "publishDate": record["publishDate"],
                        },
                        "raw_value": record[code],
                        "raw_organization": record["orgSName"],
                        "page_source_rating": page_source_rating,
                        "match_type": match_type,
                        "page_url": DETAIL_URLS[stock_code],
                        "page_metric": "研报正文 > 投资建议/评级原文",
                        "display_text": display_text,
                    }
                )
                continue
            observations[code].append(
                {
                    "observation_type": adjudications.REPORT_RECORD_OBSERVATION_TYPE,
                    "stock_code": stock_code,
                    "data_date": DATA_DATE,
                    "source_file": SOURCE_FILE,
                    "record_identity": {
                        "infoCode": record["infoCode"],
                        "title": record["title"],
                        "publishDate": record["publishDate"],
                    },
                    "raw_value": record[code],
                    "page_authors": page_authors,
                    "page_url": PAGE_URLS[stock_code],
                    "page_metric": "研报明细 > 作者",
                    "display_text": " ".join(item["name"] for item in page_authors),
                }
            )

    meanings = {
        "author": "研报作者列表；每项由作者ID和姓名组成，格式为“ID.姓名”",
        "researcher": "研究员姓名",
        "lastEmRatingName": "上次东财统一评级名称",
        "emRatingCode": "东财统一评级类别代码；与 emRatingName 对应，本次样本不是完整代码表",
        "sRatingCode": "机构原始评级类别代码；须结合 orgSName 和 sRatingName 解释，未确立跨机构代码表",
    }
    canonicals = {
        "author": "report_author_id_name_list",
        "researcher": "report_researcher_name_list",
        "lastEmRatingName": "lastEmRatingName",
        "emRatingCode": "emRatingCode",
        "sRatingCode": "sRatingCode",
    }
    decisions = []
    evidence_lines = [
        "# Official Eastmoney report record observations",
        "",
        "网页核验日期：2026-11-10（Asia/Shanghai）",
    ]
    for code in (
        "author",
        "researcher",
        "lastEmRatingName",
        "emRatingCode",
        "sRatingCode",
    ):
        previous = next(row for row in registry_rows if row["code"] == code)
        decision = {
            "id": f"20261110-reports-{code}",
            "action": "verify_public_web_observation",
            "verification_mode": (
                adjudications.REPORT_SOURCE_RATING_CODE_MODE
                if code == "sRatingCode"
                else adjudications.REPORT_RECORD_CONFLICT_MODE
            ),
            "target": {"source": REPORTS, "code": code},
            "previous_status": previous["status"],
            "previous_status_resolution": previous["status_resolution"],
            "previous": {key: previous[key] for key in ("canonical", "meaning", "unit")},
            "previous_attribute_conflicts": previous["attribute_conflicts"],
            "canonical": canonicals[code],
            "meaning": meanings[code],
            "unit": "",
            "rationale": (
                "三只不同股票的官网研报详情按 URL 中的 infoCode、标题和发布日期与 "
                "2026-11-09 raw_reports 精确绑定；两条原始评级文字精确匹配，一条“买入”对“买入(Buy)”"
                "作为近似匹配单独记录。完整采集内同一机构+代码只对应一个原始评级名称，但同一代码跨机构对应多个名称；"
                "仅确认机构原始评级代码这一字段角色，不建立跨机构代码表或跨源映射。"
                if code == "sRatingCode"
                else (
                    "三只不同股票的官网研报记录按 infoCode、标题和发布日期与 "
                    "2026-11-09 raw_reports 精确绑定；核验本目标字段的页面对应值和同记录关系，"
                    "不建立跨源映射。"
                )
            ),
            "external_evidence": (
                list(DETAIL_URLS.values()) if code == "sRatingCode" else list(PAGE_URLS.values())
            ),
            "page_observations": observations[code],
        }
        decisions.append(decision)
        evidence_lines.extend(["", f"## reports::{code}"])
        evidence_lines.extend(
            adjudications._observation_evidence_line(REPORTS, code, item)
            for item in observations[code]
        )

    evidence_path = verification / "adjudications" / "public_web" / "20261110_reports_authors.md"
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text("\n".join(evidence_lines) + "\n", encoding="utf-8")
    decision_path = "adjudications/public_web/20261110_reports_authors.json"
    document = {
        "schema_version": 1,
        "evidence_basis": "public_web_observation",
        "reviewer": "test reviewer",
        "reviewed_on": "2026-11-10",
        "evidence_file": "adjudications/public_web/20261110_reports_authors.md",
        "decisions": decisions,
    }
    _write_json(verification / decision_path, document)
    return registry, document, decision_path


def test_report_author_observations_resolve_exact_record_conflicts_and_pass_parity(tmp_path):
    registry, document, decision_path = _fixture(tmp_path)

    updated, stats = adjudications.apply_public_web_observation_adjudications(
        registry, document, decision_path, tmp_path
    )

    records = {row["code"]: row for row in updated["source_fields"]}
    assert records["author"]["canonical"] == "report_author_id_name_list"
    assert records["author"]["meaning"].startswith("研报作者列表")
    assert records["researcher"]["canonical"] == "report_researcher_name_list"
    assert records["researcher"]["meaning"] == "研究员姓名"
    assert records["lastEmRatingName"]["canonical"] == "lastEmRatingName"
    assert records["lastEmRatingName"]["meaning"] == "上次东财统一评级名称"
    assert records["emRatingCode"]["canonical"] == "emRatingCode"
    assert records["emRatingCode"]["meaning"].startswith("东财统一评级类别代码")
    assert records["sRatingCode"]["canonical"] == "sRatingCode"
    assert records["sRatingCode"]["meaning"].startswith("机构原始评级类别代码")
    assert all(
        records[code]["unit"] == ""
        for code in (
            "author",
            "researcher",
            "lastEmRatingName",
            "emRatingCode",
            "sRatingCode",
        )
    )
    assert all(
        records[code]["status"] == "verified"
        for code in (
            "author",
            "researcher",
            "lastEmRatingName",
            "emRatingCode",
            "sRatingCode",
        )
    )
    assert all(
        records[code]["attribute_conflicts"] == {}
        for code in (
            "author",
            "researcher",
            "lastEmRatingName",
            "emRatingCode",
            "sRatingCode",
        )
    )
    assert stats["status_conflicts_resolved"] == 4
    assert stats["metadata_resolved"] == 5
    assert stats["mappings_added"] == 0
    s_rating_observations = records["sRatingCode"]["adjudications"][-1]["page_observations"]
    assert [item["match_type"] for item in s_rating_observations] == [
        "exact",
        "exact",
        "approximate",
    ]
    assert adjudications.validate_registry_adjudications(updated, tmp_path) == []


def test_report_author_observation_rejects_record_identity_and_author_id_mismatches(tmp_path):
    registry, document, decision_path = _fixture(tmp_path)
    document["decisions"][0]["page_observations"][0]["record_identity"][
        "title"
    ] = "different report"
    with pytest.raises(ValueError, match="record_identity.title differs"):
        adjudications.apply_public_web_observation_adjudications(
            registry, document, decision_path, tmp_path
        )

    other_root = tmp_path / "author-id-mismatch"
    registry, document, decision_path = _fixture(other_root)
    document["decisions"][0]["page_observations"][0]["page_authors"][0]["author_id"] = "99999999999"
    with pytest.raises(ValueError, match="author-link IDs differ"):
        adjudications.apply_public_web_observation_adjudications(
            registry, document, decision_path, other_root
        )


def test_report_author_observation_requires_three_stocks_and_supported_paths(tmp_path):
    registry, document, decision_path = _fixture(tmp_path)
    document["decisions"][0]["page_observations"] = document["decisions"][0]["page_observations"][
        :2
    ]
    with pytest.raises(ValueError, match="at least three stock records"):
        adjudications.apply_public_web_observation_adjudications(
            registry, document, decision_path, tmp_path
        )

    other_root = tmp_path / "unsupported-path"
    registry, document, decision_path = _fixture(other_root)
    title_row = {
        **registry["source_fields"][0],
        "code": "title",
        "identity": "reports::title",
        "adjudications": [],
    }
    registry["source_fields"].append(title_row)
    document["decisions"][0]["target"]["code"] = "title"
    with pytest.raises(
        ValueError,
        match="do not support this reports field",
    ):
        adjudications.apply_public_web_observation_adjudications(
            registry, document, decision_path, other_root
        )


def test_previous_rating_name_requires_official_unchanged_rating_evidence(tmp_path):
    registry, document, decision_path = _fixture(tmp_path)
    rating_decision = document["decisions"][2]
    rating_decision["page_observations"][0]["page_rating_change"] = "上调"
    with pytest.raises(ValueError, match="requires the current rating and 维持 page label"):
        adjudications.apply_public_web_observation_adjudications(
            registry, document, decision_path, tmp_path
        )

    other_root = tmp_path / "changed-rating-code"
    registry, document, decision_path = _fixture(other_root)
    raw_path = other_root / "docs" / "field_verification" / SOURCE_FILE
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    raw["stocks"]["600519"][0]["ratingChange"] = 1
    _write_json(raw_path, raw)
    with pytest.raises(ValueError, match="only be verified for unchanged ratings"):
        adjudications.apply_public_web_observation_adjudications(
            registry, document, decision_path, other_root
        )


def test_eastmoney_rating_code_requires_unique_same_capture_rating_name(tmp_path):
    registry, document, decision_path = _fixture(tmp_path)
    raw_path = tmp_path / "docs" / "field_verification" / SOURCE_FILE
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    raw["stocks"]["000001"] = [
        {"stockCode": "000001", "emRatingCode": "007", "emRatingName": "增持"}
    ]
    _write_json(raw_path, raw)

    with pytest.raises(ValueError, match="does not have one consistent emRatingName"):
        adjudications.apply_public_web_observation_adjudications(
            registry, document, decision_path, tmp_path
        )


def test_source_rating_code_keeps_approximate_match_separate_and_checks_scope(tmp_path):
    registry, document, decision_path = _fixture(tmp_path)
    rating_decision = next(
        row for row in document["decisions"] if row["target"]["code"] == "sRatingCode"
    )
    rating_decision["page_observations"][2]["match_type"] = "exact"
    with pytest.raises(ValueError, match="match_type must distinguish exact"):
        adjudications.apply_public_web_observation_adjudications(
            registry, document, decision_path, tmp_path
        )

    other_root = tmp_path / "organization-code-conflict"
    registry, document, decision_path = _fixture(other_root)
    raw_path = other_root / "docs" / "field_verification" / SOURCE_FILE
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    raw["stocks"]["000002"] = [
        {
            "stockCode": "000002",
            "orgSName": "华安证券",
            "sRatingCode": "0101",
            "sRatingName": "增持",
        }
    ]
    _write_json(raw_path, raw)
    with pytest.raises(ValueError, match="one sRatingName within its organization"):
        adjudications.apply_public_web_observation_adjudications(
            registry, document, decision_path, other_root
        )
