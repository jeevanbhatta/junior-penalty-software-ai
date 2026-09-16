"""
Download all public data used in this project into data/raw/.

Every source is a real, citable public dataset (see data/SOURCES.md).
Run from the project root:

    .venv/bin/python src/fetch_data.py            # everything
    .venv/bin/python src/fetch_data.py fred       # one source

Requires FRED_API_KEY in .env (free: https://fred.stlouisfed.org/docs/api/api_key.html).
"""

import json
import os
import sys
import time
import zipfile
from datetime import date
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
load_dotenv(ROOT / ".env")

BROWSER_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)

# ---------------------------------------------------------------------------
# 1. FRED (Federal Reserve Bank of St. Louis)
# ---------------------------------------------------------------------------
# Indeed Hiring Lab job-postings indices (daily, SA, 1 Feb 2020 = 100),
# redistributed on FRED. One series per Indeed occupational category.
INDEED_SERIES = {
    "IHLIDXUS": "All postings",
    "IHLIDXUSTPSOFTDEVE": "Software Development",
    "IHLIDXUSTPITOPHE": "IT Operations & Helpdesk",
    "IHLIDXUSTPMATH": "Mathematics",
    "IHLIDXUSTPINDEDO": "Information Design & Documentation",
    "IHLIDXUSTPSCREDE": "Scientific Research & Development",
    "IHLIDXUSTPELECENGI": "Electrical Engineering",
    "IHLIDXUSTPCIVIENGI": "Civil Engineering",
    "IHLIDXUSTPINDUENGI": "Industrial Engineering",
    "IHLIDXUSTPARCH": "Architecture",
    "IHLIDXUSTPBAFI": "Banking & Finance",
    "IHLIDXUSTPACCO": "Accounting",
    "IHLIDXUSTPINSU": "Insurance",
    "IHLIDXUSTPLEGA": "Legal",
    "IHLIDXUSTPMARK": "Marketing",
    "IHLIDXUSTPMECO": "Media & Communications",
    "IHLIDXUSTPHUMARESO": "Human Resources",
    "IHLIDXUSTPMANA": "Management",
    "IHLIDXUSTPPROJMANA": "Project Management",
    "IHLIDXUSTPADMIASSI": "Administrative Assistance",
    "IHLIDXUSTPCUSTSERV": "Customer Service",
    "IHLIDXUSTPSALE": "Sales",
    "IHLIDXUSTPRETA": "Retail",
    "IHLIDXUSTPAREN": "Arts & Entertainment",
    "IHLIDXUSTPEDIN": "Education & Instruction",
    "IHLIDXUSTPNURS": "Nursing",
    "IHLIDXUSTPPHSU": "Physicians & Surgeons",
    "IHLIDXUSTPTHER": "Therapy",
    "IHLIDXUSTPPHAR": "Pharmacy",
    "IHLIDXUSTPDENT": "Dental",
    "IHLIDXUSTPMEDITECH": "Medical Technician",
    "IHLIDXUSTPMEDIINFO": "Medical Information",
    "IHLIDXUSTPVETE": "Veterinary",
    "IHLIDXUSTPPECAHOHE": "Personal Care & Home Health",
    "IHLIDXUSTPCOSOSE": "Community & Social Service",
    "IHLIDXUSTPCHIL": "Childcare",
    "IHLIDXUSTPCONS": "Construction",
    "IHLIDXUSTPINMA": "Installation & Maintenance",
    "IHLIDXUSTPPRMA": "Production & Manufacturing",
    "IHLIDXUSTPLOGISUPP": "Logistic Support",
    "IHLIDXUSTPLOST": "Loading & Stocking",
    "IHLIDXUSTPDRIV": "Driving",
    "IHLIDXUSTPCLSA": "Cleaning & Sanitation",
    "IHLIDXUSTPFOPRSE": "Food Preparation & Service",
    "IHLIDXUSTPHOTO": "Hospitality & Tourism",
    "IHLIDXUSTPSEPUSA": "Security & Public Safety",
    "IHLIDXUSTPBEWE": "Beauty & Wellness",
    "IHLIDXUSTPSPOR": "Sports",
}

