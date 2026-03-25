"""
Scheduled Manufacturing Tasks — TriStar Technical Company
"""

import frappe
from frappe import _
from frappe.utils import today, add_days, flt


def check_raw_material_reorder_levels():
    """
    Daily task: Check if any raw material stock has fallen below
    the reorder level. If so, create a Purchase Order draft.
    """
    raw_materials = [
        "Acrylic Acid",
        "Methanol",
        "HPEO",
        "Methacrylic Acid",
    ]

    for material in raw_materials:
        item = frappe.db.get_value("Item", {"item_name": material}, ["name", "reorder_levels"], as_dict=True)
        if not item:
            continue

        # Check current stock
        current_stock = frappe.db.sql(
            """
            SELECT SUM(actual_qty) as qty
            FROM `tabBin`
            WHERE item_code = %s
            """,
            item.name,
            as_dict=True,
        )

        qty = flt((current_stock[0] or {}).get("qty", 0))

        reorder_qty = frappe.db.get_value(
            "Item Reorder",
            {"parent": item.name},
            "warehouse_reorder_qty",
        ) or 0

        if qty <= flt(reorder_qty):
            frappe.logger().warning(
                f"TriStar: {material} stock ({qty} MT) is at or below reorder level ({reorder_qty} MT)."
            )
            # Notify production manager
            _notify_low_stock(material, qty, reorder_qty)


def _notify_low_stock(material, current_qty, reorder_qty):
    managers = frappe.get_all(
        "Has Role",
        filters={"role": "TriStar Production Manager"},
        fields=["parent"],
    )
    recipients = [m.parent for m in managers if m.parent]
    if not recipients:
        return

    frappe.sendmail(
        recipients=recipients,
        subject=_("⚠️ Low Stock Alert: {0}").format(material),
        message=_(
            "<b>Raw Material:</b> {0}<br>"
            "<b>Current Stock:</b> {1} MT<br>"
            "<b>Reorder Level:</b> {2} MT<br><br>"
            "Please raise a Purchase Order immediately."
        ).format(material, current_qty, reorder_qty),
    )


def flag_expiring_batches():
    """
    Daily task: Flag production batches expiring within 30 days.
    Sends alert to production manager.
    """
    threshold_date = add_days(today(), 30)
    expiring = frappe.get_all(
        "Production Batch",
        filters={
            "docstatus": 1,
            "status": ["in", ["Approved", "Shipped"]],
            "expiry_date": ["<=", threshold_date],
        },
        fields=["name", "pce_grade", "expiry_date", "actual_qty_mt"],
    )

    if not expiring:
        return

    rows = "".join(
        f"<tr><td>{b.name}</td><td>{b.pce_grade}</td><td>{b.expiry_date}</td><td>{b.actual_qty_mt} MT</td></tr>"
        for b in expiring
    )
    table = f"""
    <table border='1' cellpadding='5' cellspacing='0'>
      <tr><th>Batch</th><th>PCE Grade</th><th>Expiry Date</th><th>Qty</th></tr>
      {rows}
    </table>
    """

    managers = frappe.get_all("Has Role", filters={"role": "TriStar Production Manager"}, fields=["parent"])
    recipients = [m.parent for m in managers]
    if not recipients:
        return

    frappe.sendmail(
        recipients=recipients,
        subject=_("⚠️ Batches Expiring Within 30 Days"),
        message=_("The following batches are expiring soon:<br><br>") + table,
    )


def notify_raw_material_arrival(doc, method=None):
    """Hook: Called when a Purchase Order is submitted."""
    managers = frappe.get_all("Has Role", filters={"role": "TriStar Production Manager"}, fields=["parent"])
    recipients = [m.parent for m in managers]
    if not recipients:
        return

    items_html = "".join(
        f"<li>{item.item_name or item.item_code} — {item.qty} {item.uom}</li>"
        for item in doc.items
    )
    frappe.sendmail(
        recipients=recipients,
        subject=_("Purchase Order {0} submitted — Raw Materials incoming").format(doc.name),
        message=_(
            "A new Purchase Order has been submitted:<br><br>"
            "<b>Supplier:</b> {0}<br>"
            "<b>Expected Delivery:</b> {1}<br><br>"
            "<b>Items:</b><ul>{2}</ul>"
        ).format(doc.supplier, doc.schedule_date or "TBD", items_html),
    )
