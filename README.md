
<div align="center">

# 📦 Traqify — Supply Chain AI

**AI-powered supply chain intelligence built with Streamlit, MySQL & scikit-learn**

🚀 **Live Demo:** [traqify.streamlit.app](https://traqify.streamlit.app)

> If the app is in sleep mode, click **"Yes, get this app back up!"** to wake it.

</div>

---

## ✨ Overview

Traqify is a comprehensive supply chain analytics platform that turns raw operational data into actionable insights. It combines interactive KPI dashboards, AI-driven forecasting, anomaly detection, and intelligent reorder recommendations into a single, polished web application.

Built as an **Informatics Practices** project, Traqify demonstrates a full-stack approach: a Python/Streamlit frontend, a MySQL relational backend, machine-learning–assisted analytics, and automated email reporting.

---

## 🧩 Features

### 📊 Analytics & Reporting
- Real-time KPI dashboard — revenue, delayed shipments, low-stock items, product counts
- Monthly revenue trends with interactive Plotly visualizations
- Demand forecasting for the next N months using linear regression (`scikit-learn`)
- Multi-currency revenue conversion
- Product profitability scoring
- Seasonal revenue trend analysis
- Supplier cost comparison
- Dead stock identification

### 🤖 AI-Powered Insights
- Revenue anomaly detection
- Supplier delay anomaly detection
- Smart reorder recommendations based on stock levels and historical sales

### 📦 Inventory & Shipments
- Inventory status with reorder-level alerts
- Shipment tracker with delay badges and status updates
- Supplier scorecards and global supplier map

### 🔐 Accounts & Permissions
- Secure sign-up / login with **OTP email verification**
- Distinct user and admin dashboards
- Admin user management, password resets, and account removal
- Broadcast announcements and user conversation log
- Full activity timeline audit log

### 📧 Communications
- Automated low-stock email alerts
- Shipment-delay email alerts
- On-demand dashboard summary reports via email
- Downloadable **PDF reports** (via `fpdf2`)

### 🗄️ Data Sources
- Excel (`.xlsx`) upload
- CSV upload
- MySQL database connection with an in-app SQL console
- Google Sheets integration

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- MySQL (local or remote) — see [`project(mysql part)`](project(mysql%20part)) for the schema
- (Optional) a Google Cloud service account for Google Sheets loading

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/sus6756/AI-supplychain.git
cd AI-supplychain

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run project.py
```

The application will be available at `http://localhost:8501`.

### First-Time Use
1. Create a new account — a **one-time OTP** is emailed to you to verify your sign-up.
2. Log in, then connect your data (Excel / CSV / MySQL / Google Sheets).

### Database Setup

1. Start your MySQL server (e.g., via XAMPP or Docker).
2. Execute the schema and seed queries in [`project(mysql part)`](project(mysql%20part)).
3. Enter your connection details in the app's **MySQL Console** tab.

> ✅ Running in a Dev Container / Codespace? The included [`.devcontainer`](.devcontainer) handles package installation and auto-starts the app on port `8501`.

---

## 🗂️ Project Structure

```
AI-supplychain/
├── project.py                  # Main Streamlit application (Traqify v3.1)
├── requirements.txt            # Python dependencies
├── packages.txt                # System packages (devcontainer)
├── project                     # Minimal workbook/reference dashboard script
├── project(mysql part)         # MySQL schema + sample analytics queries
└── .devcontainer/              # Codespace / Dev Container configuration
```

---

## 🛠️ Tech Stack

| Layer       | Technology                                               |
|-------------|----------------------------------------------------------|
| Frontend    | [Streamlit](https://streamlit.io) · Plotly · custom CSS/JS |
| Backend     | Python 3 · MySQL (via `mysql-connector-python`)          |
| ML / AI     | scikit-learn (regression & anomaly detection)            |
| Reporting   | fpdf2 (PDF) · SMTP (email) · openpyxl (Excel)            |

---

## 👤 Author

**R Sashank Adithiyaa** — [@sus6756](https://github.com/sus6756)

---

## 📄 License

This project is provided under a **restrictive custom license** — all rights reserved. You may view and use the source code for personal reference, but you may **not** copy, modify, distribute, or republish it, in whole or in part, without explicit written permission from the author. See the [LICENSE](LICENSE) file for the full terms.
