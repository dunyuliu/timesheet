import streamlit as st
import gspread
from datetime import datetime
import pandas as pd

# --- Google Sheet Configuration ---
# Replace with your Google Sheet URL
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1ceutTaxlt9vYK_17L_nFE8O8jyJpUbmFctoSvecVQjQ/edit?usp=sharing"
WORKSHEET_NAME = "Sheet1"  # Or whatever your sheet is named

# --- Streamlit App ---
st.title("Timesheet")

# Initialize session state
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "description" not in st.session_state:
    st.session_state.description = ""

# Function to connect to Google Sheets and get the worksheet
def get_worksheet():
    try:
        # Use Streamlit's secrets to get the service account credentials
        gc = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
        spreadsheet = gc.open_by_url(GOOGLE_SHEET_URL)
        worksheet = spreadsheet.worksheet(WORKSHEET_NAME)
        return worksheet
    except Exception as e:
        st.error(f"Failed to connect to Google Sheets: {e}")
        return None

# --- UI and Logic ---

if st.button("Start", key="start_button"):
    st.session_state.start_time = datetime.now()
    st.success(f"Start time recorded: {st.session_state.start_time.strftime('%Y-%m-%d %H:%M:%S')}")

if st.session_state.start_time:
    if st.button("End", key="end_button"):
        end_time = datetime.now()
        start_time = st.session_state.start_time
        duration = end_time - start_time

        st.session_state.end_time = end_time
        st.session_state.duration = str(duration).split('.')[0] # Remove microseconds

        st.info(f"End time recorded: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        st.info(f"Total Duration: {st.session_state.duration}")

# Use a text_area for the description and a form for submission
if st.session_state.get("end_time"):
    with st.form("description_form"):
        description = st.text_area("What did you do?", key="description_input")
        submitted = st.form_submit_button("Save to Google Sheet")

        if submitted and description:
            worksheet = get_worksheet()
            if worksheet:
                try:
                    new_row = [
                        st.session_state.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                        st.session_state.end_time.strftime('%Y-%m-%d %H:%M:%S'),
                        st.session_state.duration,
                        description
                    ]
                    worksheet.append_row(new_row)
                    st.success("Your timesheet has been updated!")

                    # Clear state for next entry
                    for key in ["start_time", "end_time", "duration", "description"]:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.experimental_rerun()

                except Exception as e:
                    st.error(f"Failed to write to Google Sheet: {e}")
            else:
                st.error("Could not access the worksheet. Please check your configuration and permissions.")

# --- Installation ---
st.markdown("""
---
### To run this app:
1.  **Install the required libraries:**
    ```bash
    pip install streamlit gspread pandas
    ```
2.  **Run the app locally:**
    ```bash
    streamlit run timesheet.py
    ```
""")