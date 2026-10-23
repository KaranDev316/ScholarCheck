"""Load the four regression fixtures into a PostgreSQL database.

Run: DATABASE_URL=postgresql://... python -m app.storage.load_seeds
This is a development fixture loader, not a publication workflow.
"""

import argparse
from pathlib import Path

import psycopg

from app.config import load_settings
from app.storage.opportunities import CONTENT_DIR, create_schema, load_seed, read_seed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--content-dir",
        type=Path,
        default=CONTENT_DIR,
        help="Directory containing one Opportunity YAML per file",
    )
    args = parser.parse_args()
    database_url = load_settings().database_url
    if not database_url:
        parser.error("DATABASE_URL is required to load fixtures")

    paths = sorted(args.content_dir.glob("*.yaml"))
    if not paths:
        parser.error("No opportunity YAML files found")
    opportunities = [read_seed(path) for path in paths]
    if len({item.id for item in opportunities}) != len(opportunities):
        parser.error("Opportunity ids must be unique across files")

    with psycopg.connect(database_url) as conn:
        create_schema(conn)
        changed = sum(load_seed(conn, opportunity) for opportunity in opportunities)
    print(f"Loaded {len(opportunities)} fixtures; {changed} changed.")


if __name__ == "__main__":
    main()
