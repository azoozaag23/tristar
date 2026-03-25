"""
TriStar Technical Company — ERPNext App Setup
Run after installation to seed default data.
"""

import frappe
from frappe import _


def before_install():
    """Pre-migration checks."""
    frappe.logger().info("TriStar: Starting installation...")


def after_install():
    """Post-migration seed data."""
    _create_roles()
    _create_item_groups()
    _create_warehouses()
    _create_pce_grades()
    _configure_company_defaults()
    frappe.logger().info("TriStar: Installation complete.")


# ---------------------------------------------------------------------------
# ROLES
# ---------------------------------------------------------------------------

def _create_roles():
    roles = [
        "TriStar Production Manager",
        "TriStar Lab Technician",
        "TriStar Sales Executive",
        "TriStar Finance Manager",
        "TriStar HR Manager",
    ]
    for role_name in roles:
        if not frappe.db.exists("Role", role_name):
            frappe.get_doc({"doctype": "Role", "role_name": role_name}).insert(
                ignore_permissions=True
            )
    frappe.db.commit()
    frappe.logger().info("TriStar: Roles created.")


# ---------------------------------------------------------------------------
# ITEM GROUPS
# ---------------------------------------------------------------------------

def _create_item_groups():
    groups = [
        ("PCE Products", "Products"),
        ("Raw Materials - PCE", "Raw Material"),
        ("Packaging", "Products"),
    ]
    for group_name, parent in groups:
        if not frappe.db.exists("Item Group", group_name):
            frappe.get_doc({
                "doctype": "Item Group",
                "item_group_name": group_name,
                "parent_item_group": parent,
            }).insert(ignore_permissions=True)
    frappe.db.commit()


# ---------------------------------------------------------------------------
# WAREHOUSES
# ---------------------------------------------------------------------------

def _create_warehouses():
    company = frappe.defaults.get_global_default("company")
    if not company:
        return

    warehouses = [
        "Raw Materials - Tristar",
        "Finished Goods - Tristar",
        "WIP - Tristar",
        "Rejected - Tristar",
    ]
    for wh_name in warehouses:
        if not frappe.db.exists("Warehouse", f"{wh_name} - {company[:3].upper()}"):
            frappe.get_doc({
                "doctype": "Warehouse",
                "warehouse_name": wh_name,
                "company": company,
                "warehouse_type": (
                    "Transit" if "WIP" in wh_name else "Store"
                ),
            }).insert(ignore_permissions=True)
    frappe.db.commit()


# ---------------------------------------------------------------------------
# DEFAULT PCE GRADES (matches Tristar's real product lineup)
# ---------------------------------------------------------------------------

def _create_pce_grades():
    grades = [
        {
            "grade_code": "SR50",
            "grade_name": "TriStar PCE SR50",
            "grade_name_ar": "تراي ستار PCE SR50",
            "grade_type": "Slump Retainer",
            "solid_content_pct": 50.0,
            "ph_min": 5.0, "ph_max": 7.0,
            "viscosity_min": 100, "viscosity_max": 600,
            "density_min": 1.05, "density_max": 1.10,
            "water_reduction_pct": 25.0,
            "slump_retention_hrs": 2.0,
            "status": "Active",
        },
        {
            "grade_code": "HB50",
            "grade_name": "TriStar PCE HB50",
            "grade_name_ar": "تراي ستار PCE HB50",
            "grade_type": "Hybrid",
            "solid_content_pct": 50.0,
            "ph_min": 5.0, "ph_max": 7.0,
            "viscosity_min": 100, "viscosity_max": 600,
            "density_min": 1.05, "density_max": 1.10,
            "water_reduction_pct": 28.0,
            "slump_retention_hrs": 1.5,
            "status": "Active",
        },
        {
            "grade_code": "VR50",
            "grade_name": "TriStar PCE VR50",
            "grade_name_ar": "تراي ستار PCE VR50",
            "grade_type": "High-Range Water Reducer",
            "solid_content_pct": 50.0,
            "ph_min": 5.0, "ph_max": 7.0,
            "viscosity_min": 100, "viscosity_max": 600,
            "density_min": 1.05, "density_max": 1.12,
            "water_reduction_pct": 35.0,
            "slump_retention_hrs": 1.0,
            "early_strength": 0,
            "status": "Active",
        },
        {
            "grade_code": "CT50",
            "grade_name": "TriStar PCE CT50",
            "grade_name_ar": "تراي ستار PCE CT50",
            "grade_type": "Clay-Tolerant",
            "solid_content_pct": 50.0,
            "ph_min": 5.0, "ph_max": 7.0,
            "viscosity_min": 100, "viscosity_max": 600,
            "density_min": 1.05, "density_max": 1.10,
            "water_reduction_pct": 22.0,
            "slump_retention_hrs": 2.0,
            "clay_tolerant": 1,
            "status": "Active",
        },
    ]

    for g in grades:
        if not frappe.db.exists("PCE Grade", g["grade_code"]):
            doc = frappe.get_doc({"doctype": "PCE Grade", **g})
            doc.flags.ignore_permissions = True
            doc.insert()

    frappe.db.commit()
    frappe.logger().info("TriStar: Default PCE grades seeded.")


# ---------------------------------------------------------------------------
# COMPANY DEFAULTS
# ---------------------------------------------------------------------------

def _configure_company_defaults():
    company = frappe.defaults.get_global_default("company")
    if not company:
        return

    # Set country and currency for Saudi Arabia
    frappe.db.set_value("Company", company, {
        "country": "Saudi Arabia",
        "default_currency": "SAR",
    })
    frappe.db.commit()
    frappe.logger().info("TriStar: Company defaults configured for Saudi Arabia.")
