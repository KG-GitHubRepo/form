# streamlit_app.py
"""
First Medical Form (Streamlit UI)
Save this file as streamlit_app.py and run:
pip install streamlit streamlit-drawable-canvas python-dateutil Pillow
streamlit run streamlit_app.py
"""

import streamlit as st
from datetime import date, datetime, time
import re
from dateutil.relativedelta import relativedelta
from streamlit_drawable_canvas import st_canvas
from io import BytesIO

st.set_page_config(page_title="First Medical Form", layout="wide")

# ---------------- Helpers ----------------
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

def age_at_least(dob: date, years: int = 18) -> bool:
    return dob <= date.today() - relativedelta(years=years)

# ---------------- App Layout ----------------
st.title("First Medical Form")

# use a form for atomic submit
with st.form(key="claim_form"):
    # Employee block
    st.subheader("Employee")
    emp_cols = st.columns(2)
    with emp_cols[0]:
        emp_first = st.text_input("Employee First Name", key="emp_first", max_chars=50)
        emp_middle = st.text_input("Employee Middle Name", key="emp_middle", max_chars=50)
        emp_last = st.text_input("Employee Last Name", key="emp_last", max_chars=50)
        ssn_raw = st.text_input("Social Security Number (###-##-####)", key="ssn_raw", placeholder="123-45-6789")
        ssn = format_ssn(ssn_raw)
        gender = st.radio("Gender", options=["Male", "Female", "Other"], horizontal=True, key="gender")
        marital = st.selectbox("Marital Status (optional)", options=["", "Single", "Married", "Divorced", "Widowed"], key="marital")
        dob = st.date_input("Date of Birth", min_value=date(1900, 1, 1), max_value=date.today(), key="dob")
    with emp_cols[1]:
        home_street = st.text_input("Home Street Address", key="home_street")
        home_city = st.text_input("Home City", key="home_city")
        home_state = st.text_input("Home State", key="home_state")
        home_zip = st.text_input("Home ZIP", key="home_zip")
        home_phone = st.text_input("Home Phone (optional)", key="home_phone", placeholder="(123) 456-7890")

    st.markdown("---")
    # Employment & Compensation
    st.subheader("Employment & Compensation")
    emp2_cols = st.columns(2)
    with emp2_cols[0]:
        date_hired = st.date_input("Date Hired", min_value=date(1900, 1, 1), max_value=date.today(), key="date_hired")
        occupation = st.selectbox("Occupation (choose or type 'Other')", options=["", "Clerical", "Manual Labor", "Driver", "Supervisor", "Other"], key="occupation")
        occupation_manual = ""
        if occupation == "Other" or occupation == "":
            occupation_manual = st.text_input("Occupation (free text)", key="occupation_manual")
        department = st.selectbox("Regular Department (optional)", options=["", "HR", "Operations", "Production", "Sales", "Finance", "IT"], key="department")
        apprentice = st.checkbox("Apprentice Status (may affect wage rules)", key="apprentice")
    with emp2_cols[1]:
        avg_weekly_wage = st.text_input("Average Weekly Wage (₹)", key="avg_weekly_wage", placeholder="0.00")
        wage_rate_unit = st.selectbox("Rate per", options=["hour", "day", "week"], key="wage_rate_unit")
        wage_rate_value = st.number_input(f"Rate value ({wage_rate_unit})", min_value=0.0, step=0.01, format="%.2f", key="wage_rate_value")
        hours_per = st.number_input("Hours per / Days per", min_value=0.0, step=0.5, key="hours_per")
        schedule = st.text_area("Normal Work Schedule (optional)", max_chars=300, key="schedule")

    st.markdown("---")
    st.subheader("Incident / Injury")
    incident_cols = st.columns(3)
    with incident_cols[0]:
        date_of_injury = st.date_input("Date of Injury", max_value=date.today(), key="date_of_injury")
        time_of_injury = st.time_input("Time of Injury (24-hour)", value=time(0, 0), key="time_of_injury")
        desc = st.text_area("Description of Injury (max 500 chars)", max_chars=500, key="desc")
        how_occurred = st.text_area("How Injury Occurred (prompted examples)", max_chars=500, key="how_occurred")
    with incident_cols[1]:
        tools_substances = st.multiselect("Tools/Substances Involved (tags)", options=["Forklift", "Ladder", "Machine", "Chemical", "Tool", "Other"], key="tools_substances")
        on_premises = st.radio("Injury on Employer’s Premises?", options=["Yes", "No"], key="on_premises")
        occ_address = {}
        if on_premises == "No":
            st.info("Provide address of injury occurrence (required when off-premises).")
            occ_street = st.text_input("Occurrence Street", key="occ_street")
            occ_city = st.text_input("Occurrence City", key="occ_city")
            occ_state = st.text_input("Occurrence State", key="occ_state")
            occ_zip = st.text_input("Occurrence ZIP", key="occ_zip")
            occ_address = {"street": occ_street, "city": occ_city, "state": occ_state, "zip": occ_zip}
        witness = st.text_input("Witness Name & Phone (optional)", key="witness")
    with incident_cols[2]:
        first_day_lost = st.date_input("First Day of Lost Time", min_value=date(1900, 1, 1), key="first_day_lost")
        employer_paid_lost_time = st.radio("Employer Paid for Lost Time?", options=["Yes", "No"], key="employer_paid_lost_time")
        date_employer_notified_injury = st.date_input("Date Employer Notified of Injury", key="date_employer_notified_injury")
        date_employer_notified_lost_time = st.date_input("Date Employer Notified of Lost Time", key="date_employer_notified_lost_time")
        has_rtw_date = st.checkbox("Has Return-to-Work Date?", key="has_rtw_date")
        return_to_work_date = st.date_input("Return to Work Date", min_value=date(1900, 1, 1), key="return_to_work_date") if has_rtw_date else None
        rtw_same_employer = st.radio("RTW Same Employer?", options=["Yes", "No"], key="rtw_same_employer")
        rtw_restrictions = st.checkbox("RTW With Restrictions (if yes, explain)", key="rtw_restrictions")
        rtw_restrictions_text = st.text_area("RTW Restrictions Explanation", max_chars=300, key="rtw_restrictions_text") if rtw_restrictions else ""

    st.markdown("---")
    st.subheader("Medical")
    med_cols = st.columns(2)
    with med_cols[0]:
        treating_physician = st.text_input("Treating Physician Name (registry autocomplete)", key="treating_physician")
        extent_treatment = st.multiselect("Extent of Medical Treatment", options=["ER Visit", "Surgery", "Physical Therapy", "Medication", "Other"], key="extent_treatment")
        death_result = st.radio("Death Result of Injury?", options=["No", "Yes"], key="death_result")
        if death_result == "Yes":
            st.warning("Death selected — dependent logic will be triggered in processing.")
    with med_cols[1]:
        objective_findings = st.text_area("Objective Findings (diagnostic results)", max_chars=1000, key="objective_findings")
        medical_diagnoses = st.text_area("Medical Diagnosis(es)", max_chars=300, key="medical_diagnoses")
        icd_codes = st.text_input("ICD Code(s)", placeholder="e.g. S39.012A", key="icd_codes")

    st.markdown("---")
    st.subheader("Employer & Insurer")
    emp_cols = st.columns(2)
    with emp_cols[0]:
        employer_legal = st.text_input("Employer Legal Name (FEIN autocomplete)", key="employer_legal")
        employer_dba = st.text_input("Employer DBA Name (optional)", key="employer_dba")
        employer_mailing_street = st.text_input("Employer Mailing Street", key="employer_mailing_street")
        employer_mailing_city = st.text_input("Employer Mailing City", key="employer_mailing_city")
        employer_mailing_state = st.text_input("Employer Mailing State", key="employer_mailing_state")
        employer_mailing_zip = st.text_input("Employer Mailing ZIP", key="employer_mailing_zip")
        employer_fein_raw = st.text_input("Employer FEIN (##-#######)", key="employer_fein_raw")
        employer_fein = re.sub(r"\D", "", employer_fein_raw)
        if employer_fein and len(employer_fein) == 9:
            employer_fein = employer_fein[:2] + "-" + employer_fein[2:]
    with emp_cols[1]:
        unemployment_id = st.text_input("Unemployment ID Number (optional)", key="unemployment_id")
        employer_contact = st.text_input("Employer Contact Name & Phone", key="employer_contact")
        employer_physical_diff = st.checkbox("Employer Physical Address different from mailing?", key="employer_physical_diff")
        if employer_physical_diff:
            emp_phys_street = st.text_input("Employer Physical Street", key="emp_phys_street")
            emp_phys_city = st.text_input("Employer Physical City", key="emp_phys_city")
            emp_phys_state = st.text_input("Employer Physical State", key="emp_phys_state")
            emp_phys_zip = st.text_input("Employer Physical ZIP", key="emp_phys_zip")
        insurer_name = st.text_input("Insurer Name (autocomplete)", key="insurer_name")
        insured_legal_name_fein = st.text_input("Insured Legal Name & FEIN", key="insured_legal_name_fein")
        policy_number = st.text_input("Policy Number", key="policy_number")
        date_insurer_received_notice = st.date_input("Date Insurer Received Notice", max_value=date.today(), key="date_insurer_received_notice")

    st.markdown("---")
    st.subheader("Claims Admin / CA")
    ca_cols = st.columns(2)
    with ca_cols[0]:
        claims_admin = st.text_input("Claims Admin Company Name (autocomplete)", key="claims_admin")
        ca_address_street = st.text_input("CA Mailing Street", key="ca_address_street")
        ca_address_city = st.text_input("CA Mailing City", key="ca_address_city")
        ca_address_state = st.text_input("CA Mailing State", key="ca_address_state")
        ca_address_zip = st.text_input("CA Mailing ZIP", key="ca_address_zip")
    with ca_cols[1]:
        ca_fein_raw = st.text_input("CA FEIN (##-#######)", key="ca_fein_raw")
        ca_fein = re.sub(r"\D", "", ca_fein_raw)
        if ca_fein and len(ca_fein) == 9:
            ca_fein = ca_fein[:2] + "-" + ca_fein[2:]
        ca_claim_number = st.text_input("CA Claim Number", key="ca_claim_number")
        claim_type = st.selectbox("Claim Type Code", options=["", "Injury", "Illness", "Death"], key="claim_type")
        loss_type_code = st.selectbox("Type of Loss Code", options=["", "Strain", "Contusion", "Laceration", "Other"], key="loss_type_code")
        late_reason_code = st.selectbox("Late Reason Code (visible only if late)", options=["", "Late — reason 1", "Late — reason 2"], key="late_reason_code")

    st.markdown("---")
    st.subheader("Attachments & Submission")
    upload_wage = st.file_uploader("Upload Wage Statement (PDF/Excel)", type=["pdf", "xls", "xlsx"], accept_multiple_files=False, key="upload_wage")
    upload_docs = st.file_uploader("Upload Additional Docs (multi)", type=["pdf", "jpg", "png", "xls", "xlsx"], accept_multiple_files=True, key="upload_docs")

    st.markdown("**Claim Completeness Meter**")
    # required checks
    required_checks = {
        "employee_name": bool(emp_first and emp_last),
        "ssn": is_valid_ssn(ssn),
        "dob": age_at_least(dob, 18),
        "date_hired": bool(date_hired),
        "date_of_injury": bool(date_of_injury),
        "time_of_injury": bool(time_of_injury),
        "description": bool(desc and desc.strip()),
        "how_occurred": bool(how_occurred and how_occurred.strip()),
        "treating_physician": bool(treating_physician and treating_physician.strip()),
        "employer_legal": bool(employer_legal and employer_legal.strip()),
        "employer_fein": is_valid_fein(employer_fein) if employer_fein else False,
        "policy_number": bool(policy_number and policy_number.strip()),
        "date_insurer_received_notice": bool(date_insurer_received_notice),
        "ca_claim_number": bool(ca_claim_number and ca_claim_number.strip())
    }
    if on_premises == "No":
        required_checks["occurrence_address"] = all([occ_address.get("street"), occ_address.get("city"), occ_address.get("state"), occ_address.get("zip")])

    completeness_pct = int(100 * sum(required_checks.values()) / len(required_checks))
    st.progress(completeness_pct / 100)
    st.write(f"Completeness: {completeness_pct}%")

    with st.expander("Final Review Summary"):
        st.write("Employee:", f"{emp_first} {emp_middle} {emp_last}")
        st.write("SSN:", ssn if is_valid_ssn(ssn) else f"{ssn} (INVALID)")
        st.write("DOB:", dob, "— Age OK" if age_at_least(dob, 18) else "— Under 18!")
        st.write("Date of Injury:", date_of_injury, "Time:", time_of_injury)
        st.write("Employer:", employer_legal, "FEIN:", (employer_fein if is_valid_fein(employer_fein) else f"{employer_fein} (INVALID)"))
        st.write("Insurer:", insurer_name, "Policy:", policy_number)
        st.write("Claim Type:", claim_type, "Loss Type:", loss_type_code)
        st.write("Completeness:", f"{completeness_pct}%")

    st.markdown("---")
    st.subheader("Digital Signature (Employer + Physician)")
    st.info("Sign below (use mouse/touch). Click 'Clear canvas' in the toolbar to erase.")
    signature_canvas = st_canvas(
        fill_color="rgba(0, 0, 0, 0)",  # transparent
        stroke_width=2,
        stroke_color="#000000",
        background_color="#ffffff",
        height=200,
        width=700,
        drawing_mode="freedraw",
        key="signature_canvas"
    )

    # ---------- Single Submit Button (inside the form) ----------
    submit_btn = st.form_submit_button("Submit Claim")

    # ---------- Submission handling ----------
    if submit_btn:
        # basic validation list
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
            st.error("Form submission blocked. Fix the following:")
            for r in submit_disabled_reasons:
                st.write("- " + r)
        else:
            # Build payload
            payload = {
                "employee": {"first": emp_first, "middle": emp_middle, "last": emp_last, "ssn": ssn, "dob": str(dob)},
                "employment": {"hired": str(date_hired), "occupation": occupation or occupation_manual, "avg_weekly_wage": avg_weekly_wage},
                "incident": {"date": str(date_of_injury), "time": str(time_of_injury), "desc": desc, "how": how_occurred, "on_premises": on_premises},
                "medical": {"physician": treating_physician, "diagnoses": medical_diagnoses},
                "employer": {"legal": employer_legal, "fein": employer_fein, "contact": employer_contact},
                "completeness_pct": completeness_pct
            }
            st.success("Form submitted successfully.")
            st.json(payload)

            # Save signature as PNG and offer download
            if signature_canvas.image_data is not None:
                import PIL.Image as Image
                import numpy as np
                img = signature_canvas.image_data
                img = (255 * img).astype("uint8")
                pil_img = Image.fromarray(img)
                buf = BytesIO()
                pil_img.save(buf, format="PNG")
                buf.seek(0)
                st.download_button("Download Signature (PNG)", data=buf, file_name="signature.png", mime="image/png")

            # Show uploaded files summary
            if upload_wage:
                st.write("Wage statement uploaded:", upload_wage.name)
            if upload_docs:
                st.write(f"{len(upload_docs)} additional document(s) uploaded.")

# End of with st.form
st.markdown("### Notes")
st.write("All repeated widgets have unique keys to avoid StreamlitDuplicateElementId. Make sure to wire your autocomplete hooks to your registry/HRIS using secure secrets when deploying.")
