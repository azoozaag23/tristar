"""
Sales Utilities — TriStar Technical Company
Handles ZATCA (Fatoora) e-invoicing for Saudi Arabia VAT compliance.
"""

import frappe
from frappe import _
from frappe.utils import flt
import json
import hashlib
import base64
from datetime import datetime


# ---------------------------------------------------------------------------
# ZATCA / VAT HELPERS
# ---------------------------------------------------------------------------

VAT_RATE = 0.15  # Saudi Arabia standard VAT rate


def apply_vat_zatca(doc, method=None):
    """
    Called before_submit on Sales Invoice.
    Ensures 15% VAT is applied to all taxable line items.
    """
    company_country = frappe.db.get_value("Company", doc.company, "country")
    if company_country != "Saudi Arabia":
        return

    vat_account = frappe.db.get_value(
        "Account",
        {"account_type": "Tax", "company": doc.company, "account_name": ["like", "%VAT%"]},
        "name",
    )

    if not vat_account:
        frappe.msgprint(
            _("No VAT account found. Please set up a VAT (15%) tax account."),
            indicator="orange",
        )
        return

    # Ensure tax row exists
    existing_vat = [t for t in doc.taxes if t.account_head == vat_account]
    if not existing_vat:
        doc.append(
            "taxes",
            {
                "charge_type": "On Net Total",
                "account_head": vat_account,
                "description": "VAT 15% (ضريبة القيمة المضافة)",
                "rate": VAT_RATE * 100,
            },
        )


def generate_zatca_xml(doc, method=None):
    """
    Called on_submit on Sales Invoice.
    Generates a simplified ZATCA Phase 1 XML invoice and attaches it.
    Full Phase 2 (cryptographic signing) requires the ZATCA SDK.
    """
    company_country = frappe.db.get_value("Company", doc.company, "country")
    if company_country != "Saudi Arabia":
        return

    xml_content = _build_ubl_xml(doc)
    file_name = f"ZATCA_{doc.name}.xml"

    # Save as attachment
    _file = frappe.get_doc(
        {
            "doctype": "File",
            "file_name": file_name,
            "attached_to_doctype": "Sales Invoice",
            "attached_to_name": doc.name,
            "content": xml_content,
            "is_private": 1,
        }
    )
    _file.flags.ignore_permissions = True
    _file.save()
    frappe.msgprint(
        _("ZATCA XML invoice {0} generated and attached.").format(file_name),
        indicator="green",
    )


def _build_ubl_xml(doc):
    """Build a UBL 2.1-compliant XML for ZATCA Phase 1."""
    issue_date = doc.posting_date.strftime("%Y-%m-%d") if doc.posting_date else ""
    issue_time = "00:00:00"
    grand_total = flt(doc.grand_total, 2)
    tax_amount = flt(doc.total_taxes_and_charges, 2)
    net_total = flt(doc.net_total, 2)

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
         xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
         xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
  <cbc:ProfileID>reporting:1.0</cbc:ProfileID>
  <cbc:ID>{doc.name}</cbc:ID>
  <cbc:UUID>{_generate_uuid(doc.name)}</cbc:UUID>
  <cbc:IssueDate>{issue_date}</cbc:IssueDate>
  <cbc:IssueTime>{issue_time}</cbc:IssueTime>
  <cbc:InvoiceTypeCode name="0200000">388</cbc:InvoiceTypeCode>
  <cbc:DocumentCurrencyCode>SAR</cbc:DocumentCurrencyCode>
  <cac:AccountingSupplierParty>
    <cac:Party>
      <cac:PartyName>
        <cbc:Name>TriStar Technical Company</cbc:Name>
      </cac:PartyName>
      <cac:PostalAddress>
        <cbc:CityName>Dammam</cbc:CityName>
        <cbc:CountrySubentity>Eastern Province</cbc:CountrySubentity>
        <cac:Country>
          <cbc:IdentificationCode>SA</cbc:IdentificationCode>
        </cac:Country>
      </cac:PostalAddress>
      <cac:PartyTaxScheme>
        <cbc:CompanyID>{frappe.db.get_value("Company", doc.company, "tax_id") or "XXXXXXXXXXXXXXX"}</cbc:CompanyID>
        <cac:TaxScheme>
          <cbc:ID>VAT</cbc:ID>
        </cac:TaxScheme>
      </cac:PartyTaxScheme>
    </cac:Party>
  </cac:AccountingSupplierParty>
  <cac:AccountingCustomerParty>
    <cac:Party>
      <cac:PartyName>
        <cbc:Name>{doc.customer}</cbc:Name>
      </cac:PartyName>
    </cac:Party>
  </cac:AccountingCustomerParty>
  <cac:TaxTotal>
    <cbc:TaxAmount currencyID="SAR">{tax_amount}</cbc:TaxAmount>
  </cac:TaxTotal>
  <cac:LegalMonetaryTotal>
    <cbc:LineExtensionAmount currencyID="SAR">{net_total}</cbc:LineExtensionAmount>
    <cbc:TaxExclusiveAmount currencyID="SAR">{net_total}</cbc:TaxExclusiveAmount>
    <cbc:TaxInclusiveAmount currencyID="SAR">{grand_total}</cbc:TaxInclusiveAmount>
    <cbc:PayableAmount currencyID="SAR">{grand_total}</cbc:PayableAmount>
  </cac:LegalMonetaryTotal>
</Invoice>"""
    return xml


def _generate_uuid(invoice_name):
    return hashlib.md5(invoice_name.encode()).hexdigest()


def get_customer_mix_designs(customer):
    """Jinja helper: return all mix design requests for a customer."""
    return frappe.get_all(
        "Customer Technical Request",
        filters={"customer": customer},
        fields=["name", "project_name", "recommended_pce_grade", "status"],
        order_by="request_date desc",
    )
