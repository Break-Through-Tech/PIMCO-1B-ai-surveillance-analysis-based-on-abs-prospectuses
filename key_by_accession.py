"""
Milestone 1, Week 2 (final): Key extracted text to accession numbers.
Matches each extracted .txt file to its filing's accession number via the manifest.
"""
import pandas as pd
from pathlib import Path

MANIFEST = "data/_manifest.csv"
EXTRACTED_INDEX = "data/extracted_index.csv"
OUTPUT = "data/extracted_index_keyed.csv"


def filename_from_path(p):
    """Grab just the filename from a path that may use / or \\ separators."""
    if pd.isna(p):
        return ""
    return str(p).replace("\\", "/").split("/")[-1]


def main():
    manifest = pd.read_csv(MANIFEST)
    index = pd.read_csv(EXTRACTED_INDEX)

    # Build a lookup: htm filename -> filing metadata
    manifest["htm_filename"] = manifest["local_path"].apply(filename_from_path)
    lookup = manifest.set_index("htm_filename")

    rows = []
    unmatched = []
    for _, row in index.iterrows():
        htm_name = row["source_file"]          # e.g. HYUNDAI..._424H.htm
        if htm_name in lookup.index:
            m = lookup.loc[htm_name]
            rows.append({
                "accession": m["accession"],
                "accession_clean": m["accession_clean"],
                "entity_name": m["entity_name"],
                "cik": m["cik"],
                "form": m["form"],
                "filing_date": m["filing_date"],
                "source_file": htm_name,
                "text_file": row["text_file"],
                "word_count": row["word_count"],
                "doc_url": m["doc_url"],
            })
        else:
            unmatched.append(htm_name)
            rows.append({
                "accession": "",
                "accession_clean": "",
                "entity_name": "",
                "cik": "",
                "form": "",
                "filing_date": "",
                "source_file": htm_name,
                "text_file": row["text_file"],
                "word_count": row["word_count"],
                "doc_url": "",
            })

    out = pd.DataFrame(rows)
    out.to_csv(OUTPUT, index=False)

    print(f"Matched {len(rows) - len(unmatched)}/{len(rows)} files to accession numbers.")
    if unmatched:
        print(f"\n{len(unmatched)} files could NOT be matched:")
        for u in unmatched:
            print("  ", u)
    print(f"\nKeyed index written to {OUTPUT}")


if __name__ == "__main__":
    main()