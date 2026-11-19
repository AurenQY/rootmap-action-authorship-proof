"""Check the public, self-contained claims in this repository. Python 3, standard library only.
Usage: python verify.py
Checks: the Douyin ID's embedded time, and the SHA-256 of manifest.csv and the reference frames against claims.json.
Platform pages and the date of the post under review must be checked by hand (see AGENTS.md)."""
import datetime
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
claims = json.load(open(os.path.join(HERE, "claims.json"), encoding="utf-8"))
ok = True


def sha256(path):
    h = hashlib.sha256()
    with open(os.path.join(HERE, path), "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def report(name, passed, detail):
    global ok
    ok &= passed
    print(f"[{'PASS' if passed else 'FAIL'}] {name}: {detail}")


dy = next(p for p in claims["first_publication"]["platforms"] if p["platform"] == "Douyin")
t = datetime.datetime.fromtimestamp(int(dy["id"]) >> 32, datetime.timezone.utc)
release = datetime.datetime.fromisoformat(claims["first_publication"]["time_utc"].replace("Z", "+00:00"))
report("Douyin ID embedded time", t.isoformat().startswith(dy["id_embedded_time_utc"][:19]) and t <= release,
       f"{t.isoformat()} (public release {release.isoformat()})")

m = claims["manifest"]
report("manifest.csv sha256", sha256(m["file"]) == m["sha256"], m["sha256"])
for fr in claims["reference_frames"]:
    report(f"{fr['file']} sha256", sha256(fr["file"]) == fr["sha256"], fr["sha256"][:16] + "...")

print("\nAll self-contained checks passed." if ok else "\nSome checks FAILED.")
print("Still check by hand: the platform pages, and that the post under review is dated after", release.isoformat())
