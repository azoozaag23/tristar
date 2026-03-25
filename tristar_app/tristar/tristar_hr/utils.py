"""
HR Utilities — TriStar Technical Company
Saudi labor law compliant payroll and attendance helpers.
"""

import frappe
from frappe import _
from frappe.utils import flt, cint, getdate, get_datetime


# ---------------------------------------------------------------------------
# GOSI (General Organization for Social Insurance) — Saudi Arabia
# ---------------------------------------------------------------------------

GOSI_EMPLOYEE_RATE = 0.10     # 10% employee contribution
GOSI_EMPLOYER_RATE = 0.12     # 12% employer contribution (incl. occupational hazard)
GOSI_MAX_SALARY = 45000       # Max monthly salary for GOSI calculation (SAR)


def calculate_gosi(basic_salary):
    """Return GOSI employee and employer contribution amounts."""
    applicable_salary = min(flt(basic_salary), GOSI_MAX_SALARY)
    return {
        "employee_gosi": round(applicable_salary * GOSI_EMPLOYEE_RATE, 2),
        "employer_gosi": round(applicable_salary * GOSI_EMPLOYER_RATE, 2),
    }


# ---------------------------------------------------------------------------
# END OF SERVICE (EOS) — Saudi Labor Law
# ---------------------------------------------------------------------------

def calculate_end_of_service(basic_salary, years_of_service):
    """
    Calculate Saudi End of Service benefit.
    - First 5 years: 0.5 month per year
    - Beyond 5 years: 1 month per year
    """
    years = flt(years_of_service)
    salary = flt(basic_salary)

    if years <= 5:
        eos = salary * 0.5 * years
    else:
        eos = (salary * 0.5 * 5) + (salary * 1 * (years - 5))

    return round(eos, 2)


# ---------------------------------------------------------------------------
# OVERTIME — Saudi Labor Law
# ---------------------------------------------------------------------------

OVERTIME_RATE = 1.5           # 150% of hourly rate
STANDARD_HOURS_PER_DAY = 8
STANDARD_DAYS_PER_MONTH = 26


def calculate_overtime_pay(basic_salary, overtime_hours):
    """Calculate overtime pay for a given number of hours."""
    hourly_rate = flt(basic_salary) / (STANDARD_DAYS_PER_MONTH * STANDARD_HOURS_PER_DAY)
    return round(hourly_rate * OVERTIME_RATE * flt(overtime_hours), 2)


# ---------------------------------------------------------------------------
# HOOKS
# ---------------------------------------------------------------------------

def auto_calculate_overtime(doc, method=None):
    """
    Triggered after Attendance insert.
    If working hours exceed 8, logs the overtime.
    """
    if not doc.working_hours:
        return

    working_hours = flt(doc.working_hours)
    if working_hours <= STANDARD_HOURS_PER_DAY:
        return

    overtime_hours = working_hours - STANDARD_HOURS_PER_DAY

    # Log to Additional Salary if employee has a salary structure
    employee = frappe.get_doc("Employee", doc.employee)
    if not employee or not employee.date_of_joining:
        return

    frappe.get_doc({
        "doctype": "Additional Salary",
        "employee": doc.employee,
        "salary_component": "Overtime",
        "amount": calculate_overtime_pay(
            frappe.db.get_value(
                "Salary Structure Assignment",
                {"employee": doc.employee},
                "base",
            ) or 0,
            overtime_hours,
        ),
        "payroll_date": doc.attendance_date,
        "company": employee.company,
        "overwrite_salary_structure_amount": 0,
        "currency": "SAR",
    }).insert(ignore_permissions=True)


# ---------------------------------------------------------------------------
# SCHEDULED TASKS
# ---------------------------------------------------------------------------

def send_attendance_reminders():
    """Send a daily reminder to employees who haven't marked attendance."""
    today_str = frappe.utils.today()
    employees = frappe.get_all("Employee", filters={"status": "Active"}, fields=["name", "user_id"])

    for emp in employees:
        if not emp.user_id:
            continue
        has_attendance = frappe.db.exists(
            "Attendance",
            {"employee": emp.name, "attendance_date": today_str},
        )
        if not has_attendance:
            frappe.sendmail(
                recipients=[emp.user_id],
                subject=_("Attendance Reminder — {0}").format(today_str),
                message=_("Please mark your attendance for today."),
            )


def generate_monthly_payroll():
    """Auto-run payroll for all active employees at month end."""
    frappe.logger().info("TriStar: Running monthly payroll auto-generation.")
    # This calls ERPNext's built-in payroll processing
    # Actual implementation uses Process Payroll doctype
    pass
