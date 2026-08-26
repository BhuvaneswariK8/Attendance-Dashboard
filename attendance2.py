import streamlit as st
import pandas as pd
import os
import datetime
import matplotlib.pyplot as plt

admin_password = "admin123"

class_passwords = {
    'class1': 'ABCD',
    'class2': 'EFGH'}

today_date = datetime.date.today().strftime("%Y-%m-%d")

def main():
    st.title("Welcome", text_alignment="center")
    imp=st.select_slider("Select an option", options=["Admin", "Class Teacher"])
    if imp=="Admin":
        with st.form("admin_form"):
                st.header("Admin Login")
                password = st.text_input("Enter Admin Password", type="password")
                submit = st.form_submit_button("Login")
                if submit:
                    if password == admin_password:
                        st.success("Admin Login Successful!")
                        st.session_state["admin_authenticated"] = True
                        st.session_state["class_name"] = None
                    st.rerun()
                else:
                    st.error("Invalid Admin Password")

                side=st.sidebar.radio("Select an option", ["Take Attendance", "View Attendance","Add Class", "Remove Class"])  
                def take_attendance():
                    st.header("Take Attendance")
                    class_name = st.selectbox("Select Class", list(class_passwords.keys()))
                    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
                    file_name = os.path.join(CURRENT_DIR, f"{class_name}.csv")

                    try:
                        df = pd.read_csv(file_name)
                    except FileNotFoundError:
                        st.error(f"Error: File not found for {class_name} ({file_name})")
                        return

                    st.subheader(f"Mark Attendance for {class_name} - {today_date}")

                    if today_date not in df.columns:
                        df[today_date] = "Absent"

                    for index, row in df.iterrows():
                        student_name = row['Name']
                        present = st.checkbox(f"{student_name}", key=f"{student_name}_{today_date}")
                        if present:
                            df.at[index, today_date] = "Present"
                        else:
                            df.at[index, today_date] = "Absent"

                    if st.button("Submit Attendance"):
                        df.to_csv(file_name, index=False)
                        st.success("Attendance submitted successfully!")

                def view_attendance():
                    st.header("View Attendance")
                    class_name = st.selectbox("Select Class", list(class_passwords.keys()))
                    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
                    file_name = os.path.join(CURRENT_DIR, f"{class_name}.csv")

                    try:
                        df = pd.read_csv(file_name)
                    except FileNotFoundError:
                        st.error(f"Error: File not found for {class_name} ({file_name})")
                        return

                    st.subheader(f"Attendance Records for {class_name}")
                    st.dataframe(df)

                    if st.button("Generate Attendance Chart"):
                        attendance_counts = df[today_date].value_counts()
                        plt.bar(attendance_counts.index, attendance_counts.values)
                        plt.title(f"Attendance Chart for {class_name} - {today_date}")
                        plt.xlabel("Status")
                        plt.ylabel("Count")
                        st.pyplot(plt)

                def add_class():
                    st.header("Add Class")
                    new_class_name = st.text_input("Enter New Class Name")
                    new_class_password = st.text_input("Enter New Class Password", type="password")
                    if st.button("Add Class"):
                        if new_class_name and new_class_password:
                            if new_class_name in class_passwords:
                                st.error("Class already exists!")
                            else:
                                class_passwords[new_class_name] = new_class_password
                                # Create a new CSV file for the class with empty attendance
                                CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
                                file_name = os.path.join(CURRENT_DIR, f"{new_class_name}.csv")
                                df = pd.DataFrame(columns=["Name", "Roll_No"])
                                df.to_csv(file_name, index=False)
                                st.success(f"Class '{new_class_name}' added successfully!")
                        else:
                            st.error("Please enter both class name and password.")

                def remove_class():
                    st.header("Remove Class")
                    class_to_remove = st.selectbox("Select Class to Remove", list(class_passwords.keys()))
                    if st.button("Remove Class"):
                        if class_to_remove in class_passwords:
                            del class_passwords[class_to_remove]
                            # Optionally, delete the corresponding CSV file
                            CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
                            file_name = os.path.join(CURRENT_DIR, f"{class_to_remove}.csv")
                            if os.path.exists(file_name):
                                os.remove(file_name)
                            st.success(f"Class '{class_to_remove}' removed successfully!")
                        else:
                            st.error("Class not found!")

                if side == "Take Attendance":
                    take_attendance()
                elif side == "View Attendance":
                    view_attendance()
                elif side == "Add Class":
                    add_class()
                elif side == "Remove Class":
                    remove_class()

    if imp=="Class Teacher":
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
                all_present=st.button("Mark All Present")
                if all_present:
                    df[today_date] = 'P'
                    df.to_csv(file_name, index=False)
                    st.success("All students marked as present!")
                    total_students = len(df)
                    present_count = df[today_date].value_counts().get('P', 0)
                    st.info(f"Total Students: {total_students}, Present: {present_count}")
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
                        for index, status in marked_attendance.items()
                        df.loc[index, today_date] = status
                    df.to_csv(file_name, index=False)
                    st.success(f"Attendance for {today_date} is submitted successfully!")
                    st.divider()
                    if st.button("Logout"):
                                st.session_state["authenticated"] = False
                                st.session_state["class_name"] = None
                                st.rerun()
                    
                    if __name__ == "__main__":
                          main()

