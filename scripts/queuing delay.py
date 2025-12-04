import re
from collections import Counter
import numpy as np

# ── 1. log‑line pattern ────────────────────────────────────────────────────────
#   ['placeholder', 'Alabama', 41115, 'default prompt', [12, 'SE-SE3']]
#
#   • skip the first two comma‑separated fields
#   • capture the integer "seconds" at index‑2
#   • skip forward to the nested list at index‑4
#   • capture the zone string (either '...' or "...")
#
LINE_RE = re.compile(
    r"""\[
        (?:[^,]*,){2}\s*(\d+)        # group 1: seconds
        .*?                          # anything until …
        \[\s*\d+\s*,\s*              # 1st element of nested list
        ['"]([^'"]+)['"]             # group 2: zone (single or double quotes)
        \]""",
    re.VERBOSE,
)

def count_by_second(path: str, zone: str) -> Counter:
    counts = Counter()
    with open(path) as fh:
        for m in map(LINE_RE.search, fh):
            if not m:
                continue                      # malformed line → skip
            sec, z = m.groups()
            if z == zone:
                s = int(sec)
                if 0 <= s < 86_400:           # protect against bad values
                    counts[s] += 1
    return counts


# ── 2. read log and build arrival vector ───────────────────────────────────────
counts = count_by_second("requests_global.txt", "SE-SE3")
if not counts:
    raise ValueError("No matching records for zone 'SE-SE3'")

arr = np.zeros(86_400, np.int64)
for s, c in counts.items():
    arr[s] = c * 30            # one record = 30 individual requests


# ── 3. waiting‑time simulator (unchanged) ──────────────────────────────────────
def avg_wait(arrivals: np.ndarray, rate: int) -> float:
    q = 0
    wait_sum = 0
    served = 0
    for a in arrivals:
        wait_sum += q
        q += a
        serve = min(q, rate)
        q -= serve
        served += serve
    return wait_sum / served if served else float("nan")


# ── 4. run the scenario grid ───────────────────────────────────────────────────
for r in range(10, 750, 10):
    print(f"{r=:>4}  mean_wait={avg_wait(arr, r):.2f}s")
