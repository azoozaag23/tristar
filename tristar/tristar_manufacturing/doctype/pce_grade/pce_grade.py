"""
PCE Grade DocType Controller
TriStar Technical Company — Dammam, Saudi Arabia
Manages all Polycarboxylate Ether (PCE) product grades.
"""

import frappe
from frappe import _
from frappe.model.document import Document


class PCEGrade(Document):

    def validate(self):
        self._validate_ph_range()
        self._validate_viscosity_range()
        self._validate_density_range()
        self._set_item_defaults()

    def _validate_ph_range(self):
        if self.ph_min and self.ph_max:
            if self.ph_min >= self.ph_max:
                frappe.throw(_("pH Min must be less than pH Max"))
            if not (0 <= self.ph_min <= 14) or not (0 <= self.ph_max <= 14):
                frappe.throw(_("pH values must be between 0 and 14"))

    def _validate_viscosity_range(self):
        if self.viscosity_min and self.viscosity_max:
            if self.viscosity_min >= self.viscosity_max:
                frappe.throw(_("Viscosity Min must be less than Viscosity Max"))

    def _validate_density_range(self):
        if self.density_min and self.density_max:
            if self.density_min >= self.density_max:
                frappe.throw(_("Density Min must be less than Density Max"))

    def _set_item_defaults(self):
        """Auto-link to ERPNext Item master if it exists."""
        item_code = f"PCE-{self.grade_code}"
        if not frappe.db.exists("Item", item_code):
            return
        self.linked_item = item_code

    def after_insert(self):
        """Create corresponding ERPNext Item when a new PCE Grade is added."""
        self._create_erpnext_item()

    def _create_erpnext_item(self):
        item_code = f"PCE-{self.grade_code}"
        if frappe.db.exists("Item", item_code):
            return
        item = frappe.get_doc({
            "doctype": "Item",
            "item_code": item_code,
            "item_name": self.grade_name,
            "item_name_ar": self.grade_name_ar or self.grade_name,
            "item_group": "PCE Products",
            "stock_uom": "MT",
            "is_stock_item": 1,
            "is_purchase_item": 0,
            "is_sales_item": 1,
            "description": f"Polycarboxylate Ether — {self.grade_type}",
            "custom_pce_grade": self.grade_code,
        })
        item.flags.ignore_permissions = True
        item.insert()
        frappe.msgprint(
            _("ERPNext Item {0} created automatically.").format(item_code),
            indicator="green",
        )


@frappe.whitelist()
def get_grade_spec_summary(grade_code):
    """Return a summary dict of grade specs for use in Sales / QC forms."""
    grade = frappe.get_doc("PCE Grade", grade_code)
    return {
        "grade_name": grade.grade_name,
        "grade_type": grade.grade_type,
        "solid_content_pct": grade.solid_content_pct,
        "ph_range": f"{grade.ph_min}–{grade.ph_max}",
        "viscosity_range": f"{grade.viscosity_min}–{grade.viscosity_max} mPa·s",
        "density_range": f"{grade.density_min}–{grade.density_max} g/cm³",
        "water_reduction_pct": grade.water_reduction_pct,
        "slump_retention_hrs": grade.slump_retention_hrs,
    }
