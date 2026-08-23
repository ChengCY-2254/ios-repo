#!/usr/bin/env python3
"""为 Cydia / Sileo 软件源生成 Release 文件。

用法:
    python3 scripts/gen-release.py --root .

Release 包含仓库基本信息（可通过命令行参数或同名环境变量覆盖，例如
REPO_ORIGIN、REPO_LABEL、REPO_SUITE、REPO_VERSION、REPO_CODENAME、
REPO_ARCHITECTURES、REPO_COMPONENTS、REPO_DESCRIPTION），
并列出仓库根目录下实际存在的 Packages* 文件（Packages、Packages.gz、
Packages.bz2、Packages.xz 等）的 MD5 / SHA1 / SHA256 / SHA512 校验和，
供 Cydia / Sileo 校验元数据完整性。仅依赖 Python 3 标准库。
"""

import argparse
import hashlib
import os
import sys
from datetime import datetime, timezone
from email.utils import formatdate

CHUNK_SIZE = 1 << 20

# 会被写进 Release 校验和段的候选文件（只列实际存在的）
CANDIDATES = [
    "Packages",
    "Packages.gz",
    "Packages.bz2",
    "Packages.xz",
    "Packages.lzma",
    "Packages.zst",
]

# Release 中对每个文件列出的校验和段
CHECKSUMS = [
    ("MD5Sum", "md5"),
    ("SHA1", "sha1"),
    ("SHA256", "sha256"),
    ("SHA512", "sha512"),
]


def digest_file(path: str, algo: str) -> str:
    h = hashlib.new(algo)
    with open(path, "rb") as fh:
        while True:
            chunk = fh.read(CHUNK_SIZE)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description="生成 Cydia / Sileo 源 Release 文件")
    parser.add_argument("--root", default=".", help="仓库根目录（默认当前目录）")
    parser.add_argument("--origin", default=os.environ.get("REPO_ORIGIN", "My iOS Repo"))
    parser.add_argument("--label", default=os.environ.get("REPO_LABEL", "My iOS Repo"))
    parser.add_argument("--suite", default=os.environ.get("REPO_SUITE", "stable"))
    parser.add_argument("--version", default=os.environ.get("REPO_VERSION", "1.0"))
    parser.add_argument("--codename", default=os.environ.get("REPO_CODENAME", "ios"))
    parser.add_argument(
        "--architectures",
        default=os.environ.get("REPO_ARCHITECTURES", "iphoneos-arm iphoneos-arm64"),
    )
    parser.add_argument(
        "--components", default=os.environ.get("REPO_COMPONENTS", "main")
    )
    parser.add_argument(
        "--description",
        default=os.environ.get("REPO_DESCRIPTION", "A jailbreak package repository"),
    )
    args = parser.parse_args()

    root = args.root
    present = [name for name in CANDIDATES if os.path.isfile(os.path.join(root, name))]
    if not present:
        print("警告：未找到 Packages* 文件，Release 校验和段将为空", file=sys.stderr)

    lines = [
        f"Origin: {args.origin}",
        f"Label: {args.label}",
        f"Suite: {args.suite}",
        f"Version: {args.version}",
        f"Codename: {args.codename}",
        f"Architectures: {args.architectures}",
        f"Components: {args.components}",
        f"Description: {args.description}",
        "Date: " + formatdate(datetime.now(timezone.utc).timestamp(), usegmt=True),
    ]

    for header, algo in CHECKSUMS:
        lines.append("")
        lines.append(f"{header}:")
        for name in present:
            path = os.path.join(root, name)
            size = os.path.getsize(path)
            lines.append(f" {digest_file(path, algo)} {size} {name}")

    release_path = os.path.join(root, "Release")
    with open(release_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"已生成 {release_path}")


if __name__ == "__main__":
    main()