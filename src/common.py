"""Shared paths, loaders, and chart style for the analysis notebooks."""

import json
from pathlib import Path

import matplotlib as mpl
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
FIGURES = ROOT / "figures"
PROCESSED.mkdir(parents=True, exist_ok=True)
FIGURES.mkdir(parents=True, exist_ok=True)

# ChatGPT public release. Months from December 2022 on are "post".
CHATGPT = pd.Timestamp("2022-11-30")
POST_START = pd.Timestamp("2022-12-01")

# --- chart palette (validated reference palette, light mode) ---------------
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
SERIES = [BLUE, ORANGE, AQUA, YELLOW]
ORDINAL_BLUE = ["#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]  # ordered bands, light -> dark
CONTEXT_GREY = "#c3c2b7"  # de-emphasised comparison bars / bands
INK, INK_2, MUTED = "#0b0b0b", "#52514e", "#898781"
GRID, BASELINE, SURFACE = "#e1e0d9", "#c3c2b7", "#fcfcfb"


def set_style():
    mpl.rcParams.update({
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
        "figure.dpi": 110, "savefig.dpi": 200,
        "font.family": "sans-serif",
        "font.sans-serif": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
        "font.size": 10, "axes.titlesize": 11, "axes.titleweight": "bold", "axes.titlelocation": "left",
        "axes.titlecolor": INK, "axes.labelcolor": INK_2,
        "axes.edgecolor": BASELINE, "axes.linewidth": 0.8,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "axes.axisbelow": True,
        "grid.color": GRID, "grid.linewidth": 0.6, "grid.linestyle": "-",
        "xtick.color": MUTED, "ytick.color": MUTED, "xtick.labelcolor": INK_2, "ytick.labelcolor": INK_2,
        "lines.linewidth": 2, "lines.markersize": 6,
        "legend.frameon": False, "legend.fontsize": 9, "legend.labelcolor": INK_2,
        "axes.prop_cycle": mpl.cycler(color=SERIES),
    })


def mark_chatgpt(ax, x=CHATGPT, label=True, y=0.98):
    """Solid hairline at the ChatGPT release (x can be a year position, e.g. 2022.5)."""
    ax.axvline(x, color=MUTED, lw=1, zorder=1)
    if label:
        ax.text(x, y, " ChatGPT release", transform=ax.get_xaxis_transform(),
                color=INK_2, fontsize=8, va="top", ha="left")


def label_end(ax, x, y, text, dy=0):
    """Direct label just right of a line's last point, in text ink (not the series color)."""
    ax.annotate(text, (x, y), xytext=(5, dy), textcoords="offset points",
                va="center", ha="left", fontsize=8.5, color=INK_2)


def save(fig, name):
    path = FIGURES / f"{name}.png"
    fig.savefig(path, bbox_inches="tight")
    return path


# --- loaders ------------------------------------------------------------------
def load_fred(series_id):
    df = pd.read_csv(RAW / "fred" / f"{series_id}.csv", parse_dates=["date"])
    return df.set_index("date")["value"].rename(series_id)


def fred_meta():
    return json.loads((RAW / "fred" / "_metadata.json").read_text())


OEWS_YEARS = range(2019, 2026)
OEWS_NUMERIC = ["TOT_EMP", "A_MEAN", "A_PCT10", "A_PCT25", "A_MEDIAN", "A_PCT75", "A_PCT90"]


def load_oews(year):
    """National cross-industry OEWS estimates for one May reference year (detailed + total rows)."""
    yy = str(year)[2:]
    df = pd.read_excel(RAW / "bls_oews" / f"oesm{yy}nat" / f"national_M{year}_dl.xlsx")
    df.columns = df.columns.str.upper()
    df = df[df["O_GROUP"].isin(["detailed", "total"])].copy()
    for c in OEWS_NUMERIC:  # '#' = top-coded wage, '*'/'**' = suppressed -> NaN
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["YEAR"] = year
    return df[["YEAR", "OCC_CODE", "OCC_TITLE", "O_GROUP"] + OEWS_NUMERIC]


def load_exposure():
    """Eloundou et al. (2024) exposure, averaged from O*NET-SOC 8-digit to 6-digit SOC."""
    exp = pd.read_csv(RAW / "exposure" / "eloundou_2023_occ_level.csv")
    exp["OCC_CODE"] = exp["O*NET-SOC Code"].str[:7]
    cols = ["dv_rating_alpha", "dv_rating_beta", "human_rating_alpha", "human_rating_beta"]
    return exp.groupby("OCC_CODE")[cols].mean()


def load_aioe():
    """Felten, Raj & Seamans (2021) AI Occupational Exposure by 6-digit SOC (SOC-2010 codes, so
    occupations recoded in SOC 2018 do not match and drop out)."""
    a = pd.read_excel(RAW / "exposure" / "felten_aioe_data_appendix.xlsx", sheet_name="Appendix A")
    return a.rename(columns={"SOC Code": "OCC_CODE", "AIOE": "aioe"}).set_index("OCC_CODE")[["aioe"]]


def wavg(x, w):
    x, w = np.asarray(x, float), np.asarray(w, float)
    ok = ~(np.isnan(x) | np.isnan(w))
    if not ok.any() or w[ok].sum() == 0:
        return np.nan
    return np.average(x[ok], weights=w[ok])
