/**
 * TriStar Technical Company — Custom ERPNext Client Scripts
 * Dammam, Saudi Arabia
 */

// -----------------------------------------------------------------------
// Production Batch — client-side helpers
// -----------------------------------------------------------------------
frappe.ui.form.on("Production Batch", {

    refresh(frm) {
        // Colour-code the yield field
        if (frm.doc.batch_yield_pct !== undefined) {
            const cls = frm.doc.batch_yield_pct >= 95
                ? "batch-yield-high"
                : "batch-yield-low";
            frm.fields_dict.batch_yield_pct.$wrapper
                .find(".control-value")
                .addClass(cls);
        }

        // Quick QC Test creation button
        if (frm.doc.docstatus === 1 && !frm.doc.qc_reference) {
            frm.add_custom_button(__("Create QC Test"), () => {
                frappe.new_doc("Quality Control Test", {
                    production_batch: frm.doc.name,
                    pce_grade: frm.doc.pce_grade,
                    test_date: frappe.datetime.get_today(),
                });
            }, __("Actions"));
        }
    },

    actual_qty_mt(frm) {
        if (frm.doc.planned_qty_mt && frm.doc.actual_qty_mt) {
            frm.set_value(
                "batch_yield_pct",
                ((frm.doc.actual_qty_mt / frm.doc.planned_qty_mt) * 100).toFixed(2)
            );
        }
    },
});

// -----------------------------------------------------------------------
// Quality Control Test — auto-evaluate pass/fail on blur
// -----------------------------------------------------------------------
frappe.ui.form.on("Quality Control Test", {

    pce_grade(frm) {
        if (!frm.doc.pce_grade) return;
        frappe.call({
            method: "tristar.tristar_manufacturing.doctype.pce_grade.pce_grade.get_grade_spec_summary",
            args: { grade_code: frm.doc.pce_grade },
            callback(r) {
                if (r.message) {
                    frm.dashboard.add_comment(
                        `<b>${r.message.grade_name}</b> — ${r.message.grade_type}<br>
                         pH: ${r.message.ph_range} | Viscosity: ${r.message.viscosity_range}`,
                        "blue", true
                    );
                }
            },
        });
    },
});

// -----------------------------------------------------------------------
// Customer Technical Request — fetch PCE grade spec on selection
// -----------------------------------------------------------------------
frappe.ui.form.on("Customer Technical Request", {

    recommended_pce_grade(frm) {
        if (!frm.doc.recommended_pce_grade) return;
        frappe.call({
            method: "tristar.tristar_manufacturing.doctype.pce_grade.pce_grade.get_grade_spec_summary",
            args: { grade_code: frm.doc.recommended_pce_grade },
            callback(r) {
                if (r.message) {
                    frm.set_value("expected_water_reduction", r.message.water_reduction_pct);
                    frm.set_value("expected_slump_retention", r.message.slump_retention_hrs);
                }
            },
        });
    },
});

// -----------------------------------------------------------------------
// Sales Invoice — ZATCA info banner for Saudi company
// -----------------------------------------------------------------------
frappe.ui.form.on("Sales Invoice", {
    refresh(frm) {
        if (frm.doc.company) {
            frappe.db.get_value("Company", frm.doc.company, "country", (r) => {
                if (r && r.country === "Saudi Arabia" && frm.doc.docstatus === 1) {
                    frm.dashboard.add_comment(
                        "✅ ZATCA XML invoice will be generated on submission.",
                        "green", false
                    );
                }
            });
        }
    },
});
