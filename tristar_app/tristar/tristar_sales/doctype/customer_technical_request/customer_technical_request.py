"""
Customer Technical Request DocType Controller
TriStar Technical Company — Dammam, Saudi Arabia

Manages technical consultations for concrete mix design — a key
value-added service TriStar offers alongside PCE product sales.
"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import today, add_days


class CustomerTechnicalRequest(Document):

    def validate(self):
        self._auto_recommend_pce_grade()

    def _auto_recommend_pce_grade(self):
        """Suggest the best PCE grade based on project parameters if not set."""
        if self.recommended_pce_grade:
            return

        # Simple rule-based recommendation
        if self.target_slump_mm and flt(self.target_slump_mm) >= 180:
            # High slump needed → High-Range Water Reducer
            grade = frappe.db.get_value(
                "PCE Grade",
                {"grade_type": "High-Range Water Reducer", "status": "Active"},
                "grade_code",
            )
        elif self.clay_in_aggregate:
            grade = frappe.db.get_value(
                "PCE Grade",
                {"grade_type": "Clay-Tolerant", "status": "Active"},
                "grade_code",
            )
        else:
            grade = frappe.db.get_value(
                "PCE Grade",
                {"grade_type": "Hybrid", "status": "Active"},
                "grade_code",
            )

        if grade:
            self.recommended_pce_grade = grade

    def after_insert(self):
        """Send notification to assigned sales engineer."""
        if self.assigned_to:
            frappe.sendmail(
                recipients=[self.assigned_to],
                subject=_("New Technical Request: {0}").format(self.name),
                message=_(
                    "A new customer technical request has been assigned to you.<br><br>"
                    "<b>Customer:</b> {0}<br>"
                    "<b>Project:</b> {1}<br>"
                    "<b>Priority:</b> {2}<br><br>"
                    "Please review and respond within 24 hours."
                ).format(
                    self.customer,
                    self.project_name or "N/A",
                    self.priority,
                ),
            )


def flt(val, precision=None):
    """Safe float conversion."""
    try:
        result = float(val or 0)
        if precision is not None:
            result = round(result, precision)
        return result
    except (TypeError, ValueError):
        return 0.0
