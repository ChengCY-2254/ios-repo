#!/usr/bin/env python3
"""Generate the Release file for a Cydia/Sileo repository.

Usage: python3 scripts/gen-release.py --root .

Values can be overridden with CLI flags or environment variables
(REPO_ORIGIN, REPO_LABEL, REPO_SUITE, REPO_VERSION, REPO_CODENAME,
REPO_ARCHITECTURES, REPO_COMPONENTS, REPO_DESCRIPTION).
All Packages* files present in the root are checksummed into the release.
"""

import argparse
import hashlib
import os
import sys
from datetime import datetime, timezone
from email.utils import formatdate

CHUNK_SIZE = 1 << 20

CANDIDATES = [
    "Packages",
    "Packages.gz",
    "Packages.bz2",
    "Packages.xz",
    "Packages.lzma",
    "Packages.zst",
]

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
    parser = argparse.ArgumentParser(description="Generate Cydia/Sileo Release file")
    parser.add_argument("--root", default=".")
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
        print("warning: no Packages* files found", file=sys.stderr)

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
    print(f"wrote {release_path}")


if __name__ == "__main__":
    main()