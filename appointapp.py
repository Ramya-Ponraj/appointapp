import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
from datetime import datetime

# -------------- CONFIGURE GEMINI API ---------------
genai.configure(api_key="AIzaSyDUqoyAAYv4Veg3hwrfELljrC_-MkcJMpg")  # Replace with your actual Gemini API Key
model = genai.GenerativeModel("gemini-2.0-flash")

# -------------- PAGE CONFIG ------------------------
st.set_page_config(page_title="Appointment Booking", layout="centered")
st.title("📅 Book Your Appointment")

# -------------- SESSION STATE ----------------------
if "appointment_summary" not in st.session_state:
    st.session_state["appointment_summary"] = ""
if "appointment_data" not in st.session_state:
    st.session_state["appointment_data"] = {}

# -------------- USER INPUT FORM ---------------------
with st.form("booking_form"):
    name = st.text_input("Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone Number")
    appointment_type = st.selectbox("Type of Appointment", ["Dental Check-up", "Vision Test", "General Consultation", "Therapy Session"])
    date = st.date_input("Preferred Date")
    time = st.time_input("Preferred Time")
    notes = st.text_area("Additional Notes", height=100)

    submitted = st.form_submit_button("Book Appointment")

# -------------- HANDLE SUBMISSION --------------------
if submitted:
    if not name or not email or not phone:
        st.warning("❗ Please fill out all required fields.")
    else:
        st.success("✅ Appointment information submitted. Generating confirmation...")
        st.session_state["appointment_data"] = {
            "name": name,
            "email": email,
            "phone": phone,
            "appointment_type": appointment_type,
            "date": date.strftime("%B %d, %Y"),
            "time": time.strftime("%I:%M %p"),
            "notes": notes
        }

        prompt = f"""
        Create a short, friendly appointment confirmation message for:
        Name: {name}
        Email: {email}
        Phone: {phone}
        Appointment: {appointment_type}
        Date: {date.strftime("%B %d, %Y")}
        Time: {time.strftime("%I:%M %p")}
        Notes: {notes}
        """

        response = model.generate_content(prompt)
        summary = response.text.strip()
        st.session_state["appointment_summary"] = summary

# -------------- DISPLAY GENERATED SUMMARY ---------------
if st.session_state["appointment_summary"]:
    st.markdown("### ✉️ Appointment Confirmation")
    st.text_area("Confirmation Message", st.session_state["appointment_summary"], height=200)

    # --- Download PDF ---
    def generate_pdf(text):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        for line in text.split('\n'):
            pdf.multi_cell(0, 10, line)
        file_path = "appointment_confirmation.pdf"
        pdf.output(file_path)
        return file_path

    pdf_file = generate_pdf(st.session_state["appointment_summary"])
    with open(pdf_file, "rb") as f:
        st.download_button(label="📥 Download Confirmation as PDF", data=f, file_name="appointment_confirmation.pdf", mime="application/pdf")

# -------------- RESCHEDULE OPTION ----------------------
st.markdown("---")
st.subheader("🔁 Reschedule Appointment")

if st.button("Reschedule with New Date/Time"):
    if not st.session_state["appointment_data"]:
        st.warning("❗ No previous appointment found to reschedule.")
    else:
        new_date = st.date_input("New Date", key="reschedule_date")
        new_time = st.time_input("New Time", key="reschedule_time")

        prompt = f"""
        Regenerate the confirmation message for the following updated appointment:
        Name: {st.session_state['appointment_data']['name']}
        Appointment: {st.session_state['appointment_data']['appointment_type']}
        New Date: {new_date.strftime('%B %d, %Y')}
        New Time: {new_time.strftime('%I:%M %p')}
        """

        new_response = model.generate_content(prompt)
        new_summary = new_response.text.strip()
        st.session_state["appointment_summary"] = new_summary

        st.success("🔁 Appointment successfully rescheduled!")
        st.text_area("Updated Confirmation", new_summary, height=200)

# -------------- MOCK DYNAMIC SLOT SUGGESTION ----------------------
st.markdown("---")
st.subheader("💡 Need Help Choosing a Slot?")

if st.button("Suggest Alternative Time Slots"):
    slot_prompt = f"""
    Suggest 3 alternative appointment time slots for a {appointment_type} that are close to {time.strftime('%I:%M %p')} on {date.strftime('%A, %B %d')}.
    """
    alt_response = model.generate_content(slot_prompt)
    st.info("Here are some suggestions:")
    st.markdown(alt_response.text.strip())
