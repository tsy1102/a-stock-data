#!/usr/bin/env python3
"""sync_readme.py — 从 CHANGELOG.md 同步 README.md 顶部"版本历史"块

设计目标：
  - 保留 CHANGELOG.md 的完整详细描述（每版本多行）
  - 自动同步到 README.md 顶部"版本历史"区
  - 单一权威源（CHANGELOG.md）→ README 自动同步

使用方式：
  1. 手动运行：python scripts/sync_readme.py
  2. CI 集成：git commit 前自动运行

行为：
  - 解析 CHANGELOG.md 每个版本条目的全部内容
  - 去掉 ### 章节标题
  - 重写 README.md 顶部的"版本历史"块
  - 其他 README 内容保持不变
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from datetime import datetime


CHANGELOG = Path("CHANGELOG.md")
README = Path("README.md")

# 摘要块标记（README 中的占位符）
SUMMARY_BEGIN = "## 📋 版本历史"

# emoji 列表（按顺序，每个版本轮换）
EMOJIS = ["🐛", "✨", "📊", "🔧", "🏗️", "📦", "🛠️", "🧹", "💾", "🔬", "🔌", "🎯", "🔀", "🧱", "🌱", "🌰", "🚀", "💡", "📚", "🧪"]


def select_emoji(version: str, body: str) -> str:
    """根据版本内容启发式选择 emoji"""
    # 按优先级匹配关键词
    if "Bug 修复" in body or "Bug修复" in body or "Fixed" in body or "is_workday" in body:
        return "🐛"
    if "Added" in body or "新增" in body:
        return "✨"
    if "性能" in body or "压测" in body or "perf" in body.lower():
        return "📊"
    if "重构" in body or "修复" in body:
        return "🔧"
    if "架构" in body or "设计" in body:
        return "🏗️"
    if "zhb" in body.lower() and "全局" in body:
        return "📦"
    if "scratch" in body.lower() or "清理" in body:
        return "🧹"
    if "缓存" in body or "cache" in body.lower():
        return "💾"
    if "mootdx" in body or "tdx" in body.lower():
        return "🔌"
    if "Data Provider" in body or "data_provider" in body:
        return "🎯"
    if "FieldSpec" in body or "sc_schema" in body:
        return "🏗️"
    if version == "8.0":
        return "🌱"
    return "✨"


def clean_body(body: str) -> str:
    """清理 body：去掉 ### 章节标题，保留子内容

    例如：
        ### Added — 阶段二：六大报告脚本新增ZHB分析维度

        **sht报告（短线）**：
        - 新增主力资金流向展示...

    变成：

        **sht报告（短线）**：
        - 新增主力资金流向展示...
    """
    lines = body.strip().split("\n")
    cleaned_lines = []
    for line in lines:
        # 跳过 ### 章节标题（如 "### Added — 阶段二..."）
        if re.match(r"^###\s+", line):
            continue
        cleaned_lines.append(line)

    # 移除开头和结尾的空行
    while cleaned_lines and not cleaned_lines[0].strip():
        cleaned_lines.pop(0)
    while cleaned_lines and not cleaned_lines[-1].strip():
        cleaned_lines.pop()

    return "\n".join(cleaned_lines)


def extract_version_block(version: str, date: str, body: str) -> str:
    """构造单个版本的 README 块（保留详细描述）

    Args:
        version: 版本号
        date: 日期
        body: CHANGELOG 中该版本的完整内容

    Returns:
        markdown 字符串
    """
    emoji = select_emoji(version, body)
    cleaned = clean_body(body)

    # 构造 > 引用块（每行前加 >）
    quoted = "\n".join(f"> {line}" if line.strip() else ">" for line in cleaned.split("\n"))

    return f"> {emoji} **V{version}**（{date}）\n{quoted}"


def extract_changelog_summaries():
    """从 CHANGELOG.md 提取所有版本摘要

    Returns:
        list of (version, date, body) tuples
    """
    content = CHANGELOG.read_text(encoding="utf-8")

    # 匹配版本条目（包括所有内容直到下一个 ## [ 或文件结束）
    pattern = r"^## \[([\d.]+)\] - (\d{4}-\d{2}-\d{2})\n+(.+?)(?=^## \[|\Z)"
    matches = re.finditer(pattern, content, re.M | re.S)

    versions = []
    for m in matches:
        version, date, body = m.group(1), m.group(2), m.group(3)
        versions.append((version, date, body.strip()))

    return versions


def build_summary_block(versions) -> str:
    """构造 README 版本历史块（保留完整内容）

    Args:
        versions: extract_changelog_summaries() 返回的列表

    Returns:
        markdown string
    """
    lines = [SUMMARY_BEGIN, ""]
    lines.append("完整版本历史详见 [CHANGELOG.md](CHANGELOG.md)。")
    lines.append("")

    for version, date, body in versions:
        block = extract_version_block(version, date, body)
        lines.append(block)
        lines.append("")

    return "\n".join(lines)


def update_readme(versions) -> bool:
    """重写 README 版本历史块"""
    content = README.read_text(encoding="utf-8")

    # 找到当前版本历史块开始位置
    begin_idx = content.find(SUMMARY_BEGIN)
    if begin_idx == -1:
        print(f"ERROR: README.md 中找不到 '{SUMMARY_BEGIN}' 标记")
        return False

    # 找到版本历史块结束（下一个 "---" 分隔符）
    end_marker = "\n---"
    end_idx = content.find(end_marker, begin_idx)
    if end_idx == -1:
        print("ERROR: README.md 版本历史块后找不到 '---' 分隔符")
        return False

    # 构造新版本历史块
    new_block = build_summary_block(versions)

    # 替换
    new_content = content[:begin_idx] + new_block + "\n" + content[end_idx:].lstrip("\n")

    # 写回
    README.write_text(new_content, encoding="utf-8")
    return True


def main():
    print(f"[sync_readme] 开始从 {CHANGELOG} 同步到 {README}")
    print(f"[sync_readme] 当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if not CHANGELOG.exists():
        print(f"ERROR: {CHANGELOG} 不存在")
        sys.exit(1)

    if not README.exists():
        print(f"ERROR: {README} 不存在")
        sys.exit(1)

    versions = extract_changelog_summaries()
    print(f"[sync_readme] 提取 {len(versions)} 个版本")

    if update_readme(versions):
        print(f"[sync_readme] ✅ README.md 版本历史块已更新")
    else:
        print(f"[sync_readme] ❌ 更新失败")
        sys.exit(1)


if __name__ == "__main__":
    main()