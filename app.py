# app.py
"""
Streamlit app implementing the Worker Compensation claim form described by the user.

Run:
pip install streamlit streamlit-drawable-canvas python-dateutil
streamlit run app.py
"""

import streamlit as st
from datetime import date, datetime
import re
from dateutil.relativedelta import relativedelta
from streamlit_drawable_canvas import st_canvas
from io import BytesIO

st.set_page_config(page_title="Claim Form", layout="wide")

# ----- Helpers -----
def is_valid_ssn(ssn: str) -> bool:
    return bool(re.fullmatch(r"\d{3}-\d{2}-\d{4}", ssn))

def format_ssn(raw: str) -> str:
    digits = re.sub(r"\D", "", raw)
    if len(digits) <= 3:
        return digits
    if len(digits) <= 5:
        return f"{digits[:3]}-{digits[3:]}"
    return f"{digits[:3]}-{digits[3:5]}-{digits[5:9]}"

def is_valid_fein(fein: str) -> bool:
    return bool(re.fullmatch(r"\d{2}-\d{7}", fein))

def disable_future(d: date) -> bool:
    return d <= date.today()

def age_at_least(dob: date, years: int = 18) -> bool:
    return dob <= date.today() - relativedelta(years=years)

def must_be_on_or_after(a: date, b: date) -> bool:
    # a must be >= b
    return a >= b

def bytes_to_file(bytes_obj, filename="file"):
    return BytesIO(bytes_obj)

# ----- Layout -----
st.title("Workers' Compensation — Claim Intake Form (Streamlit UI)")

