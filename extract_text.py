"""
Milestone 1, Week 2: Extract clean text from EDGAR 424H filings.
"""
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup
import re

TEXT_DIR = Path("data/extracted_text")
TEXT_DIR.mkdir(parents=True, exist_ok=True)


def extract_html_text(html):
    soup = BeautifulSoup(html, "lxml")

    for tag in soup(["script", "style", "head", "meta", "link"]):
        tag.decompose()

    # Tables: keep ones with real content, drop layout scaffolding
    for table in soup.find_all("table"):
        rows_out = []
        for tr in table.find_all("tr"):
            cells = [td.get_text(" ", strip=True) for td in tr.find_all(["td", "th"])]
            cells = [c for c in cells if c]           # drop empty spacer cells
            if cells:
                rows_out.append(" | ".join(cells))
        joined = "\n".join(rows_out)
        if len(joined.strip()) < 3:                   # basically empty = layout table
            table.decompose()
        else:
            table.replace_with("\n" + joined + "\n")

    text = soup.get_text(separator="\n")

    lines = [ln.strip() for ln in text.splitlines()]
    out, blank = [], False
    for ln in lines:
        if ln:
            out.append(ln); blank = False
        elif not blank:
            out.append(""); blank = True
    text = re.sub(r"\n{3,}", "\n\n", "\n".join(out))
    return text.strip()


def main():
    files = sorted(Path("data").glob("*.htm"))
    print(f"Found {len(files)} .htm files\n")

    rows = []
    for i, path in enumerate(files, 1):
        html = path.read_text(encoding="utf-8", errors="ignore")
        text = extract_html_text(html)
        out_name = path.stem + ".txt"
        (TEXT_DIR / out_name).write_text(text, encoding="utf-8")
        wc = len(text.split())
        rows.append({"source_file": path.name, "text_file": out_name, "word_count": wc})
        print(f"[{i}/{len(files)}] {path.name[:45]:45} {wc:>7} words")

    pd.DataFrame(rows).to_csv("data/extracted_index.csv", index=False)
    print(f"\nDone. Text files in {TEXT_DIR}/")
    print("Index written to data/extracted_index.csv")


if __name__ == "__main__":
    main()