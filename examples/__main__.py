"""Print the canonical seed as three briefs."""

from time_slice.brief import render_set
from time_slice.epochs import slice_seed

CANONICAL_SEED = 1234

if __name__ == "__main__":
    print(render_set(slice_seed(CANONICAL_SEED)))
