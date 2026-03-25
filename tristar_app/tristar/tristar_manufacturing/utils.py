"""
Manufacturing Utilities — TriStar Technical Company
"""

import frappe
from frappe import _


def create_batch_from_work_order(doc, method=None):
    """
    Hook: Called when a Production Order is submitted.
    Auto-creates a Production Batch draft.
    """
    if not frappe.db.exists("DocType", "Production Batch"):
        return

    batch = frappe.get_doc({
        "doctype": "Production Batch",
        "pce_grade": doc.item_code.replace("PCE-", "") if doc.item_code.startswith("PCE-") else doc.item_code,
        "batch_date": doc.planned_start_date,
        "planned_qty_mt": doc.qty,
        "status": "In Production",
        "remarks": f"Auto-created from Production Order {doc.name}",
    })
    batch.flags.ignore_permissions = True
    batch.insert()
    frappe.msgprint(
        _("Production Batch {0} created from Work Order {1}").format(batch.name, doc.name),
        indicator="green",
    )


def get_pce_grade_info(grade_code):
    """Jinja helper: return grade info dict for print templates."""
    if not frappe.db.exists("PCE Grade", grade_code):
        return {}
    return frappe.get_doc("PCE Grade", grade_code).as_dict()
