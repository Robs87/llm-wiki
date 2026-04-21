#!/usr/bin/env python3
"""llm-wiki lint 工具集 — Hermes agent 使用参考

覆盖 lint 10 项检查中的 6 项核心可自动化项：
  ① 孤儿页面（已有 skill 内嵌示例，此处也收录）
  ② 断链检测
  ③ Index 完整性
  ④ Frontmatter 验证
  ⑤ 标签审计
  ⑥ 页大小检查
  ⑦ Log 轮转检查

使用方法：将 WIKI_PATH 替换为实际路径后，agent 可用 execute_code 调用各函数。
或用 execute_code 直接内联函数体。
"""

import os, re
from collections import defaultdict
from pathlib import Path

# ── 配置 ──────────────────────────────────────────────
WIKI_PATH = os.environ.get("WIKI_PATH", os.path.expanduser("~/Desktop/wiki"))
WIKI_DIRS = ["entities", "concepts", "comparisons", "queries"]  # Layer 2 目录
REQUIRED_FM_FIELDS = ["title", "created", "updated", "type", "tags", "sources"]
VALID_TYPES = ["entity", "concept", "comparison", "query", "summary"]


def get_all_md_files(base_dir, subdirs=None):
    """获取 wiki Layer 2 目录下所有 .md 文件路径（相对于 base_dir）"""
    if subdirs is None:
        subdirs = WIKI_DIRS
    files = []
    for subdir in subdirs:
        dir_path = os.path.join(base_dir, subdir)
        if not os.path.isdir(dir_path):
            continue
        for f in os.listdir(dir_path):
            if f.endswith(".md"):
                files.append(os.path.join(subdir, f))
    return files


# ── ① 孤儿页面 ────────────────────────────────────────
def find_orphans(base_dir=WIKI_PATH):
    """返回零入链的 wiki 页面列表"""
    all_files = get_all_md_files(base_dir)
    # 构建 wikilink → 出链源文件 的映射
    inbound = defaultdict(set)
    for fpath in all_files:
        full_path = os.path.join(base_dir, fpath)
        try:
            content = open(full_path, "r", encoding="utf-8").read()
        except Exception:
            continue
        # 匹配 [[link]] 格式
        links = re.findall(r"\[\[([^\]|]+)", content)
        for link in links:
            link = link.strip()
            inbound[link].add(fpath)

    orphans = []
    for fpath in all_files:
        # 页面名 = 不含目录前缀和 .md 后缀的文件名
        page_name = os.path.splitext(os.path.basename(fpath))[0]
        # 也检查带目录的完整路径（如 entities/openai）
        full_name = os.path.splitext(fpath)[0]
        if not inbound.get(page_name) and not inbound.get(full_name):
            orphans.append(fpath)
    return orphans


# ── ② 断链检测 ────────────────────────────────────────
def find_broken_links(base_dir=WIKI_PATH):
    """返回指向不存在页面的 [[wikilink]]"""
    all_files = get_all_md_files(base_dir)
    # 构建存在页面的名称集合（去 .md）
    existing = set()
    for fpath in all_files:
        name_no_ext = os.path.splitext(fpath)[0]  # 如 entities/openai
        basename = os.path.basename(name_no_ext)   # 如 openai
        existing.add(name_no_ext)
        existing.add(basename)

    broken = []
    for fpath in all_files:
        full_path = os.path.join(base_dir, fpath)
        try:
            content = open(full_path, "r", encoding="utf-8").read()
        except Exception:
            continue
        links = re.findall(r"\[\[([^\]|]+)", content)
        for link in links:
            link = link.strip()
            # 匹配：完全名 / 短名 / 短名.md
            if link not in existing and f"{link}.md" not in str(existing):
                # 额外检查：是否是 raw/ 下的文件（raw 文件不算断链）
                if os.path.exists(os.path.join(base_dir, "raw", f"{link}.md")):
                    continue
                broken.append({"source": fpath, "link": link})

    # 去重
    seen = set()
    unique = []
    for b in broken:
        key = (b["source"], b["link"])
        if key not in seen:
            seen.add(key)
            unique.append(b)
    return unique


