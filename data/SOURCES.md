# Data sources

Every file under `data/raw/` comes from a public source listed below and can be re-downloaded with `src/fetch_data.py`. **No data in this project is simulated or synthetic.** An earlier draft used a randomly generated "calibrated" job-postings panel; that notebook, its figures, and all the numbers derived from it were deleted on 2026-09-13.

Retrieval date for all files: **2026-09-13** unless noted.

---

## 1. Indeed Hiring Lab job postings indices (via FRED)

- **Files:** `data/raw/fred/IHLIDXUS*.csv` (48 series), metadata in `data/raw/fred/_metadata.json`
- **What:** Daily, seasonally adjusted index of job postings on Indeed, 1 Feb 2020 = 100, for all US postings and for each Indeed occupational category (Software Development, Accounting, Nursing, …).
- **Coverage:** 2020-02-01 to 2026-09-04. The Mathematics, IT Operations & Helpdesk, and Information Design & Documentation series stop on 2025-07-18, and a few others stop earlier (see metadata).
- **Cite as:** Indeed Hiring Lab, *Job Postings on Indeed in the United States* [IHLIDXUS; IHLIDXUSTPSOFTDEVE; …], retrieved from FRED, Federal Reserve Bank of St. Louis, https://fred.stlouisfed.org/series/IHLIDXUSTPSOFTDEVE, September 13, 2026.
- **Upstream:** https://github.com/hiring-lab/job_postings_tracker
- **Caveats:** The index measures how many postings there are, not hires, and says nothing about seniority. Its categories do not map one-to-one to SOC codes, and it cannot separate junior from senior postings.

## 2. BLS Current Employment Statistics, Current Population Survey (via FRED)

- **Files:** `data/raw/fred/{PAYEMS, CES6054150001, CES5051800001, USINFO, CES6054000001, UNRATE, LNS14024887, LNS14000036, LNS14000089, LNS14000060, LNS14027662, FEDFUNDS}.csv`
- **What:** Monthly SA payroll employment for Computer Systems Design & Related Services (NAICS 5415), Computing Infrastructure/Data Processing/Web Hosting (NAICS 518), Information, and Professional/Scientific/Technical Services. CPS unemployment rates by age (16–24, 20–24, 25–34, 25–54) and for workers 25+ with a bachelor's degree. The effective federal funds rate is included as a monetary-policy confounder.
- **Cite as:** U.S. Bureau of Labor Statistics, *All Employees, Computer Systems Design and Related Services* [CES6054150001], retrieved from FRED, Federal Reserve Bank of St. Louis, https://fred.stlouisfed.org/series/CES6054150001, September 13, 2026. Other series are cited the same way.
- **License:** BLS data are in the public domain.

## 3. BLS Occupational Employment and Wage Statistics (OEWS), national, May 2019 to May 2025

- **Files:** `data/raw/bls_oews/oesm{19..25}nat.zip` and extracted `national_M{YEAR}_dl.xlsx`
- **What:** Employment and annual wage percentiles (10th, 25th, 50th, 75th, 90th) for about 830 detailed SOC occupations.
- **Cite as:** U.S. Bureau of Labor Statistics, *Occupational Employment and Wage Statistics, May 2019 to May 2025 National Estimates*, https://www.bls.gov/oes/tables.htm.
- **Retrieval note:** bls.gov returns HTTP 403 to scripted downloads. The unmodified official zip files were retrieved from Internet Archive snapshots of the official URLs (`https://web.archive.org/web/2026id_/https://www.bls.gov/oes/special-requests/oesm{YY}nat.zip`; snapshots dated 2025-12-20 for 2019 and 2021–2024, and 2026-09-11 for 2020 and 2025). A few values were spot-checked against the live BLS API: Software Developers, May 2025, employment 1,687,890 and median $135,980 both match.
- **Caveats:**
  - May 2019 and 2020 use hybrid SOC codes. Software Developers and QA Testers are combined as 15-1256, which is 15-1252 + 15-1253 from May 2021 on.
  - Wages above the BLS top-code (`#`) are treated as missing.
  - OEWS is a 3-year rolling sample, so year-to-year changes are smoothed and BLS advises against using it as a strict time series.
- **License:** Public domain.

## 4. GPT exposure scores (Eloundou, Manning, Mishkin & Rock)

- **File:** `data/raw/exposure/eloundou_2023_occ_level.csv`
- **What:** Occupation-level (O*NET-SOC 2019) share of tasks exposed to LLMs, rated by humans and by GPT-4. α = E1 (direct exposure), β = E1 + 0.5·E2, γ = E1 + E2.
- **Cite as:** Eloundou, T., Manning, S., Mishkin, P., & Rock, D. (2024). GPTs are GPTs: Labor market impact potential of LLMs. *Science*, 384(6702), 1306–1308. https://doi.org/10.1126/science.adj0998. Data: https://github.com/openai/GPTs-are-GPTs