# BLS CES / CPS / JOLTS and macro controls, as redistributed on FRED.
MACRO_SERIES = [
    # CES industry payrolls (thousands, SA)
    "PAYEMS",          # total nonfarm
    "CES6054150001",   # computer systems design & related services (NAICS 5415)
    "CES5051800001",   # computing infrastructure, data processing, web hosting (NAICS 518)
    "USINFO",          # information sector
    "CES6054000001",   # professional, scientific & technical services
    # CPS unemployment rates by age (%, SA)
    "UNRATE",
    "LNS14024887",     # 16-24
    "LNS14000036",     # 20-24
    "LNS14000089",     # 25-34
    "LNS14000060",     # 25-54
    "LNS14027662",     # bachelor's degree and higher, 25+
    # Monetary-policy confounder
    "FEDFUNDS",
]


def fred_get(path: str, **params) -> dict:
    params.update(api_key=os.environ["FRED_API_KEY"], file_type="json")
    for attempt in range(5):
        time.sleep(0.6)  # FRED allows ~120 requests/minute
        r = requests.get(f"https://api.stlouisfed.org/fred/{path}", params=params, timeout=60)
        if r.status_code == 429 or r.status_code >= 500:
            time.sleep(5 * 2 ** attempt)
            continue
        break
    if not r.ok:  # don't let the exception message echo the API key in the URL
        raise requests.HTTPError(f"HTTP {r.status_code} for {path} {params.get('series_id')}")
    return r.json()


def fetch_fred():
    out = RAW / "fred"
    out.mkdir(parents=True, exist_ok=True)
    meta = {}
    for sid in list(INDEED_SERIES) + MACRO_SERIES:
        try:
            info = fred_get("series", series_id=sid)["seriess"][0]
            obs = fred_get("series/observations", series_id=sid)["observations"]
        except requests.HTTPError as e:
            print(f"  {sid}: FAILED ({e})")
            continue
        df = pd.DataFrame(obs)[["date", "value"]]
        df["value"] = pd.to_numeric(df["value"], errors="coerce")  # FRED uses "." for missing
        df.to_csv(out / f"{sid}.csv", index=False)
        meta[sid] = {k: info[k] for k in ("title", "units", "frequency", "seasonal_adjustment",
                                           "observation_start", "observation_end", "last_updated")}
        meta[sid]["notes"] = info.get("notes", "")
        meta[sid]["url"] = f"https://fred.stlouisfed.org/series/{sid}"
        print(f"  {sid}: {len(df)} obs, {info['observation_start']} -> {info['observation_end']}")
    meta["_retrieved"] = date.today().isoformat()
    (out / "_metadata.json").write_text(json.dumps(meta, indent=2))


# ---------------------------------------------------------------------------
# 2. BLS Occupational Employment and Wage Statistics (OEWS), national, May 2019-2025
# ---------------------------------------------------------------------------
# bls.gov blocks scripted downloads (HTTP 403), so the identical zip files are
# pulled from the Internet Archive's snapshots of the official URLs.
def fetch_oews(years=range(2019, 2026)):
    out = RAW / "bls_oews"
    out.mkdir(parents=True, exist_ok=True)
    for y in years:
        yy = str(y)[2:]
        dest = out / f"oesm{yy}nat.zip"
        if not dest.exists():
            official = f"https://www.bls.gov/oes/special-requests/oesm{yy}nat.zip"
            r = requests.get(f"https://web.archive.org/web/2026id_/{official}", timeout=300)
            r.raise_for_status()
            dest.write_bytes(r.content)
        with zipfile.ZipFile(dest) as z:
            z.extractall(out)
        print(f"  OEWS May {y}: ok")


# ---------------------------------------------------------------------------
# 3. Stack Overflow Developer Survey microdata 2021-2025 (ODbL)
# ---------------------------------------------------------------------------
def fetch_stackoverflow(years=range(2021, 2026)):
    base = "https://media.githubusercontent.com/media/StackExchange/Survey/main/packages/archive"
    for y in years:
        d = RAW / "stackoverflow" / "microdata" / str(y)
        d.mkdir(parents=True, exist_ok=True)
        for f in ("results.csv", "schema.csv"):
            if (d / f).exists() and (d / f).stat().st_size > 1000:
                continue
            with requests.get(f"{base}/{y}/{f}", stream=True, timeout=600) as r:
                r.raise_for_status()
                with open(d / f, "wb") as fh:
                    for chunk in r.iter_content(1 << 20):
                        fh.write(chunk)
        print(f"  Stack Overflow {y}: ok")


