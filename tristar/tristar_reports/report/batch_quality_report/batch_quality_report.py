"""
Batch Quality Report
TriStar Technical Company — Dammam, Saudi Arabia

Shows QC test results per batch with pass/fail indicators.
"""

import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"fieldname": "test_name", "label": _("QC Test"), "fieldtype": "Link", "options": "Quality Control Test", "width": 150},
        {"fieldname": "production_batch", "label": _("Production Batch"), "fieldtype": "Link", "options": "Production Batch", "width": 160},
        {"fieldname": "pce_grade", "label": _("PCE Grade"), "fieldtype": "Link", "options": "PCE Grade", "width": 120},
        {"fieldname": "test_date", "label": _("Test Date"), "fieldtype": "Date", "width": 100},
        {"fieldname": "ph_result", "label": _("pH"), "fieldtype": "Float", "width": 70},
        {"fieldname": "ph_pass", "label": _("pH ✓"), "fieldtype": "Check", "width": 65},
        {"fieldname": "viscosity_result", "label": _("Viscosity (mPa·s)"), "fieldtype": "Float", "width": 130},
        {"fieldname": "viscosity_pass", "label": _("Visc ✓"), "fieldtype": "Check", "width": 70},
        {"fieldname": "density_result", "label": _("Density (g/cm³)"), "fieldtype": "Float", "width": 130},
        {"fieldname": "density_pass", "label": _("Dens ✓"), "fieldtype": "Check", "width": 70},
        {"fieldname": "solid_content_result", "label": _("Solid Content (%)"), "fieldtype": "Float", "width": 130},
        {"fieldname": "solid_content_pass", "label": _("SC ✓"), "fieldtype": "Check", "width": 60},
        {"fieldname": "overall_result", "label": _("Result"), "fieldtype": "Data", "width": 100},
    ]


def get_data(filters):
    conditions = "WHERE qc.docstatus = 1"
    if filters and filters.get("from_date"):
        conditions += f" AND qc.test_date >= '{filters['from_date']}'"
    if filters and filters.get("to_date"):
        conditions += f" AND qc.test_date <= '{filters['to_date']}'"
    if filters and filters.get("pce_grade"):
        conditions += f" AND qc.pce_grade = '{filters['pce_grade']}'"
    if filters and filters.get("overall_result"):
        conditions += f" AND qc.overall_result = '{filters['overall_result']}'"

    return frappe.db.sql(
        f"""
        SELECT
            qc.name          AS test_name,
            qc.production_batch,
            qc.pce_grade,
            qc.test_date,
            qc.ph_result,
            qc.ph_pass,
            qc.viscosity_result,
            qc.viscosity_pass,
            qc.density_result,
            qc.density_pass,
            qc.solid_content_result,
            qc.solid_content_pass,
            qc.overall_result
        FROM `tabQuality Control Test` qc
        {conditions}
        ORDER BY qc.test_date DESC
        """,
        as_dict=True,
    )
