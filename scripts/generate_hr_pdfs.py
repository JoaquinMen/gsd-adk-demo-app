"""Generate mock HR policy PDF documents for GSD (US & Argentina)."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

from fpdf import FPDF

DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "hr_pdfs"

EXPECTED_PDF_FILENAMES: Tuple[str, ...] = (
    "gsd_holidays_us_argentina.pdf",
    "gsd_benefits_usa.pdf",
    "gsd_benefits_argentina.pdf",
)


class GSDPolicyPDF(FPDF):
    """Styled PDF builder for GSD internal HR policy documents."""

    def __init__(self, doc_title: str, doc_code: str) -> None:
        super().__init__()
        self.doc_title = doc_title
        self.doc_code = doc_code
        self.set_auto_page_break(auto=True, margin=18)

    def header(self) -> None:
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(80, 80, 80)
        self.cell(0, 6, f"GSD Consulting Tech Firm | Official HR Policy ({self.doc_code})", new_x="LMARGIN", new_y="NEXT")
        self.line(10, self.get_y() + 1, 200, self.get_y() + 1)
        self.ln(4)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(110, 110, 110)
        self.cell(0, 10, f"GSD Internal Confidential - {self.doc_title} - Page {self.page_no()}", align="C")


def _render_policy_pdf(
    output_path: Path,
    doc_title: str,
    doc_code: str,
    sections: List[Tuple[str, List[str]]],
) -> Path:
    """Render a multi-section HR policy document to a PDF file."""
    pdf = GSDPolicyPDF(doc_title=doc_title, doc_code=doc_code)
    pdf.add_page()

    # Main document title
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(20, 40, 80)
    pdf.multi_cell(0, 9, doc_title, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    for heading, paragraphs in sections:
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(30, 60, 110)
        pdf.multi_cell(0, 8, heading, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)

        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(20, 20, 20)
        for paragraph in paragraphs:
            pdf.multi_cell(0, 6, paragraph, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)
        pdf.ln(2)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(output_path))
    return output_path


def _holidays_sections() -> List[Tuple[str, List[str]]]:
    return [
        (
            "1. Overview & Holiday Time-Tracking Policy at GSD",
            [
                "Company Name: GSD (Global Software Delivery), a technology and AI consulting firm operating in the United States (US) and Argentina.",
                "All full-time GSD consultants and staff observe the official public holidays of their country of residence (US or Argentina). Consultants are not expected to work or log client billable hours on official country holidays unless pre-authorized in writing by an Engagement Director.",
                "If a client emergency requires work on an official GSD holiday, logged hours are billed at 1.5x the standard client rate and the consultant receives one (1) compensatory floating PTO day.",
            ],
        ),
        (
            "2. GSD United States (US) Official 2026 Holiday Calendar (11 Paid Holidays)",
            [
                "- Thursday, January 1, 2026: New Year's Day",
                "- Monday, January 19, 2026: Martin Luther King Jr. Day",
                "- Monday, February 16, 2026: Presidents' Day",
                "- Monday, May 25, 2026: Memorial Day",
                "- Friday, June 19, 2026: Juneteenth National Independence Day",
                "- Friday, July 3, 2026: Independence Day (Observed for July 4)",
                "- Monday, September 7, 2026: Labor Day",
                "- Monday, October 12, 2026: Indigenous Peoples' Day / Fall Recharge Day",
                "- Thursday, November 26, 2026: Thanksgiving Day",
                "- Friday, November 27, 2026: Day After Thanksgiving (GSD US Holiday)",
                "- Friday, December 25, 2026: Christmas Day",
                "Note: US consultants also receive two (2) Floating Cultural Holidays per calendar year.",
            ],
        ),
        (
            "3. GSD Argentina Official 2026 Holiday Calendar (Feriados Nacionales & Puentes)",
            [
                "- Thursday, January 1, 2026: Ano Nuevo (New Year's Day)",
                "- Monday, February 16 & Tuesday, February 17, 2026: Carnaval (2 days)",
                "- Monday, March 23, 2026: Feriado con Fines Turisticos (Bridge Holiday)",
                "- Tuesday, March 24, 2026: Dia Nacional de la Memoria por la Verdad y la Justicia",
                "- Thursday, April 2, 2026: Dia del Veterano y de los Caidos en la Guerra de Malvinas",
                "- Friday, April 3, 2026: Viernes Santo (Good Friday)",
                "- Friday, May 1, 2026: Dia del Trabajador (Labor Day)",
                "- Monday, May 25, 2026: Dia de la Revolucion de Mayo",
                "- Monday, June 15, 2026: Paso a la Inmortalidad del Gral. Martin Miguel de Guemes (Observed)",
                "- Saturday, June 20, 2026: Paso a la Inmortalidad del Gral. Manuel Belgrano",
                "- Thursday, July 9, 2026: Dia de la Independencia (Independence Day)",
                "- Friday, July 10, 2026: Feriado con Fines Turisticos (Independence Bridge Holiday)",
                "- Monday, August 17, 2026: Paso a la Inmortalidad del Gral. Jose de San Martin",
                "- Monday, October 12, 2026: Dia del Respeto a la Diversidad Cultural",
                "- Monday, November 23, 2026: Dia de la Soberania Nacional (Observed)",
                "- Monday, December 7, 2026: Feriado con Fines Turisticos (Bridge Holiday)",
                "- Tuesday, December 8, 2026: Inmaculada Concepcion de Maria",
                "- Friday, December 25, 2026: Navidad (Christmas Day)",
            ],
        ),
        (
            "4. Mandatory Onboarding & Holiday Policy Company Videos",
            [
                "All GSD employees can access internal video training on the GSD Learning Portal:",
                "- Video VID-HR-101: 'Welcome to GSD: Cross-Border Collaboration Between US and Argentina Teams' (Duration: 14 mins, Speaker: CEO Sofia Martinez).",
                "- Video VID-HR-102: 'How to Log Time, Holidays, and PTO in GSD Billing Systems' (Duration: 9 mins, Speaker: Operations Lead Lucas Benitez).",
                "- Video VID-HR-103: 'Security & Workplace Conduct for Client Engagements' (Duration: 22 mins, Mandatory within 14 days of hire).",
            ],
        ),
    ]


def _us_benefits_sections() -> List[Tuple[str, List[str]]]:
    return [
        (
            "1. GSD United States (US) Employee Benefits Overview",
            [
                "This document defines the official employee benefits, leave policies, health coverage, and workplace guidelines for full-time United States (US) employees of GSD (Global Software Delivery).",
                "Eligibility: All regular full-time US employees working 30+ hours per week are eligible for benefits starting on the first day of employment (no waiting period).",
            ],
        ),
        (
            "2. Paternal & Parental Leave Policy (United States)",
            [
                "Paternal & Parental Leave Entitlement: GSD provides twelve (12) weeks (60 business days) of 100% fully paid Parental Leave to all eligible US employees - regardless of gender, including fathers (paternal leave), mothers, adoptive parents, and foster parents.",
                "Eligibility Requirement: Employees must have completed at least six (6) months of continuous employment with GSD to qualify for full paid parental leave.",
                "Flexible Scheduling: Paid paternal/parental leave may be taken continuously or broken into two blocks within the first twelve (12) months following the birth, adoption, or foster placement of a child.",
                "Ramp-Back Program: Returning US parents may work a reduced 80% schedule (32 hours/week) at 100% pay for their first four (4) weeks back on active duty.",
            ],
        ),
        (
            "3. Vacation, Paid Time Off (PTO), and Sick Leave (United States)",
            [
                "Annual Vacation / PTO: US employees receive twenty (20) business days (4 weeks) of Paid Time Off (PTO) per calendar year for their first 3 years of tenure, increasing to twenty-five (25) business days starting in year 4.",
                "Rollover Cap: Up to five (5) unused PTO days may be carried over into the next calendar year.",
                "Sick & Mental Health Days: US employees receive seven (7) paid sick/mental health days per year, separate from vacation PTO.",
                "Year-End Recharge: GSD grants a company-wide paid slow-down between December 26 and December 31 for non-critical project teams.",
            ],
        ),
        (
            "4. Health, Dental, Vision, and Retirement Benefits (United States)",
            [
                "Medical Insurance: GSD offers two national BlueCross BlueShield (BCBS) medical plans. GSD pays 90% of employee premiums and 75% of dependent premiums:",
                "  1) GSD Platinum PPO Plan: $250 annual deductible, $20 primary care copay, $35 specialist copay.",
                "  2) GSD High-Deductible Health Plan (HDHP) with HSA: $1,600 individual deductible; GSD contributes $1,500/year ($3,000 for families) directly into the employee's Health Savings Account (HSA).",
                "Dental & Vision: 100% employer-paid Delta Dental PPO (includes $2,500 orthodontia lifetime maximum) and VSP Vision coverage ($250 annual frame allowance).",
                "401(k) Retirement Plan: GSD matches 100% of employee contributions up to 5% of base salary with immediate 100% vesting.",
                "Wellness & Home Office Stipend: $1,200/year Lifestyle & Wellness stipend plus a one-time $1,000 Home Office Ergonomic Setup allowance.",
            ],
        ),
        (
            "5. US Workplace Policies & Company Video Library",
            [
                "Hybrid & Remote Work Policy: GSD operates a Remote-First model in the US with optional co-working hubs in Austin, New York, and San Francisco. Core collaboration hours with Argentina teams are 10:00 AM to 3:00 PM US Eastern Time.",
                "US Benefits Video Resources:",
                "- Video VID-US-201: 'Navigating Your GSD US BCBS Medical Plan & HSA' (11 mins)",
                "- Video VID-US-202: 'Applying for US Paid Paternal & Parental Leave in Workday' (7 mins)",
                "- Video VID-US-203: 'Maximizing Your GSD 401(k) 5% Match with Fidelity' (10 mins)",
            ],
        ),
    ]


def _argentina_benefits_sections() -> List[Tuple[str, List[str]]]:
    return [
        (
            "1. GSD Argentina Employee Benefits Overview",
            [
                "This document defines the official employee benefits, paternal/parental leave, vacation rules, health coverage (Prepaga), and workplace policies for full-time Argentina employees of GSD (Global Software Delivery).",
                "All benefits in this guide supplement and exceed the statutory minimums established by Argentina's Ley de Contrato de Trabajo (LCT No. 20.744).",
            ],
        ),
        (
            "2. Paternal & Parental Leave Policy (Argentina - Licencia por Paternidad y Parental)",
            [
                "Enhanced Paid Paternal Leave (Licencia por Paternidad / Co-Parent): While Argentine statutory law provides only 2 days, GSD provides six (6) weeks (30 business days / 42 calendar days) of 100% fully paid Paternal / Co-Parent Leave for fathers and non-birthing parents upon the birth or adoption of a child.",
                "Maternity / Primary Caregiver Leave: Birthing mothers receive ninety (90) calendar days of statutory leave plus an additional thirty (30) calendar days fully paid by GSD, totaling 120 calendar days (approx. 17 weeks) at 100% salary.",
                "Soft Landing Return (Regreso Gradual): Both mothers and fathers in Argentina may work a 6-hour reduced daily schedule at 100% pay for the first four (4) weeks after returning from parental leave.",
                "Childcare Subsidy (Reintegro por Guarderia): GSD reimburses up to $250 USD equivalent per month per child (ages 45 days to 4 years) for daycare or accredited caregiver expenses.",
            ],
        ),
        (
            "3. Vacation & Paid Time Off Policy (Argentina - Vacaciones y Dias GSD)",
            [
                "Business-Day Vacation Counting: Instead of counting calendar days as under standard LCT, GSD grants vacation in business days (dias habiles) so holidays and weekends never consume vacation balance:",
                "  - 0 to 5 years tenure: fifteen (15) business days of paid vacation per year (equivalent to 21 calendar days).",
                "  - 5 to 10 years tenure: twenty (20) business days of paid vacation per year.",
                "  - 10+ years tenure: twenty-five (25) business days of paid vacation per year.",
                "GSD Flex Days: In addition to annual vacation, Argentina employees receive three (3) paid 'GSD Flex Days' per year for personal milestones, moving, or family events, plus Exam Leave (up to 12 paid days/year for university students).",
            ],
        ),
        (
            "4. Health Coverage (Medicina Prepaga) & Financial Benefits (Argentina)",
            [
                "Premium Health Coverage (Prepaga): GSD provides 100% subsidized top-tier medical coverage for the employee and their immediate family group (conyuge e hijos) through either OSDE Plan 410 or Swiss Medical Plan SMG50.",
                "Health Plan Highlights: 100% coverage in hospitalization, international travel medical assistance, odontologia general, 100% medication coverage during pregnancy/first year of child's life, and annual optical reimbursement.",
                "Compensation Protection & Split Payment: Salaries are benchmarked in USD with monthly CPI adjustment reviews in ARS, and employees may elect to receive up to 70% of net compensation in USD.",
                "Connectivity, Electricity & Wellness Stipends: Monthly reimbursement of $120 USD equivalent covering high-speed fiber internet, home electricity, and gym/sport memberships (SportClub / Megatlon Pase Libre).",
            ],
        ),
        (
            "5. Argentina Workplace Policies & Company Video Library",
            [
                "Hybrid & Remote Work Policy: GSD Argentina operates Remote-First across Buenos Aires, Cordoba, Rosario, and Mendoza, with optional access to the GSD Palermo Hub in CABA and WeWork All-Access passes.",
                "Argentina Benefits Video Resources:",
                "- Video VID-AR-301: 'Guia de Beneficios GSD Argentina: OSDE 410, Vacaciones en Dias Habiles y Guarderia' (13 mins)",
                "- Video VID-AR-302: 'Como Solicitar la Licencia por Paternidad Extendida (6 Semanas) en GSD' (8 mins)",
                "- Video VID-AR-303: 'Politica de Equipamiento IT, Reintegros de Conectividad y Seguridad' (12 mins)",
            ],
        ),
    ]


def generate_all_hr_pdfs(output_dir: Path = DEFAULT_OUTPUT_DIR) -> Dict[str, Path]:
    """Generate all three mock GSD HR policy PDFs and return a mapping of filename to path."""
    output_dir.mkdir(parents=True, exist_ok=True)
    generated: Dict[str, Path] = {}

    holidays_path = _render_policy_pdf(
        output_path=output_dir / "gsd_holidays_us_argentina.pdf",
        doc_title="GSD 2026 Holiday Calendar & Time-Tracking Policy (US & Argentina)",
        doc_code="POL-HR-001",
        sections=_holidays_sections(),
    )
    generated[holidays_path.name] = holidays_path

    us_benefits_path = _render_policy_pdf(
        output_path=output_dir / "gsd_benefits_usa.pdf",
        doc_title="GSD United States (US) Employee Benefits & Workplace Guide",
        doc_code="POL-HR-002-US",
        sections=_us_benefits_sections(),
    )
    generated[us_benefits_path.name] = us_benefits_path

    ar_benefits_path = _render_policy_pdf(
        output_path=output_dir / "gsd_benefits_argentina.pdf",
        doc_title="GSD Argentina Employee Benefits & Workplace Guide",
        doc_code="POL-HR-003-AR",
        sections=_argentina_benefits_sections(),
    )
    generated[ar_benefits_path.name] = ar_benefits_path

    return generated


def main() -> None:
    """CLI entrypoint for generating the 3 GSD HR PDFs."""
    generated = generate_all_hr_pdfs()
    print(f"Generated {len(generated)} GSD HR PDF files in {DEFAULT_OUTPUT_DIR}:")
    for name, path in generated.items():
        print(f"  - {name} ({path.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
