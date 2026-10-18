# Contributing to Traqify

Thanks for your interest in Traqify! This project is primarily an academic
(Informatics Practices) build, but issues, ideas and pull requests are welcome.

> **Licence note:** Traqify ships under a **restrictive, all-rights-reserved
> licence** (see [`LICENSE`](LICENSE)). By opening a pull request you agree that
> your contribution may be distributed under those same terms.

---

## Ways to contribute

| I want to…                       | Do this                                                      |
| -------------------------------- | ------------------------------------------------------------ |
| Report something broken          | Open a [bug report](.github/ISSUE_TEMPLATE/bug_report.yml)   |
| Suggest a feature or analytic     | Open a [feature request](.github/ISSUE_TEMPLATE/feature_request.yml) |
| Ask a setup question             | Start a Discussion                                           |
| Report a security issue          | Follow [`SECURITY.md`](SECURITY.md) — **do not** open a public issue |
| Send code                        | Open a pull request                                          |

---

## Local development

```bash
git clone https://github.com/sus6756/AI-supplychain.git
cd AI-supplychain

python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 1. Configure your database

Traqify reads its connection details from Streamlit secrets. Create
`.streamlit/secrets.toml` (this path is git-ignored):

```toml
DB_HOST     = "127.0.0.1"
DB_USER     = "your_user"
DB_PASSWORD = "your_password"
DB_NAME     = "supply_chain"
DB_PORT     = "3306"
```

The app creates its own tables on first boot. To seed the schema manually,
run the statements in [`project(mysql part)`](project(mysql%20part)).

> **macOS / local MySQL note:** `project.py` pins `ssl_ca` to the Linux CA bundle
> path used by Streamlit Community Cloud. Comment that key out when connecting to
> a local server without TLS.

### 2. Run it

```bash
streamlit run project.py
```

### 3. Load demo data

`sample/supply_chain_demo.xlsx` is a presentation-ready dataset (24 products,
10 suppliers, 147 shipments, 18 months of sales across 4 sheets). Upload it from
the sidebar's **Excel** tab to populate every dashboard.

Regenerate it at any time:

```bash
python sample/generate_demo_dataset.py
```

---

## Project layout

| Path                          | What it is                                            |
| ----------------------------- | ----------------------------------------------------- |
| `project.py`                  | The whole Streamlit application (~3.5k lines)         |
| `project`                     | Minimal reference workbook/dashboard script           |
| `project(mysql part)`         | Schema + sample analytics queries                     |
| `sample/`                     | Ready-to-upload demo workbooks                        |
| `.streamlit/config.toml`      | Deep-navy / cyan theme                                |
| `.devcontainer/`              | Codespaces / Dev Container config                     |
| `docs/screenshots/`           | Screenshots used by the README                        |

---

## Coding conventions

- **Python:** 4-space indentation, `snake_case`, type hints on helpers where practical.
- **Streamlit structure:** keep new UI inside the existing tab functions rather than
  appending to the router at the bottom of the file.
- **Styling:** reuse the CSS custom properties in the `:root` block
  (`--primary`, `--bg-card`, `--border`, …). Do not hard-code new hex colours that
  duplicate an existing token.
- **Charts:** build figures with Plotly Express and apply `CHART_LAYOUT` via
  `fig.update_layout(**CHART_LAYOUT)` so every chart keeps the same theme.
- **Database:** always use parameterised queries (`%s` placeholders). Never
  interpolate user input into SQL strings.
- **Errors:** wrap DB and SMTP calls in `try/except` — analytics must degrade
  gracefully, never crash a dashboard tab.

---

## Before you open a pull request

```bash
python -m py_compile project.py      # must pass
```

Then confirm:

- [ ] No secrets, credentials, or real customer data are committed.
- [ ] Screenshots added for any visual change.
- [ ] README / docs updated if setup or behaviour changed.
- [ ] You did **not** commit `.streamlit/secrets.toml`.

---

## Commit messages

Conventional, imperative, and scoped where it helps:

```
feat(shipments): add per-carrier delay breakdown
fix(auth): stop rendering an empty card above the login form
docs(readme): add architecture diagram
```

---

## Architecture, in one breath

```
Streamlit UI  ──▶  pandas transforms  ──▶  Plotly figures
      │                                          ▲
      ├──▶ MySQL (users, activity, messages) ────┤
      ├──▶ scikit-learn (forecast, anomalies) ───┤
      └──▶ SMTP / fpdf2 (emails, PDF reports) ───┘
```

Data enters as an Excel/CSV upload, a MySQL result set, or a Google Sheet, and is
normalised into three frames — `products`, `shipments`, `sales` — that every tab
consumes.
