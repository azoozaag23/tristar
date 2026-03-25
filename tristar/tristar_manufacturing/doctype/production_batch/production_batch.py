"""
Production Batch DocType Controller
TriStar Technical Company — Dammam, Saudi Arabia

Tracks every PCE production run from raw material consumption
through QC approval to finished-goods inventory posting.
"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, today, add_days


class ProductionBatch(Document):

    # ------------------------------------------------------------------
    # VALIDATION
    # ------------------------------------------------------------------
    def validate(self):
        self._calculate_yield()
        self._validate_quantities()
        self._set_expiry_date()

    def _calculate_yield(self):
        if self.planned_qty_mt and self.actual_qty_mt:
            self.batch_yield_pct = flt(
                (self.actual_qty_mt / self.planned_qty_mt) * 100, 2
            )

    def _validate_quantities(self):
        if flt(self.planned_qty_mt) <= 0:
            frappe.throw(_("Planned Quantity must be greater than zero."))
        if flt(self.actual_qty_mt) < 0:
            frappe.throw(_("Actual Quantity cannot be negative."))
        if flt(self.waste_qty_mt) < 0:
            frappe.throw(_("Waste Quantity cannot be negative."))

    def _set_expiry_date(self):
        """Default shelf life: 12 months from production date."""
        if not self.expiry_date and self.batch_date:
            self.expiry_date = add_days(self.batch_date, 365)

    # ------------------------------------------------------------------
    # SUBMIT
    # ------------------------------------------------------------------
    def on_submit(self):
        self._post_stock_entry()
        self._update_status("Approved")

    def _post_stock_entry(self):
        """Create a Stock Entry (Manufacture) in ERPNext for finished goods."""
        if not self.actual_qty_mt or not self.warehouse:
            return

        item_code = f"PCE-{self.pce_grade}"
        se = frappe.get_doc({
            "doctype": "Stock Entry",
            "stock_entry_type": "Manufacture",
            "posting_date": self.batch_date,
            "company": frappe.defaults.get_global_default("company"),
            "remarks": f"Production Batch: {self.name}",
            "items": [
                {
                    "item_code": item_code,
                    "qty": self.actual_qty_mt,
                    "uom": "MT",
                    "t_warehouse": self.warehouse,
                    "batch_no": self.lot_number or self.name,
                }
            ],
        })
        se.flags.ignore_permissions = True
        se.insert()
        se.submit()
        frappe.msgprint(
            _("Stock Entry {0} created for {1} MT of {2}.").format(
                se.name, self.actual_qty_mt, item_code
            ),
            indicator="green",
        )

    def _update_status(self, status):
        self.db_set("status", status)

    # ------------------------------------------------------------------
    # CANCEL
    # ------------------------------------------------------------------
    def on_cancel(self):
        self._update_status("Rejected")

    # ------------------------------------------------------------------
    # API ENDPOINTS
    # ------------------------------------------------------------------


@frappe.whitelist()
def get_batches_by_grade(pce_grade, from_date=None, to_date=None):
    """Return production batch list for a specific PCE Grade, optionally filtered by date."""
    filters = {"pce_grade": pce_grade, "docstatus": 1}
    if from_date:
        filters["batch_date"] = [">=", from_date]
    if to_date:
        filters["batch_date"] = ["<=", to_date]

    return frappe.get_all(
        "Production Batch",
        filters=filters,
        fields=[
            "name",
            "batch_date",
            "planned_qty_mt",
            "actual_qty_mt",
            "batch_yield_pct",
            "qc_status",
            "status",
        ],
        order_by="batch_date desc",
    )


@frappe.whitelist()
def get_monthly_production_summary():
    """Return monthly aggregated production data for the dashboard."""
    return frappe.db.sql(
        """
        SELECT
            DATE_FORMAT(batch_date, '%Y-%m') AS month,
            pce_grade,
            SUM(planned_qty_mt) AS total_planned,
            SUM(actual_qty_mt) AS total_actual,
            AVG(batch_yield_pct) AS avg_yield,
            COUNT(*) AS batch_count
        FROM `tabProduction Batch`
        WHERE docstatus = 1
        GROUP BY month, pce_grade
        ORDER BY month DESC
        LIMIT 24
        """,
        as_dict=True,
    )
