import streamlit as st
import pandas as pd
from datetime import date
import os

# 1. Hardcoded Class Credentials
class_passwords = {
    'class1': 'ABCD',
    'class2': 'EFGH'
}

today_date = date.today().strftime("%Y-%m-%d")

def main():
    st.title("Welcome to the Attendance Log")

    # Initialize Session State
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        st.session_state["class_name"] = None

    # 2. Login Form
    if not st.session_state["authenticated"]:
        with st.form("login_form"):
            class_input = st.selectbox("Select Class", list(class_passwords.keys()))
            passw_input = st.text_input("Enter Password", type="password")
            submit = st.form_submit_button("Login")

            if submit:
                if passw_input == class_passwords.get(class_input):
                    st.session_state["authenticated"] = True
                    st.session_state["class_name"] = class_input
                    st.success(f"Logged into {class_input}!")
                    st.rerun()
                else:
                    st.error("Invalid class or password")

    # 3. Attendance Interface (Post-Login)
    else:
        class_name = st.session_state["class_name"]
        st.header(f"Attendance for {class_name}")

        CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
        file_name = os.path.join(CURRENT_DIR, f"{class_name}.csv")


        # Check if student file exists
        try:
            df = pd.read_csv(file_name)
        except FileNotFoundError:
            st.error(f"Error: File not found for {class_name} ({file_name})")
            if st.button("Back / Logout"):
                st.session_state["authenticated"] = False
                st.session_state["class_name"] = None
                st.rerun()
            return

        st.subheader(f"Mark Attendance for {class_name} - {today_date}")

        # Ensure today's date column exists in DataFrame
        if today_date not in df.columns:
            df[today_date] = 'A'

        marked_attendance = {}

        # 4. Attendance Checklist Form
        with st.form("attendance_form"):
            st.write("**Students List**")

            for index, row in df.iterrows():
                student_name = row['Name']
                roll_no = row['Roll_No']
                
                # Pre-fill checkbox if already marked 'P'
                initial_status = (row[today_date] == 'P')

                checkbox_state = st.checkbox(
                    f"**{roll_no}** - {student_name}",
                    value=initial_status,
                    key=f"check_{index}"
                )
                marked_attendance[index] = 'P' if checkbox_state else 'A'
    

            submitted = st.form_submit_button("Submit Attendance")

            if submitted:
                # Update today's status for each student
                for index, status in marked_attendance.items():
                    df.loc[index, today_date] = status

                # Save back to CSV
                df.to_csv(file_name, index=False)
                st.success(f"Attendance for {today_date} is submitted successfully!")

        # 5. Logout Option
        st.divider()
        if st.button("Logout"):
            st.session_state["authenticated"] = False
            st.session_state["class_name"] = None
            st.rerun()

if __name__ == "__main__":
    main()