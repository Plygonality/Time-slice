from __future__ import annotations

import json
import os
from pathlib import Path

from time_slice.epochs import slice_seed

GOLDEN = Path(__file__).parent / "goldens" / "seed_1234.json"


def test_canonical_seed_matches_golden() -> None:
    got = slice_seed(1234).to_dict()
    if os.environ.get("UPDATE_GOLDENS") == "1":
        GOLDEN.write_text(json.dumps(got, indent=2) + "\n", encoding="utf-8")
    expected = json.loads(GOLDEN.read_text(encoding="utf-8"))
    assert got == expected
