from pathlib import Path

from stock_common.md_render import render_md_report


def test_report_markdown_writer_persists_headings_and_tables(tmp_path: Path) -> None:
    output_path = tmp_path / "report.md"
    lines = [
        "【摘要】",
        "➤ 关键指标",
        "代码  名称  价格",
        "------  ------  ------",
        "600519  示例公司  10.5",
    ]

    rendered = render_md_report(str(output_path), lines)

    assert rendered.startswith("## 摘要")
    assert "**关键指标**" in rendered
    assert "| 代码 | 名称 | 价格 |" in rendered
    assert "| 600519 | 示例公司 | 10.5 |" in rendered
    assert output_path.read_text(encoding="utf-8") == rendered
