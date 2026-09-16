# Tech Job Replacement: generative AI and early-career software work

Replication package: https://github.com/jeevanbhatta/junior-penalty-software-ai

**Research question.** Since ChatGPT's release (30 Nov 2022), has generative AI reduced demand for *junior* software developers relative to seniors, in postings, employment, or pay? This is the "junior penalty" hypothesis, framed with the task-based model of Acemoglu & Restrepo (2022).

**Status (2026-09-13).** Every result in this repository comes from public data (see [data/SOURCES.md](data/SOURCES.md)). The earlier notebook generated a *synthetic* "calibrated" job-postings panel with `np.random`. That notebook, its six figures, and the numbers in the old paper draft have been removed or archived; see "What changed" below.

**Read first:** [reports/junior_penalty_report.html](reports/junior_penalty_report.html), which covers the findings, the literature review and the references.

**The paper.** A working paper based on this analysis is kept outside the repository (`paper/`, not tracked) and is available from the author. This repository is its replication package: it reproduces every number in the paper.

## Layout

```
data/
  SOURCES.md          citation, URL, license and caveats for every dataset
  raw/                untouched downloads (fred/, bls_oews/, cps/, stackoverflow/, exposure/, nyfed/)
  processed/          tables written by the notebooks
notebooks/
  01_macro_context.ipynb           CES tech payrolls, CPS unemployment by age, NY Fed recent grads, Fed funds
  02_indeed_postings.ipynb         Indeed postings: software vs 47 occupations, DiD + permutation, event study
  03_oews_exposure.ipynb           OEWS 2019-25 software employment & wage percentiles; GPT-exposure event study
  04_stackoverflow_microdata.ipynb Stack Overflow 2021-25: junior-senior pay gap, AI use by experience
  05_cps_age_composition.ipynb     CPS microdata 2020-26: age mix of software developers vs 222 occupations
figures/              every chart the notebooks produce (the paper links here; no duplicates)
reports/              the written report (HTML)
src/
  fetch_data.py       downloads every dataset (python src/fetch_data.py [fred|oews|stackoverflow|exposure|nyfed|cps])
  common.py           paths, loaders, chart style shared by the notebooks
```

## Reproduce

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.template .env        # add a free FRED_API_KEY
.venv/bin/python src/fetch_data.py          # ~1.4 GB into data/raw/ (not tracked in git)
cd notebooks && for n in 0*.ipynb; do ../.venv/bin/jupyter nbconvert --to notebook --execute --inplace "$n"; done
```

## Headline results

| Source | Result |
|---|---|
| Indeed postings | Software postings fell 54% from Sep–Nov 2022 to Jun–Aug 2026, the most of the 41 occupational categories (DiD −0.59 log points, permutation p = 0.021). 58% of the fall from the Feb 2022 peak happened *before* ChatGPT. |
| BLS OEWS | Software developers & QA employment grew 8.3% from May 2022 to May 2025. P10 pay rose 15.7% vs 8.4% for P90, so the wage distribution *compressed*. |
| OEWS × GPT exposure | 1.7% lower employment per SD of exposure by 2025, with a pre-trend. The effect disappears with the Felten et al. AIOE measure. |
| CPS microdata | The 22–25 share of software developers went from 8.14% (2021–22) to 8.32% (2023–26). That ranks 102 of 222 occupations, with no relative decline; 2026 (7.5%) is the low point to watch. |
| Stack Overflow survey | The self-reported junior–senior pay gap widened 5–13% after 2022. This is the only source showing a pay penalty, and it is selection-prone. |
| NY Fed recent grads | Recent graduates' unemployment gap over all workers rose from +0.5 pp (2022) to +1.5 pp (2026). CS and computer engineering majors rank 4th and 2nd of 74. |

**Bottom line.** Hiring demand for software work collapsed and tilted toward experience. But much of the collapse predates ChatGPT and coincides with rate hikes. Representative data through mid-2026 shows no junior *employment* or *wage* penalty among employed developers yet.

## What changed on 2026-09-13

- **Deleted (synthetic):** `tech_job_replacement_analysis.ipynb`, which simulated 13,764 postings with `np.random`; its six PNGs; and `src/analysis_pipeline.py`.
- **Deleted (broken downloads):** HTML error pages saved as `.csv`/`.txt` (BLS "Access Denied", FRED bot pages, a Layoffs.fyi 404); git-LFS pointer files named `results_*.csv`; and 404 pages saved as JSON.
- **Deleted:** empty `Job/` and `Replacement/` scaffolding, and `src/data_sources.py`, which had mislabeled series IDs (replaced by `src/fetch_data.py`).
- **Archived:** `paper_draft.md` and `.tex` moved to `paper/archive_superseded/` with a warning banner. Its claimed "17.8% junior wage penalty" and "9.27 pp drop in junior posting share" came from the simulation and are not supported by any real source here.
- **References:** unverifiable bibliography entries were dropped. For example, no record of "Bessen, Impink & Seamans (2023), *The role of AI in commercial innovation and labor demand*" could be found.

## Verification

Every number in the paper and report was recomputed from source data by an independent script (77/79 checks matched exactly; the three discrepancies found were corrected). Every bibliography entry was checked against Crossref, the arXiv API, or the publisher's own page: all DOIs and arXiv IDs resolve with matching titles, and no link 404s.