# ── ③ Index 完整性 ────────────────────────────────────
def check_index_completeness(base_dir=WIKI_PATH):
    """对比文件系统 vs index.md，返回遗漏和多余条目"""
    index_path = os.path.join(base_dir, "index.md")
    all_files = get_all_md_files(base_dir)
    file_set = set(all_files)

    indexed = set()
    missing_from_index = []
    extra_in_index = []

    if not os.path.exists(index_path):
        return {"error": "index.md 不存在", "missing": list(file_set), "extra": []}

    try:
        content = open(index_path, "r", encoding="utf-8").read()
    except Exception:
        return {"error": "无法读取 index.md", "missing": list(file_set), "extra": []}

    for fpath in file_set:
        # 检查文件名（不含 .md）是否出现在 index 中
        name = os.path.splitext(os.path.basename(fpath))[0]
        if name not in content:
            missing_from_index.append(fpath)

    # 提取 index 中所有 [[wikilink]]，检查是否指向存在的文件
    index_links = re.findall(r"\[\[([^\]|]+)", content)
    for link in index_links:
        link = link.strip()
        # 检查 link 是否对应某个存在的 .md 文件
        found = False
        for fpath in file_set:
            name = os.path.splitext(os.path.basename(fpath))[0]
            if name == link or os.path.splitext(fpath)[0].endswith(link):
                found = True
                break
        if not found:
            extra_in_index.append(link)

    return {
        "missing_from_index": missing_from_index,
        "extra_in_index": extra_in_index,
    }


# ── ④ Frontmatter 验证 ────────────────────────────────
def validate_frontmatter(base_dir=WIKI_PATH):
    """检查每个 wiki 页面的 frontmatter 是否完整且合法"""
    all_files = get_all_md_files(base_dir)
    issues = []

    for fpath in all_files:
        full_path = os.path.join(base_dir, fpath)
        try:
            content = open(full_path, "r", encoding="utf-8").read()
        except Exception:
            issues.append({"file": fpath, "error": "无法读取文件"})
            continue

        # 提取 YAML frontmatter
        if not content.startswith("---"):
            issues.append({"file": fpath, "error": "缺少 YAML frontmatter（不以 --- 开头）"})
            continue

        end = content.find("---", 3)
        if end == -1:
            issues.append({"file": fpath, "error": "frontmatter 未闭合（缺少第二个 ---）"})
            continue

        fm_text = content[3:end].strip()
        fm = {}
        for line in fm_text.split("\n"):
            if ":" in line:
                key, _, val = line.partition(":")
                fm[key.strip()] = val.strip().strip("\"'")

        # 检查必填字段
        for field in REQUIRED_FM_FIELDS:
            if field not in fm:
                issues.append({"file": fpath, "error": f"缺少必填字段: {field}"})

        # 检查 type 值
        if "type" in fm and fm["type"] not in VALID_TYPES:
            issues.append({"file": fpath, "error": f"无效 type: {fm['type']}，应为 {VALID_TYPES}"})

    return issues


# ── ⑤ 标签审计 ────────────────────────────────────────
def audit_tags(base_dir=WIKI_PATH):
    """收集所有 wiki 页面使用的标签，并与 SCHEMA.md taxonomy 对比"""
    schema_path = os.path.join(base_dir, "SCHEMA.md")
    all_files = get_all_md_files(base_dir)

    # 从 SCHEMA.md 提取 taxonomy
    taxonomy_tags = set()
    if os.path.exists(schema_path):
        try:
            content = open(schema_path, "r", encoding="utf-8").read()
            # 匹配 `- tag-name` 格式
            taxonomy_tags = set(re.findall(r"^\s*-\s+([\w-]+)\s*$", content, re.MULTILINE))
        except Exception:
            pass

    # 收集所有页面使用的标签
    used_tags = defaultdict(list)  # tag -> [files]
    for fpath in all_files:
        full_path = os.path.join(base_dir, fpath)
        try:
            content = open(full_path, "r", encoding="utf-8").read()
        except Exception:
            continue
        # 从 frontmatter 提取 tags
        fm_match = re.search(r"^tags:\s*\[(.+?)\]", content, re.MULTILINE | re.DOTALL)
        if fm_match:
            tags_str = fm_match.group(1)
            tags = re.findall(r"([\w-]+)", tags_str)
            for tag in tags:
                used_tags[tag].append(fpath)

    # 找出不在 taxonomy 中的标签
    unlisted = {tag: files for tag, files in used_tags.items() if tag not in taxonomy_tags}

    return {
        "taxonomy_tags": sorted(taxonomy_tags),
        "used_tags": {k: sorted(v) for k, v in sorted(used_tags.items())},
        "unlisted_tags": {k: sorted(v) for k, v in sorted(unlisted.items())},
    }