### 4b. AI Occupational Exposure (Felten, Raj & Seamans), robustness measure

- **File:** `data/raw/exposure/felten_aioe_data_appendix.xlsx` (sheet "Appendix A": AIOE by 6-digit SOC)
- **Cite as:** Felten, E. W., Raj, M., & Seamans, R. (2021). Occupational, industry, and geographic exposure to artificial intelligence: A novel dataset and its potential uses. *Strategic Management Journal*, 42(12), 2195–2217. https://doi.org/10.1002/smj.3286. Data: https://github.com/AIOE-Data/AIOE
- **Caveat:** AIOE is keyed to SOC-2010 codes. Occupations that were recoded in SOC 2018 do not match; the match rate is 93% of the OEWS 2019–25 panel.

## 5. Stack Overflow Annual Developer Survey microdata, 2021 to 2025

- **Files:** `data/raw/stackoverflow/microdata/{2021..2025}/results.csv` and `schema.csv`. Stack Overflow's published aggregate JSON files are in `data/raw/stackoverflow/published_json/`.
- **What:** Respondent-level survey data (roughly 49k–89k respondents per year): experience (`YearsCodePro` for 2021–2024, `WorkExp` for 2022–2025), self-reported compensation converted to USD (`ConvertedCompYearly`), country, employment, developer type, and AI-tool use (`AISelect` for 2023–2025, `AIThreat` for 2024–2025).
- **Cite as:** Stack Overflow (2021–2025). *Stack Overflow Annual Developer Survey*. https://survey.stackoverflow.co/. Data: https://github.com/StackExchange/Survey
- **License:** Open Database License (ODbL) v1.0; individual contents under the Database Contents License (DbCL) v1.0.
- **Caveats:** This is an opt-in convenience sample, not representative of the developer labor force. Its composition changes from year to year with recruitment, and pay is self-reported.

## 7. Current Population Survey (CPS) basic monthly public-use microdata, Jan 2020 to latest month

- **Files:** `data/raw/cps/{mon}{yy}pub_employed.csv.gz`, one per month. Each is an extract of employed persons aged 16+ (`pemlr` ∈ {1,2}).
- **Variables kept:** `hryear4`, `hrmonth`, `hrmis`, `prtage`, `pemlr`, `ptio1ocd` (2018 Census occupation code), `peio1cow`, `peeduca`, `pwcmpwgt` (composite weight), `pternwa` (weekly earnings, outgoing rotation groups only), `pworwgt` (earnings weight).
- **Source:** U.S. Census Bureau & Bureau of Labor Statistics, *Current Population Survey, Basic Monthly Public Use File*, https://www2.census.gov/programs-surveys/cps/datasets/{year}/basic/{mon}{yy}pub.csv
- **Cite as:** U.S. Census Bureau. *Current Population Survey Basic Monthly Public Use Microdata, January 2020 to August 2026*. Washington, DC. Accessed September 13, 2026.
- **Why it starts in 2020:** from January 2020 the CPS uses 2018 Census occupation codes throughout (software developers = 1021, QA analysts and testers = 1022, computer programmers = 1010). Earlier months use 2010 codes and are published only as fixed-width files.
- **Caveats:**
  - Monthly samples of software developers are small (a few hundred), so estimates are pooled by quarter or year.
  - Occupation is self-reported and coded by the Census Bureau. Rows without an occupation code are dropped.
  - **October 2025 does not exist.** The CPS was not collected that month because of the lapse in federal appropriations, and it cannot be collected retroactively (BLS, "Impact of the 2025 federal government shutdown on the CPS", https://www.bls.gov/cps/methods/2025-federal-government-shutdown-impact-cps.htm). The extract therefore has 79 months, Jan 2020 to Aug 2026.

## 6. Federal Reserve Bank of New York: The Labor Market for Recent College Graduates

- **Files:** `data/raw/nyfed/college-labor-{unemployment,underemployment,wages,outcomes-by-major}-data.csv`, `college-labor-chart-meta.json`
- **What:** Monthly unemployment and underemployment (smoothed CPS/IPUMS, 1990 to present) for recent graduates (ages 22–27, BA+), all college graduates, young workers, and all workers. The by-major table gives unemployment, underemployment, and wages, including Computer Science and Computer Engineering; it is a snapshot of the latest release.
- **Release:** August 6, 2026 (2026:Q2 data).
- **Cite as:** Federal Reserve Bank of New York, *The Labor Market for Recent College Graduates*, https://www.newyorkfed.org/research/college-labor-market, accessed September 13, 2026.
