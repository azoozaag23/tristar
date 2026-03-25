"""
PCE Production Summary Report
TriStar Technical Company — Dammam, Saudi Arabia

Shows monthly production volumes, yields, and QC pass rates
per PCE grade. Used by management for KPI tracking.
"""

import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)
    summary = get_summary(data)
    return columns, data, None, chart, summary


def get_columns():
    return [
        {
            "fieldname": "month",
            "label": _("Month"),
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "fieldname": "pce_grade",
            "label": _("PCE Grade"),
            "fieldtype": "Link",
            "options": "PCE Grade",
            "width": 130,
        },
        {
            "fieldname": "batch_count",
            "label": _("Batches"),
            "fieldtype": "Int",
            "width": 80,
        },
        {
            "fieldname": "total_planned",
            "label": _("Planned (MT)"),
            "fieldtype": "Float",
            "width": 120,
        },
        {
            "fieldname": "total_actual",
            "label": _("Actual (MT)"),
            "fieldtype": "Float",
            "width": 120,
        },
        {
            "fieldname": "avg_yield",
            "label": _("Avg Yield (%)"),
            "fieldtype": "Float",
            "width": 120,
        },
        {
            "fieldname": "qc_pass_count",
            "label": _("QC Pass"),
            "fieldtype": "Int",
            "width": 90,
        },
        {
            "fieldname": "qc_pass_rate",
            "label": _("QC Pass Rate (%)"),
            "fieldtype": "Float",
            "width": 130,
        },
    ]


def get_data(filters):
    conditions = "WHERE pb.docstatus = 1"
    if filters and filters.get("from_date"):
        conditions += f" AND pb.batch_date >= '{filters['from_date']}'"
    if filters and filters.get("to_date"):
        conditions += f" AND pb.batch_date <= '{filters['to_date']}'"
    if filters and filters.get("pce_grade"):
        conditions += f" AND pb.pce_grade = '{filters['pce_grade']}'"

    data = frappe.db.sql(
        f"""
        SELECT
            DATE_FORMAT(pb.batch_date, '%Y-%m')   AS month,
            pb.pce_grade,
            COUNT(pb.name)                         AS batch_count,
            SUM(pb.planned_qty_mt)                 AS total_planned,
            SUM(pb.actual_qty_mt)                  AS total_actual,
            AVG(pb.batch_yield_pct)                AS avg_yield,
            SUM(CASE WHEN pb.qc_status = 'Pass' THEN 1 ELSE 0 END) AS qc_pass_count
        FROM `tabProduction Batch` pb
        {conditions}
        GROUP BY month, pb.pce_grade
        ORDER BY month DESC, pb.pce_grade
        """,
        as_dict=True,
    )

    for row in data:
        row["avg_yield"] = flt(row["avg_yield"], 2)
        row["qc_pass_rate"] = (
            flt(row["qc_pass_count"] / row["batch_count"] * 100, 1)
            if row["batch_count"]
            else 0
        )

    return data


def get_chart(data):
    if not data:
        return None

    labels = list({row["month"] for row in data})
    labels.sort()
    grades = list({row["pce_grade"] for row in data})

    datasets = []
    for grade in grades:
        grade_data = {row["month"]: row["total_actual"] for row in data if row["pce_grade"] == grade}
        datasets.append({
            "name": grade,
            "values": [flt(grade_data.get(m, 0), 2) for m in labels],
        })

    return {
        "data": {"labels": labels, "datasets": datasets},
        "type": "bar",
        "colors": ["#1a6fbf", "#2ecc71", "#e67e22", "#e74c3c"],
        "title": "Monthly Production Volume by PCE Grade (MT)",
    }


def get_summary(data):
    if not data:
        return []
    total_actual = sum(flt(r["total_actual"]) for r in data)
    avg_yield = sum(flt(r["avg_yield"]) for r in data) / len(data) if data else 0
    total_batches = sum(cint(r["batch_count"]) for r in data)

    return [
        {"label": _("Total Production (MT)"), "value": round(total_actual, 2), "indicator": "green"},
        {"label": _("Average Yield (%)"), "value": round(avg_yield, 1), "indicator": "blue"},
        {"label": _("Total Batches"), "value": total_batches, "indicator": "blue"},
    ]


def cint(val):
    try:
        return int(val or 0)
    except (TypeError, ValueError):
        return 0
