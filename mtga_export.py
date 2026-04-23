#!/usr/bin/env python3
"""Export an MTG Arena collection to CSV via mtga-tracker-daemon + Scryfall."""
import argparse
import csv
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from lands_report import render_lands_html

SCRYFALL_BULK_INDEX = "https://api.scryfall.com/bulk-data"

HEADERS = {
    "User-Agent": "mtga-arena-exporter/0.1 (+https://github.com/uzimith/mtg-arena-exporter)",
    "Accept": "application/json",
}


def _request(url: str, accept: str) -> urllib.request.Request:
    headers = dict(HEADERS)
    headers["Accept"] = accept
    return urllib.request.Request(url, headers=headers)


def fetch_json(url: str, accept: str = "application/json"):
    req = _request(url, accept)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        if e.code in (400, 403):
            print(
                f"! {url} returned HTTP {e.code}. "
                "Scryfall requires a User-Agent and Accept header on every request.",
                file=sys.stderr,
            )
        elif e.code == 429:
            print("! Scryfall rate limit hit. Wait ~1 minute and retry.", file=sys.stderr)
        raise


def download_file(url: str, dest: Path) -> None:
    req = _request(url, "*/*")
    with urllib.request.urlopen(req, timeout=300) as r, dest.open("wb") as f:
        while True:
            chunk = r.read(1 << 20)
            if not chunk:
                break
            f.write(chunk)


def load_scryfall_arena_map(cache_dir: Path) -> dict:
    cache_dir.mkdir(parents=True, exist_ok=True)
    print("→ fetching Scryfall bulk-data index...")
    index = fetch_json(SCRYFALL_BULK_INDEX)
    time.sleep(0.1)
    default = next(b for b in index["data"] if b["type"] == "default_cards")

    dest = cache_dir / "default_cards.json"
    stamp = cache_dir / "default_cards.updated_at"
    current = default["updated_at"]
    cached = stamp.read_text(errors="ignore").strip() if stamp.exists() else ""

    if not dest.exists() or cached != current:
        size_mb = default.get("size", 0) // (1024 * 1024)
        print(f"→ downloading default_cards ({size_mb} MB)...")
        download_file(default["download_uri"], dest)
        stamp.write_text(current)
    else:
        print("✓ using cached default_cards.json")

    arena_map: dict[int, dict] = {}
    with dest.open("r", encoding="utf-8") as f:
        cards = json.load(f)
    for c in cards:
        aid = c.get("arena_id")
        if aid is not None:
            arena_map[int(aid)] = c
    return arena_map


def query_daemon(base: str) -> list:
    base = base.rstrip("/")
    last_err: Exception | None = None
    for path in ("/cards", "/collection"):
        url = base + path
        try:
            data = fetch_json(url)
        except Exception as e:
            last_err = e
            continue
        cards = data.get("cards") if isinstance(data, dict) else data
        if cards is None and isinstance(data, dict):
            cards = data.get("collection")
        if isinstance(cards, list) and cards:
            print(f"✓ using endpoint {path} ({len(cards)} cards)")
            return cards
    raise SystemExit(
        f"! daemon at {base} returned no collection data. "
        "Start Arena, log in, open the Collection screen, then retry. "
        f"(last error: {last_err})"
    )


def extract_entry(entry: dict) -> tuple[int, int]:
    grp = entry.get("grpId") or entry.get("id") or entry.get("arena_id")
    count = (
        entry.get("owned")
        if entry.get("owned") is not None
        else entry.get("count") if entry.get("count") is not None
        else entry.get("quantity", 0)
    )
    return int(grp), int(count)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--daemon", default="http://localhost:6842",
                   help="mtga-tracker-daemon base URL")
    p.add_argument("--out", default="mtga_collection.csv",
                   help="output CSV path")
    p.add_argument("--cache", default=str(Path.home() / ".cache" / "mtga-export"),
                   help="Scryfall bulk-data cache directory")
    p.add_argument("--html", default=None,
                   help="optional HTML 2-color land report output path")
    args = p.parse_args()

    print(f"→ querying daemon at {args.daemon}")
    raw = query_daemon(args.daemon)

    arena_map = load_scryfall_arena_map(Path(args.cache))

    rows = []
    missing: list[tuple[int, int]] = []
    for entry in raw:
        grp, count = extract_entry(entry)
        if count <= 0:
            continue
        card = arena_map.get(grp)
        if card is None:
            missing.append((grp, count))
            continue
        rows.append({
            "Count": count,
            "Name": card.get("name", ""),
            "Set Code": card.get("set", "").upper(),
            "Set Name": card.get("set_name", ""),
            "Collector Number": card.get("collector_number", ""),
            "Rarity": card.get("rarity", ""),
            "Scryfall ID": card.get("id", ""),
        })

    out = Path(args.out)
    fields = ["Count", "Name", "Set Code", "Set Name",
              "Collector Number", "Rarity", "Scryfall ID"]
    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    print(f"✓ wrote {out} ({len(rows)} rows)")

    if args.html:
        html_path = Path(args.html)
        html_path.write_text(render_lands_html(rows), encoding="utf-8")
        print(f"✓ wrote {html_path}")

    if missing:
        print(f"! {len(missing)} grpIds had no Scryfall arena_id match "
              "(typically Alchemy or rebalanced cards):")
        for grp, count in missing[:10]:
            print(f"    grpId={grp} count={count}")
        if len(missing) > 10:
            print(f"    ... and {len(missing) - 10} more")
    return 0


if __name__ == "__main__":
    sys.exit(main())
