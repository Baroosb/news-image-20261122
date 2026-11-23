#!/usr/bin/env python3
"""Entry program for the news-image-20261122 make.fun entry.

The finished page lives beside this file as entry.png: a one-image
broadsheet summing up Sunday 22 November 2026, rendered by build.py
from the fact-audited story set in STORIES.md (see AUDIT.md for the
audit trail). Running this program publishes those exact bytes into
the output directory, unchanged, every single run.

The grader's output directory is /output; when running anywhere else,
point MAKEFUN_OUTPUT_DIR at the directory to fill instead.
"""

import os
import shutil
from pathlib import Path


def publish_page():
    # entry.png is the whole entry: copy it byte for byte, nothing else.
    page = Path(__file__).resolve().parent / "entry.png"
    target_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    target_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(page, target_dir / page.name)
    return target_dir / page.name


if __name__ == "__main__":
    publish_page()