# Use a form so the front-end remains responsive; we will still validate on change
with st.form(key="claim_form", clear_on_submit=False):
    cols = st.columns([1, 1])
    with cols[0]:
        st.subheader("Employee")
        emp_first = st.text_input("Employee Name — First", help="Autocomplete from HRIS (mock).", max_chars=50)
        emp_middle = st.text_input("Middle", max_chars=50)
        emp_last = st.text_input("Last", max_chars=50)
        ssn_raw = st.text_input("Social Security Number (###-##-####)", help="Tooltip: SSN required for identification", placeholder="123-45-6789")
        ssn = format_ssn(ssn_raw)
        gender = st.radio("Gender", options=["Male", "Female", "Other"], horizontal=True)
        marital = st.selectbox("Marital Status (optional)", options=["", "Single", "Married", "Divorced", "Widowed"])
        dob = st.date_input("Date of Birth", min_value=date(1900,1,1), max_value=date.today(), help="Must be ≥ 18 years")
        home_street = st.text_input("Home Address — Street")
        home_city = st.text_input("City")
        home_state = st.text_input("State")
        home_zip = st.text_input("ZIP", max_chars=10)
        home_phone = st.text_input("Home Phone (optional)", placeholder="(123) 456-7890")
    with cols[1]:
        st.subheader("Employment & Compensation")
        date_hired = st.date_input("Date Hired", min_value=date(1900,1,1), max_value=date.today())
        occupation = st.selectbox("Occupation (or specify)", options=["", "Clerical", "Manual Labor", "Driver", "Supervisor", "Other"])
        if occupation == "Other" or occupation == "":
            occupation_manual = st.text_input("Occupation (free text)", placeholder="Enter occupation")
        else:
            occupation_manual = ""
        department = st.selectbox("Regular Department (optional)", options=["", "HR", "Operations", "Production", "Sales", "Finance", "IT"])
        apprentice = st.checkbox("Apprentice Status (tooltip)", help="Apprentice status may affect wage logic")
        avg_weekly_wage = st.text_input("Average Weekly Wage (₹)", placeholder="0.00")
        wage_rate_unit = st.selectbox("Rate per", options=["hour", "day", "week"])
        wage_rate_value = st.number_input(f"Rate ({wage_rate_unit})", min_value=0.0, step=0.01, format="%.2f")
        hours_per = st.number_input("Hours per / Days per", min_value=0.0, step=0.5)
        schedule = st.text_area("Normal Work Schedule (weekly grid description) — optional", max_chars=300)

    st.markdown("---")
    st.subheader("Incident / Injury")
    incident_cols = st.columns(3)
    with incident_cols[0]:
        date_of_injury = st.date_input("Date of Injury", max_value=date.today())
        time_of_injury = st.time_input("Time of Injury (24-hour)")
        desc = st.text_area("Description of Injury", max_chars=500)
        how_occurred = st.text_area("How Injury Occurred", help="Provide detailed explanation", max_chars=500)
    with incident_cols[1]:
        tools_substances = st.multiselect("Tools/Substances Involved", options=["Forklift", "Ladder", "Machine", "Chemical", "Tool", "Other"])
        on_premises = st.radio("Injury on Employer’s Premises", options=["Yes", "No"])
        address_occurrence = {}
        if on_premises == "No":
            st.info("Provide address of injury occurrence (required when off-premises).")
            occ_street = st.text_input("Occurrence — Street")
            occ_city = st.text_input("Occurrence — City")
            occ_state = st.text_input("Occurrence — State")
            occ_zip = st.text_input("Occurrence — ZIP")
            address_occurrence = {"street": occ_street, "city": occ_city, "state": occ_state, "zip": occ_zip}
        witness = st.text_input("Witness Name and Phone (optional)")
    with incident_cols[2]:
        first_day_lost = st.date_input("First Day of Lost Time", min_value=date(1900,1,1))
        employer_paid_lost_time = st.radio("Employer Paid for Lost Time", options=["Yes", "No"])
        date_employer_notified_injury = st.date_input("Date Employer Notified of Injury")
        date_employer_notified_lost_time = st.date_input("Date Employer Notified of Lost Time")
        return_to_work_date = st.date_input("Return to Work Date (optional)", value=None) if st.checkbox("Has Return-to-Work Date?") else None
        rtw_same_employer = st.radio("RTW Same Employer (optional)", options=["Yes","No"])
        rtw_restrictions = st.checkbox("RTW With Restrictions (if yes, explain)")
        rtw_restrictions_text = st.text_area("RTW Restrictions (explain)", max_chars=300) if rtw_restrictions else ""

    st.markdown("---")
    st.subheader("Medical")
    med_cols = st.columns(2)
    with med_cols[0]:
        treating_physician = st.text_input("Treating Physician Name", help="Autocomplete from registry (mock)")
        extent_treatment = st.multiselect("Extent of Medical Treatment", options=["ER Visit", "Surgery", "Physical Therapy", "Medication", "Other"])
        death_result = st.radio("Death Result of Injury", options=["No","Yes"])
        if death_result == "Yes":
            st.warning("Death selected — dependent logic triggered (not expanded here).")
    with med_cols[1]:
        objective_findings = st.text_area("Objective Findings (diagnostic results)", max_chars=1000)
        medical_diagnoses = st.text_area("Medical Diagnosis(es)", max_chars=300)
        icd_codes = st.text_input("ICD Code(s)", placeholder="e.g. S39.012A")

    st.markdown("---")
    st.subheader("Employer & Insurer")
    emp_cols = st.columns(2)
    with emp_cols[0]:
        employer_legal = st.text_input("Employer Legal Name (autocomplete from FEIN registry)")
        employer_dba = st.text_input("Employer DBA Name (optional)")
        employer_mailing_street = st.text_input("Employer Mailing Street")
        employer_mailing_city = st.text_input("City")
        employer_mailing_state = st.text_input("State")
        employer_mailing_zip = st.text_input("ZIP")
        employer_fein_raw = st.text_input("Employer FEIN (##-#######)")
        employer_fein = re.sub(r"\D","", employer_fein_raw)
        if employer_fein and len(employer_fein) == 9:
            employer_fein = employer_fein[:2] + "-" + employer_fein[2:]
    with emp_cols[1]:
        unemployment_id = st.text_input("Unemployment ID Number (optional)")
        employer_contact = st.text_input("Employer Contact Name & Phone")
        employer_physical_diff = st.checkbox("Employer Physical Address different from mailing?")
        if employer_physical_diff:
            emp_phys_street = st.text_input("Employer Physical Street")
            emp_phys_city = st.text_input("Employer Physical City")
            emp_phys_state = st.text_input("Employer Physical State")
            emp_phys_zip = st.text_input("Employer Physical ZIP")
        insurer_name = st.text_input("Insurer Name (autocomplete)")
        insured_legal_name_fein = st.text_input("Insured Legal Name & FEIN (validation)")
        policy_number = st.text_input("Policy Number")
        date_insurer_received_notice = st.date_input("Date Insurer Received Notice", max_value=date.today())

    st.markdown("---")
    st.subheader("Claims Admin / CA")
    ca_cols = st.columns(2)
    with ca_cols[0]:
        claims_admin = st.text_input("Claims Admin Company Name (autocomplete)")
        ca_address_street = st.text_input("CA Address — Street")
        ca_address_city = st.text_input("City")
        ca_address_state = st.text_input("State")
        ca_address_zip = st.text_input("ZIP")
    with ca_cols[1]:
        ca_fein_raw = st.text_input("CA FEIN (##-#######)")
        ca_fein = re.sub(r"\D","", ca_fein_raw)
        if ca_fein and len(ca_fein) == 9:
            ca_fein = ca_fein[:2] + "-" + ca_fein[2:]
        ca_claim_number = st.text_input("CA Claim Number")
        claim_type = st.selectbox("Claim Type Code", options=["", "Injury", "Illness", "Death"])
        loss_type_code = st.selectbox("Type of Loss Code", options=["", "Strain", "Contusion", "Laceration", "Other"])
        late_reason_code = st.selectbox("Late Reason Code (visible only if late)", options=["", "Late Reporting — reason 1", "Late Reporting — reason 2"])

    st.markdown("---")
    st.subheader("Attachments & Submission")
    upload_wage = st.file_uploader("Upload Wage Statement (PDF/Excel)", type=["pdf","xls","xlsx"], accept_multiple_files=False)
    upload_docs = st.file_uploader("Upload Additional Docs (multi)", type=["pdf","jpg","png","xls","xlsx"], accept_multiple_files=True)
    st.markdown("**Claim Completeness Meter**")
    # ----- Completeness calculation -----
    required_checks = {
        "employee_name": bool(emp_first and emp_last),
        "ssn": is_valid_ssn(ssn),
        "dob": age_at_least(dob, 18),
        "date_hired": bool(date_hired),
        "date_of_injury": bool(date_of_injury),
        "time_of_injury": bool(time_of_injury),
        "description": bool(desc.strip()),
        "how_occurred": bool(how_occurred.strip()),
        "treating_physician": bool(treating_physician.strip()),
        "employer_legal": bool(employer_legal.strip()),
        "employer_fein": is_valid_fein(employer_fein) if employer_fein else False,
        "policy_number": bool(policy_number.strip()),
        "date_insurer_received_notice": bool(date_insurer_received_notice),
        "ca_claim_number": bool(ca_claim_number.strip())
    }
    # If off-premises, require occurrence address
    if on_premises == "No":
        required_checks["occurrence_address"] = all([address_occurrence.get("street"), address_occurrence.get("city"), address_occurrence.get("state"), address_occurrence.get("zip")])
    # Count completeness
    completeness_pct = int(100 * sum(required_checks.values()) / len(required_checks))
    st.progress(completeness_pct / 100)
    st.write(f"Completeness: {completeness_pct}%")

    # Final review summary (accordion)
    with st.expander("Final Review Summary (expand)"):
        st.write("Employee:", f"{emp_first} {emp_middle} {emp_last}")
        st.write("SSN:", ssn if is_valid_ssn(ssn) else f"{ssn} (INVALID)")
        st.write("DOB:", dob, "Age OK" if age_at_least(dob, 18) else "Under 18!")
        st.write("Date of Injury:", date_of_injury, "Time:", time_of_injury)
        st.write("Employer:", employer_legal, "FEIN:", employer_fein if is_valid_fein(employer_fein) else f"{employer_fein} (INVALID)")
        st.write("Insurer:", insurer_name, "Policy:", policy_number)
        st.write("Claim Type:", claim_type, "Loss Type:", loss_type_code)
        st.write("Completeness:", f"{completeness_pct}%")

    st.markdown("---")
    st.subheader("Digital Signature (Employer + Physician)")
    st.info("Sign below (use mouse/touch). Click 'Clear canvas' in the toolbar to erase.")
    signature_canvas = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=2,
        stroke_color="#000",
        background_color="#fff",
        height=200,
        width=700,
        drawing_mode="freedraw",
        key="sig_canvas"
    )

    # Validate before allowing submission
    submit_disabled_reasons = []
    if not required_checks["employee_name"]:
        submit_disabled_reasons.append("Employee full name required.")
    if not required_checks["ssn"]:
        submit_disabled_reasons.append("Valid SSN required (###-##-####).")
    if not required_checks["dob"]:
        submit_disabled_reasons.append("Employee must be ≥ 18 years old.")
    if not required_checks["date_of_injury"]:
        submit_disabled_reasons.append("Date of injury required.")
    if not required_checks["treating_physician"]:
        submit_disabled_reasons.append("Treating physician required.")
    if not required_checks["employer_legal"]:
        submit_disabled_reasons.append("Employer legal name required.")
    if not required_checks["employer_fein"]:
        submit_disabled_reasons.append("Valid Employer FEIN required (##-#######).")
    if signature_canvas.image_data is None:
        submit_disabled_reasons.append("Digital signature required.")

    if submit_disabled_reasons:
        st.warning("Form cannot be submitted until required fields are valid.")
        for r in submit_disabled_reasons[:6]:
            st.write("- " + r)
        submit_btn = st.form_submit_button("Submit (disabled)", disabled=True)
    else:
        submit_btn = st.form_submit_button("Submit")

    # If the user clicked Submit (and validation passed)
    if submit_btn and not submit_disabled_reasons:
        # Collect payload (example)
        payload = {
            "employee": {"first": emp_first, "middle": emp_middle, "last": emp_last, "ssn": ssn, "dob": str(dob)},
            "employment": {"hired": str(date_hired), "occupation": occupation or occupation_manual, "avg_weekly_wage": avg_weekly_wage},
            "incident": {"date": str(date_of_injury), "time": str(time_of_injury), "desc": desc, "how": how_occurred},
            "medical": {"physician": treating_physician, "diagnoses": medical_diagnoses},
            "employer": {"legal": employer_legal, "fein": employer_fein, "contact": employer_contact}
        }
        st.success("Form submitted successfully.")
        st.json(payload)

        # Save signature as PNG to buffer and offer download
        if signature_canvas.image_data is not None:
            import PIL.Image as Image
            import numpy as np
            img = signature_canvas.image_data
            # Convert RGBA array to PIL image
            img = (255 * img).astype("uint8")
            pil_img = Image.fromarray(img)
            buf = BytesIO()
            pil_img.save(buf, format="PNG")
            buf.seek(0)
            st.download_button("Download Signature (PNG)", data=buf, file_name="signature.png", mime="image/png")

        # Save uploaded files (example)
        if upload_wage:
            st.write("Wage statement uploaded:", upload_wage.name)
        if upload_docs:
            st.write(f"{len(upload_docs)} additional document(s) uploaded.")

# End of form
st.markdown("### Notes")
st.write("This Streamlit UI demonstrates required validation, conditional fields, a claim completeness meter, digital signature, and file uploads as requested. Adapt the autocomplete hooks to call your HRIS/FEIN/registry APIs where needed.")