# ── ⑥ 页大小检查 ──────────────────────────────────────
def check_page_size(base_dir=WIKI_PATH, threshold=200):
    """返回超过阈值行数的页面"""
    all_files = get_all_md_files(base_dir)
    oversized = []

    for fpath in all_files:
        full_path = os.path.join(base_dir, fpath)
        try:
            lines = open(full_path, "r", encoding="utf-8").readlines()
        except Exception:
            continue
        line_count = len(lines)
        if line_count > threshold:
            oversized.append({"file": fpath, "lines": line_count, "threshold": threshold})

    return sorted(oversized, key=lambda x: -x["lines"])


# ── ⑦ Log 轮转检查 ────────────────────────────────────
def check_log_rotation(base_dir=WIKI_PATH, entry_threshold=500):
    """检查 log.md 是否需要轮转"""
    log_path = os.path.join(base_dir, "log.md")
    if not os.path.exists(log_path):
        return {"needs_rotation": False, "entries": 0, "reason": "log.md 不存在"}

    try:
        content = open(log_path, "r", encoding="utf-8").read()
    except Exception:
        return {"needs_rotation": False, "entries": 0, "reason": "无法读取 log.md"}

    entries = re.findall(r"^##\s+\[", content, re.MULTILINE)
    count = len(entries)

    return {
        "needs_rotation": count > entry_threshold,
        "entries": count,
        "threshold": entry_threshold,
    }


# ── 一键运行所有检查 ──────────────────────────────────
def run_all_lint(base_dir=WIKI_PATH):
    """运行全部自动化 lint 检查，返回结构化报告"""
    results = {}

    print("=== ① 孤儿页面 ===")
    orphans = find_orphans(base_dir)
    results["orphans"] = orphans
    print(f"  发现 {len(orphans)} 个孤儿页面")
    for o in orphans:
        print(f"    - {o}")

    print("\n=== ② 断链检测 ===")
    broken = find_broken_links(base_dir)
    results["broken_links"] = broken
    print(f"  发现 {len(broken)} 个断链")
    for b in broken:
        print(f"    - {b['source']} → [[{b['link']}]]")

    print("\n=== ③ Index 完整性 ===")
    idx = check_index_completeness(base_dir)
    results["index_completeness"] = idx
    if "error" in idx:
        print(f"  ⚠ {idx['error']}")
    else:
        print(f"  缺少 {len(idx['missing_from_index'])} 个页面未录入 index")
        print(f"  index 中有 {len(idx['extra_in_index'])} 个条目指向不存在的页面")

    print("\n=== ④ Frontmatter 验证 ===")
    fm_issues = validate_frontmatter(base_dir)
    results["frontmatter"] = fm_issues
    print(f"  发现 {len(fm_issues)} 个 frontmatter 问题")
    for issue in fm_issues:
        print(f"    - {issue['file']}: {issue['error']}")

    print("\n=== ⑤ 标签审计 ===")
    tag_audit = audit_tags(base_dir)
    results["tags"] = tag_audit
    unlisted = tag_audit.get("unlisted_tags", {})
    print(f"  Taxonomy 标签数: {len(tag_audit.get('taxonomy_tags', []))}")
    print(f"  实际使用标签数: {len(tag_audit.get('used_tags', {}))}")
    print(f"  不在 taxonomy 中的标签: {len(unlisted)}")
    for tag, files in unlisted.items():
        print(f"    - [{tag}] 使用于: {', '.join(files)}")

    print("\n=== ⑥ 页大小检查（>{200} 行）===")
    oversized = check_page_size(base_dir)
    results["page_size"] = oversized
    print(f"  发现 {len(oversized)} 个超大页面")
    for o in oversized:
        print(f"    - {o['file']}: {o['lines']} 行")

    print("\n=== ⑦ Log 轮转检查 ===")
    log_check = check_log_rotation(base_dir)
    results["log_rotation"] = log_check
    print(f"  log.md 当前 {log_check['entries']} 条（阈值 {log_check['threshold']}）")
    if log_check["needs_rotation"]:
        print("  ⚠ 需要轮转！")
    else:
        print("  ✅ 无需轮转")

    return results


if __name__ == "__main__":
    import sys
    wiki_dir = sys.argv[1] if len(sys.argv) > 1 else WIKI_PATH
    run_all_lint(wiki_dir)
