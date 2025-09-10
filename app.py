import streamlit as st
import requests
from datetime import datetime
import time

st.set_page_config(page_title="Focus - Time Tracker", page_icon="⏱️", layout="centered")

# Your Google Form configuration
FORM_ID = "1FAIpQLSfW0gh8rbHtgeUOLfTP9rxV5aKHI-kcbJ94bbSDNN2c5cZ8EQ"
FORM_SUBMIT_URL = f"https://docs.google.com/forms/d/e/{FORM_ID}/formResponse"

# Form field IDs (extracted from your form)
FORM_FIELDS = {
    "name": "entry.116257796",
    "start_time": "entry.844414881", 
    "end_time": "entry.834530983",
    "duration": "entry.365539651",
    "task_description": "entry.1897147484",
    "location": "entry.1523129993"
}

def submit_to_google_form(data):
    """Submit data to Google Form"""
    try:
        # Prepare the form data
        form_data = {
            FORM_FIELDS["name"]: data["name"],
            FORM_FIELDS["start_time"]: data["start_time"],
            FORM_FIELDS["end_time"]: data["end_time"],
            FORM_FIELDS["duration"]: data["duration"],
            FORM_FIELDS["task_description"]: data["task_description"],
            FORM_FIELDS["location"]: data["location"]
        }
        
        # Submit to Google Form
        response = requests.post(FORM_SUBMIT_URL, data=form_data)
        return response.status_code == 200
    except Exception as e:
        st.error(f"Error submitting to form: {str(e)}")
        return False

def main():
    st.title("⏱️ Focus - Time Tracker")
    st.markdown("Track your work sessions - data automatically saved to Google Forms!")
    
    # Initialize session state
    if 'session_active' not in st.session_state:
        st.session_state.session_active = False
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None
    
    # User identification
    user_name = st.text_input("Your Name:", placeholder="Enter your name")
    
    if not user_name:
        st.warning("Please enter your name to continue.")
        st.stop()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if not st.session_state.session_active:
            if st.button("🟢 START", type="primary", use_container_width=True):
                st.session_state.start_time = datetime.now()
                st.session_state.session_active = True
                st.success(f"Session started at {st.session_state.start_time.strftime('%H:%M:%S')}")
                st.rerun()
        else:
            st.success(f"Session active since {st.session_state.start_time.strftime('%H:%M:%S')}")
    
    with col2:
        if st.session_state.session_active:
            if st.button("🔴 END", type="secondary", use_container_width=True):
                end_time = datetime.now()
                elapsed_time = end_time - st.session_state.start_time
                elapsed_seconds = int(elapsed_time.total_seconds())
                elapsed_formatted = f"{elapsed_seconds // 3600:02d}:{(elapsed_seconds % 3600) // 60:02d}:{elapsed_seconds % 60:02d}"
                
                st.session_state.end_time = end_time
                st.session_state.elapsed_formatted = elapsed_formatted
                st.session_state.show_form = True
                
                st.success(f"Session ended! Duration: {elapsed_formatted}")
                st.rerun()
    
    # Show task entry form after ending session
    if st.session_state.get('show_form', False):
        st.markdown("---")
        st.subheader("📝 Session Complete!")
        
        # Display session summary
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Start Time", st.session_state.start_time.strftime("%H:%M:%S"))
            st.metric("Duration", st.session_state.elapsed_formatted)
        with col2:
            st.metric("End Time", st.session_state.end_time.strftime("%H:%M:%S"))
        
        # Task details form
        with st.form("task_details"):
            task_description = st.text_area("What did you work on?", 
                                           placeholder="Describe your work session...")
            work_location = st.text_input("Where did you work?", 
                                        placeholder="e.g., Office, Home, Coffee shop...")
            
            if st.form_submit_button("💾 Save to Google Form", type="primary"):
                # Prepare data for Google Form
                session_data = {
                    "name": user_name,
                    "start_time": st.session_state.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "end_time": st.session_state.end_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "duration": st.session_state.elapsed_formatted,
                    "task_description": task_description,
                    "location": work_location
                }
                
                with st.spinner("Saving to Google Form..."):
                    if submit_to_google_form(session_data):
                        st.success("✅ Session saved successfully!")
                        st.balloons()
                        time.sleep(2)  # Brief pause for user feedback
                        
                        # Reset session state
                        st.session_state.session_active = False
                        st.session_state.start_time = None
                        st.session_state.show_form = False
                        st.rerun()
                    else:
                        st.error("❌ Failed to save session. Please try again.")
    
    # Display current session info with live timer
    if st.session_state.session_active:
        st.markdown("---")
        
        current_time = datetime.now()
        current_elapsed = current_time - st.session_state.start_time
        current_seconds = int(current_elapsed.total_seconds())
        current_formatted = f"{current_seconds // 3600:02d}:{(current_seconds % 3600) // 60:02d}:{current_seconds % 60:02d}"
        
        st.metric("⏰ Current Session Duration", current_formatted)
        
        # Auto-refresh every 1 second for live timer
        time.sleep(1)
        st.rerun()
    
    # Footer with links
    st.markdown("---")
    st.markdown("### 📊 View Data")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"[📋 View Form]({FORM_SUBMIT_URL.replace('/formResponse', '/viewform')})")
    with col2:
        st.markdown("[📈 View Responses](https://docs.google.com/forms/d/1FAIpQLSfW0gh8rbHtgeUOLfTP9rxV5aKHI-kcbJ94bbSDNN2c5cZ8EQ/edit#responses)")
    
    # Instructions
    st.markdown("### 📖 How it works:")
    st.markdown("""
    1. **Enter your name** and click **🟢 START** to begin timing
    2. Work on your tasks (timer updates in real-time)
    3. Click **🔴 END** when finished
    4. Fill out what you worked on and where
    5. Click **💾 Save** - data automatically goes to Google Form/Sheet
    6. Start your next session!
    
    **✨ Completely automatic** - no copy-pasting needed!
    """)

if __name__ == "__main__":
    main()