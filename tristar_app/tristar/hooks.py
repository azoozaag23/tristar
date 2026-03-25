app_name = "tristar"
app_title = "TriStar Technical"
app_publisher = "TriStar Technical Company"
app_description = "Custom ERPNext module for TriStar Technical Co. — PCE Manufacturer, Dammam, Saudi Arabia"
app_email = "info@tristartech.com"
app_license = "MIT"
app_version = "1.0.0"

# -------------------------------------------------------------------------
# REQUIRED APPS
# -------------------------------------------------------------------------
required_apps = ["frappe", "erpnext"]

# -------------------------------------------------------------------------
# WEBSITE
# -------------------------------------------------------------------------
app_include_css = ["/assets/tristar/css/tristar.css"]
app_include_js = ["/assets/tristar/js/tristar.js"]

# -------------------------------------------------------------------------
# DESK (BACKEND) ASSETS
# -------------------------------------------------------------------------
app_include_css = ["/assets/tristar/css/tristar.css"]
app_include_js = ["/assets/tristar/js/tristar.js"]

# -------------------------------------------------------------------------
# DOCUMENT EVENTS
# -------------------------------------------------------------------------
doc_events = {
    "Production Order": {
        "on_submit": "tristar.tristar_manufacturing.doctype.production_batch.production_batch.create_batch_from_work_order",
    },
    "Sales Invoice": {
        "before_submit": "tristar.tristar_sales.utils.apply_vat_zatca",
        "on_submit": "tristar.tristar_sales.utils.generate_zatca_xml",
    },
    "Purchase Order": {
        "on_submit": "tristar.tristar_manufacturing.utils.notify_raw_material_arrival",
    },
    "Attendance": {
        "after_insert": "tristar.tristar_hr.utils.auto_calculate_overtime",
    },
}

# -------------------------------------------------------------------------
# SCHEDULED TASKS
# -------------------------------------------------------------------------
scheduler_events = {
    "daily": [
        "tristar.tristar_manufacturing.tasks.check_raw_material_reorder_levels",
        "tristar.tristar_manufacturing.tasks.flag_expiring_batches",
        "tristar.tristar_hr.tasks.send_attendance_reminders",
    ],
    "weekly": [
        "tristar.tristar_reports.tasks.send_weekly_production_report",
        "tristar.tristar_reports.tasks.send_weekly_sales_report",
    ],
    "monthly": [
        "tristar.tristar_hr.tasks.generate_monthly_payroll",
    ],
}

# -------------------------------------------------------------------------
# FIXTURES (exported configuration)
# -------------------------------------------------------------------------
fixtures = [
    {
        "doctype": "Custom Field",
        "filters": [["module", "=", "TriStar Manufacturing"]],
    },
    {
        "doctype": "Property Setter",
        "filters": [["module", "=", "TriStar Manufacturing"]],
    },
    {
        "doctype": "Role",
        "filters": [["name", "in", [
            "TriStar Production Manager",
            "TriStar Lab Technician",
            "TriStar Sales Executive",
            "TriStar Finance Manager",
            "TriStar HR Manager",
        ]]],
    },
    {
        "doctype": "Workflow",
        "filters": [["module", "=", "TriStar Manufacturing"]],
    },
]

# -------------------------------------------------------------------------
# OVERRIDE STANDARD DOCTYPE JS
# -------------------------------------------------------------------------
override_doctype_class = {
    "Item": "tristar.tristar_manufacturing.overrides.item.TriStarItem",
    "Customer": "tristar.tristar_sales.overrides.customer.TriStarCustomer",
}

# -------------------------------------------------------------------------
# JINJA TEMPLATE TAGS
# -------------------------------------------------------------------------
jinja = {
    "methods": [
        "tristar.tristar_manufacturing.utils.get_pce_grade_info",
        "tristar.tristar_sales.utils.get_customer_mix_designs",
    ],
}

# -------------------------------------------------------------------------
# TRANSLATIONS
# -------------------------------------------------------------------------
# Arabic is enabled at the user/system level in ERPNext settings
# Translation files are in tristar/translations/ar.csv
