# Context — Mutual Fund FAQ Assistant (RAG Chatbot)

## 1. Project Goal

Build a **facts-only FAQ assistant** for mutual fund schemes using a **Retrieval-Augmented Generation (RAG)** approach. The product context is **Groww**. The assistant answers objective, verifiable queries by retrieving information exclusively from official public sources (AMC websites, AMFI, SEBI). It must **never** provide investment advice, opinions, or recommendations.

---

## 2. Target Users

| Persona | Use-Case |
|---|---|
| Retail investors | Comparing mutual fund schemes with factual data |
| Customer support / content teams | Handling repetitive mutual fund queries |

---

## 3. Corpus Definition

- **AMC**: **HDFC Mutual Fund** (HDFC Asset Management Company)
- **Schemes**: **12 schemes** covering equity, index, hybrid, debt, and gold categories
- **Data Source Platform**: [Groww](https://groww.in)

### 3.1 Selected Scheme URLs

| # | Scheme | Category | Groww URL |
|---|--------|----------|-----------|
| 1 | HDFC Mid Cap Fund – Direct Growth | Mid-Cap Equity | [Link](https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth) |
| 2 | HDFC Equity Fund – Direct Growth | Multi-Cap / Flexi-Cap Equity | [Link](https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth) |
| 3 | HDFC Defence Fund – Direct Growth | Sectoral / Thematic Equity | [Link](https://groww.in/mutual-funds/hdfc-defence-fund-direct-growth) |
| 4 | HDFC Large and Mid Cap Fund – Direct Growth | Large & Mid-Cap Equity | [Link](https://groww.in/mutual-funds/hdfc-large-and-mid-cap-fund-direct-growth) |
| 5 | HDFC Large Cap Fund – Direct Growth | Large-Cap Equity | [Link](https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth) |
| 6 | HDFC Nifty LargeMidcap 250 Index Fund – Direct Growth | Index (Large+Mid) | [Link](https://groww.in/mutual-funds/hdfc-nifty-largemidcap-250-index-fund-direct-growth) |
| 7 | HDFC Nifty Top 20 Equal Weight Index Fund – Direct Growth | Index (Top 20 EW) | [Link](https://groww.in/mutual-funds/hdfc-nifty-top-20-equal-weight-index-fund-direct-growth) |
| 8 | HDFC Ultra Short Term Fund – Direct Growth | Debt (Ultra Short Term) | [Link](https://groww.in/mutual-funds/hdfc-ultra-short-term-fund-direct-growth) |
| 9 | HDFC Equity Savings Fund – Direct Growth | Hybrid (Equity Savings) | [Link](https://groww.in/mutual-funds/hdfc-equity-savings-fund-direct-growth) |
| 10 | HDFC Nifty 100 Index Fund – Direct Growth | Index (Nifty 100) | [Link](https://groww.in/mutual-funds/hdfc-nifty-100-index-fund-direct-growth) |
| 11 | HDFC Nifty100 Low Volatility 30 Index Fund – Direct Growth | Index (Low Vol 30) | [Link](https://groww.in/mutual-funds/hdfc-nifty100-low-volatility-30-index-fund-direct-growth) |
| 12 | HDFC Gold ETF Fund of Fund – Direct Plan Growth | Gold (FoF) | [Link](https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth) |

### 3.2 Data Source Scope

> **Only the 12 Groww URLs listed above serve as the data source.** No PDFs, KIM/SID documents, HDFC AMC pages, or other external sources are used.

---

## 4. Assistant Behavior

### 4.1 Answerable Queries (Facts-Only)

The assistant handles factual questions such as:

- Expense ratio of a scheme
- Exit load details
- Minimum SIP amount
- ELSS lock-in period
- Riskometer classification
- Benchmark index
- Process to download statements or capital gains reports

### 4.2 Response Format Rules

| Rule | Requirement |
|---|---|
| Length | **≤ 3 sentences** |
| Citation | Exactly **one** source link per response |
| Footer | `"Last updated from sources: <date>"` |

### 4.3 Refusal Handling

For non-factual or advisory queries (e.g., *"Should I invest in this fund?"*, *"Which fund is better?"*):

- Politely refuse with a clear explanation
- Reinforce the facts-only limitation
- Provide a relevant educational link (e.g., AMFI or SEBI resource)

---

## 5. User Interface (Minimal)

- A **welcome message**
- **Three example questions**
- A visible **disclaimer**: `"Facts-only. No investment advice."`

---

## 6. Constraints

### 6.1 Data & Sources

- Use **only** official public sources (AMC, AMFI, SEBI)
- **No** third-party blogs or aggregator websites

### 6.2 Privacy & Security

Absolutely **no** collection, storage, or processing of:

- PAN or Aadhaar numbers
- Account numbers
- OTPs
- Email addresses or phone numbers

### 6.3 Content Restrictions

- No investment advice or recommendations
- No performance comparisons or return calculations
- For performance queries → link to the official factsheet only

### 6.4 Transparency

- Responses must be short, factual, and verifiable
- Every answer must include a source link and a last-updated date

---

## 7. Expected Deliverables

| Deliverable | Details |
|---|---|
| **README** | Setup instructions, selected AMC & schemes, architecture overview (RAG approach), known limitations |
| **Disclaimer snippet** | `"Facts-only. No investment advice."` |
| **Working FAQ assistant** | RAG-based chatbot meeting all requirements above |

---

## 8. Success Criteria

1. Accurate retrieval of factual mutual fund information
2. Strict adherence to facts-only responses
3. Consistent inclusion of valid source citations
4. Proper refusal of advisory queries
5. Clean, minimal, and user-friendly interface

---

## 9. Summary

> Build a trustworthy, transparent, and compliant mutual fund FAQ assistant that prioritizes **accuracy over intelligence**. Users must receive only verified, source-backed financial information — with zero advisory bias or speculative content.