# ---------------------------------------------------------------------------
# 4. Eloundou, Manning, Mishkin & Rock (2024, Science) GPT exposure scores
# ---------------------------------------------------------------------------
def fetch_exposure():
    out = RAW / "exposure"
    out.mkdir(parents=True, exist_ok=True)
    url = "https://raw.githubusercontent.com/openai/GPTs-are-GPTs/main/data/occ_level.csv"
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    (out / "eloundou_2023_occ_level.csv").write_bytes(r.content)
    print("  Eloundou et al. exposure: ok")
    # Felten, Raj & Seamans (2021, SMJ) AI Occupational Exposure (AIOE), used as a robustness measure
    r = requests.get("https://github.com/AIOE-Data/AIOE/raw/main/AIOE_DataAppendix.xlsx", timeout=120)
    r.raise_for_status()
    (out / "felten_aioe_data_appendix.xlsx").write_bytes(r.content)
    print("  Felten et al. AIOE: ok")


# ---------------------------------------------------------------------------
# 5. Federal Reserve Bank of New York: Labor Market for Recent College Graduates
# ---------------------------------------------------------------------------
def fetch_nyfed():
    out = RAW / "nyfed"
    out.mkdir(parents=True, exist_ok=True)
    base = "https://www.newyorkfed.org/medialibrary/research/interactives/data/college-labor-market"
    for f in ("college-labor-unemployment-data.csv", "college-labor-underemployment-data.csv",
              "college-labor-wages-data.csv", "college-labor-outcomes-by-major-data.csv",
              "college-labor-chart-meta.json"):
        r = requests.get(f"{base}/{f}", headers={"User-Agent": BROWSER_UA}, timeout=60)
        r.raise_for_status()
        (out / f).write_bytes(r.content)
    print("  NY Fed recent grads: ok")


# ---------------------------------------------------------------------------
# 6. Census Bureau Current Population Survey (CPS) basic monthly public-use microdata
# ---------------------------------------------------------------------------
# Jan 2020 onward uses 2018 Census occupation codes throughout (software developers = 1021,
# QA testers = 1022, programmers = 1010), so the extract starts there. Only employed persons
# aged 16+ and the handful of variables used in notebook 05 are kept.
CPS_MONTHS = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
CPS_COLS = ["hryear4", "hrmonth", "hrmis", "prtage", "pemlr", "ptio1ocd", "peio1cow",
            "peeduca", "pwcmpwgt", "pternwa", "pworwgt"]


def _cps_month(y, m):
    """Stream one month's public-use CSV (the zips hold fixed-width .dat) and keep employed persons."""
    out = RAW / "cps"
    name = f"{CPS_MONTHS[m - 1]}{str(y)[2:]}pub"
    dest = out / f"{name}_employed.csv.gz"
    if dest.exists():
        return name, "cached"
    url = f"https://www2.census.gov/programs-surveys/cps/datasets/{y}/basic/{name}.csv"
    if requests.head(url, headers={"User-Agent": BROWSER_UA}, timeout=60).status_code == 404:
        return name, "missing"
    # Jan-Feb 2021 files label the occupation code peio1ocd (and weekly earnings prernwa) instead
    alt = {"peio1ocd": "ptio1ocd", "prernwa": "pternwa"}
    df = pd.read_csv(url, usecols=lambda c: c.lower() in CPS_COLS or c.lower() in alt,
                     storage_options={"User-Agent": BROWSER_UA})
    df.columns = df.columns.str.lower()
    df = df.rename(columns={k: v for k, v in alt.items() if k in df.columns and v not in df.columns})
    df = df[df.pemlr.isin([1, 2]) & (df.prtage >= 16)]  # employed (at work / absent)
    df.to_csv(dest, index=False)
    return name, f"{len(df)} employed persons"


def fetch_cps(start=2020, end=date.today().year):
    from concurrent.futures import ThreadPoolExecutor
    (RAW / "cps").mkdir(parents=True, exist_ok=True)
    months = [(y, m) for y in range(start, end + 1) for m in range(1, 13)
              if (y, m) <= (date.today().year, date.today().month)]
    with ThreadPoolExecutor(max_workers=4) as pool:
        for name, status in pool.map(lambda ym: _cps_month(*ym), months):
            print(f"  CPS {name}: {status}")


SOURCES = {
    "fred": fetch_fred,
    "cps": fetch_cps,
    "oews": fetch_oews,
    "stackoverflow": fetch_stackoverflow,
    "exposure": fetch_exposure,
    "nyfed": fetch_nyfed,
}

if __name__ == "__main__":
    for name in sys.argv[1:] or SOURCES:
        print(f"[{name}]")
        SOURCES[name]()
