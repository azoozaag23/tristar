# TriStar Technical — Custom ERPNext App

**شركة تراي ستار التقنية | المدينة الصناعية الثانية، الدمام، المملكة العربية السعودية**

Custom [Frappe](https://frappeframework.com) / [ERPNext](https://erpnext.com) application for **TriStar Technical Company**, the leading manufacturer of Polycarboxylate Ether (PCE) superplasticizers in Saudi Arabia.

---

## 📦 What's Included

### Manufacturing Module (`TriStar Manufacturing`)
| Feature | Description |
|---|---|
| **PCE Grade** | Master record for each PCE product grade (SR50, HB50, VR50, CT50, etc.) with full technical specs |
| **Production Batch** | Tracks every production run — planned vs actual qty, yield %, reactor ID, shift, QC status |
| **Quality Control Test** | Lab test results (pH, viscosity, density, solid content) auto-validated against grade specs |
| **Raw Material Alerts** | Daily scheduler checks acrylic acid, methanol, HPEO, methacrylic acid stock vs reorder levels |
| **Expiring Batch Alerts** | Daily scanner flags batches expiring within 30 days |

### Sales Module (`TriStar Sales`)
| Feature | Description |
|---|---|
| **Customer Technical Request** | Manages PCE mix-design consultations — project details, recommended grade & dosage, trial mix results |
| **ZATCA / Fatoora** | Phase 1 UBL 2.1 XML e-invoice generation on Sales Invoice submission |
| **VAT (15%)** | Auto-applies Saudi 15% VAT on invoices |

### HR Module (`TriStar HR`)
| Feature | Description |
|---|---|
| **GOSI Calculation** | Saudi social insurance (10% employee / 12% employer) |
| **End of Service** | Saudi Labor Law EOS benefit calculation |
| **Overtime** | Auto-calculates and logs overtime pay (150%) from Attendance records |
| **Attendance Reminders** | Daily email reminders for employees without attendance |

### Reports (`TriStar Reports`)
| Report | Description |
|---|---|
| **PCE Production Summary** | Monthly volume, yield %, and QC pass rates per grade with bar chart |
| **Batch Quality Report** | Detailed per-batch QC test results with pass/fail columns |

### Other
- 🌐 **Arabic translations** — All labels, field names, and messages translated (`translations/ar.csv`)
- 🎨 **Custom CSS/JS** — Brand styling, RTL support, smart form helpers
- 🔧 **Auto-seed** — Installs all 4 real PCE grades, roles, warehouses, and item groups on `bench migrate`

---

## 🚀 Installation

### Prerequisites
- Frappe Framework v14 or v15
- ERPNext v14 or v15
- Python 3.10+
- Node.js 18+

### Steps

```bash
# 1. Go to your frappe-bench directory
cd ~/frappe-bench

# 2. Get the app
bench get-app /path/to/tristar_app
# OR if hosted on GitHub:
# bench get-app https://github.com/tristar-tech/tristar

# 3. Install on your site
bench --site your-site.local install-app tristar

# 4. Run migrations (seeds default data)
bench --site your-site.local migrate

# 5. Build assets
bench build --app tristar

# 6. Restart
bench restart
```

---

## ⚙️ Post-Install Configuration

1. **Set Company Name** → Go to `Setup → Company` and set name to "TriStar Technical Company", country to Saudi Arabia, currency to SAR.
2. **Enter VAT Registration Number** → `Company → Tax ID` (required for ZATCA XML).
3. **Enable Arabic Language** → `Setup → System Settings → Language → Arabic`.
4. **Assign Roles** to users:
   - `TriStar Production Manager`
   - `TriStar Lab Technician`
   - `TriStar Sales Executive`
   - `TriStar Finance Manager`
   - `TriStar HR Manager`
5. **Configure GOSI** → Enter employee GOSI numbers in Employee master.
6. **Set Reorder Levels** → In each raw material Item, set `Reorder Level` under the `Reorder Levels` table.

---

## 🗂️ App Structure

```
tristar_app/
├── setup.py
├── requirements.txt
├── MANIFEST.in
└── tristar/
    ├── hooks.py                        # App config & event hooks
    ├── modules.txt
    ├── patches.txt
    ├── config/
    │   └── desktop.py                  # Desk module icons
    ├── public/
    │   ├── css/tristar.css             # Brand styles + RTL
    │   └── js/tristar.js              # Client-side form scripts
    ├── translations/
    │   └── ar.csv                      # Arabic translations
    ├── setup/
    │   └── install.py                  # Seed: roles, grades, warehouses
    ├── tristar_manufacturing/
    │   ├── doctype/
    │   │   ├── pce_grade/              # PCE Grade DocType
    │   │   ├── production_batch/       # Production Batch DocType
    │   │   └── quality_control_test/   # QC Test DocType
    │   ├── tasks.py                    # Scheduled tasks
    │   └── utils.py                   # Shared helpers
    ├── tristar_sales/
    │   ├── doctype/
    │   │   └── customer_technical_request/
    │   └── utils.py                   # ZATCA XML + VAT
    ├── tristar_hr/
    │   ├── utils.py                   # GOSI, EOS, Overtime
    │   └── tasks.py
    └── tristar_reports/
        └── report/
            ├── pce_production_summary/
            └── batch_quality_report/
```

---

## 🔐 Roles & Permissions

| Role | Access |
|---|---|
| TriStar Production Manager | Full Manufacturing + Reports |
| TriStar Lab Technician | QC Tests + Production Batch (read) |
| TriStar Sales Executive | Customer Requests + Sales |
| TriStar Finance Manager | Accounting + Reports |
| TriStar HR Manager | HR + Payroll |

---

## 📋 PCE Grades Seeded on Install

| Code | Name | Type |
|---|---|---|
| SR50 | TriStar PCE SR50 | Slump Retainer |
| HB50 | TriStar PCE HB50 | Hybrid |
| VR50 | TriStar PCE VR50 | High-Range Water Reducer |
| CT50 | TriStar PCE CT50 | Clay-Tolerant |

---

## 📞 Support

TriStar Technical Company | info@tristartech.com | [tristartech.com](https://tristartech.com)

---

*Built with ❤️ for TriStar Technical Company — Dammam, Saudi Arabia*
