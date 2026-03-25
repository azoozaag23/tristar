"""
Quality Control Test DocType Controller
TriStar Technical Company — Dammam, Saudi Arabia

Validates measured values against the PCE Grade specification limits
and auto-determines pass/fail for each parameter.
"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class QualityControlTest(Document):

    def validate(self):
        self._load_grade_specs()
        self._evaluate_parameters()
        self._set_overall_result()

    def _load_grade_specs(self):
        if not self.pce_grade:
            return
        self._grade = frappe.get_doc("PCE Grade", self.pce_grade)

    def _evaluate_parameters(self):
        g = getattr(self, "_grade", None)
        if not g:
            return

        # pH
        if self.ph_result is not None:
            self.ph_pass = int(
                flt(g.ph_min) <= flt(self.ph_result) <= flt(g.ph_max)
            )

        # Viscosity
        if self.viscosity_result is not None:
            self.viscosity_pass = int(
                flt(g.viscosity_min) <= flt(self.viscosity_result) <= flt(g.viscosity_max)
            )

        # Density
        if self.density_result is not None:
            self.density_pass = int(
                flt(g.density_min) <= flt(self.density_result) <= flt(g.density_max)
            )

        # Solid Content — allow ±2% tolerance
        if self.solid_content_result is not None:
            target = flt(g.solid_content_pct)
            self.solid_content_pass = int(
                abs(flt(self.solid_content_result) - target) <= 2.0
            )

    def _set_overall_result(self):
        results = [
            self.ph_pass,
            self.viscosity_pass,
            self.density_pass,
            self.solid_content_pass,
        ]
        # Only evaluate if at least one test was entered
        entered = [r for r in results if r is not None]
        if not entered:
            return

        all_pass = all(r == 1 for r in entered)
        self.overall_result = "Pass" if all_pass else "Fail"

    def on_submit(self):
        """Update the parent Production Batch with QC result."""
        batch = frappe.get_doc("Production Batch", self.production_batch)
        batch.qc_status = self.overall_result
        batch.qc_reference = self.name
        batch.save(ignore_permissions=True)

        if self.overall_result == "Pass":
            batch.db_set("status", "Approved")
        elif self.overall_result == "Fail":
            batch.db_set("status", "QC Hold")

        frappe.msgprint(
            _("Production Batch {0} updated with QC result: {1}").format(
                self.production_batch, self.overall_result
            ),
            indicator="green" if self.overall_result == "Pass" else "red",
        )
