import streamlit as st
import pandas as pd
import os
import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

admin_password = "admin123"

class_passwords = {
    'class1': 'ABCD',
    'class2': 'EFGH'
}

today_date = datetime.date.today().strftime("%Y-%m-%d")
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


def clear_widget_cache():
    """Removes all cached checkbox widget states from session memory."""
    for key in list(st.session_state.keys()):
        if key.startswith("check_"):
            del st.session_state[key]



def take_attendance_admin():
    st.header("Admin - Take Attendance")
    class_name = st.selectbox(
        "Select Class", 
        list(class_passwords.keys()), 
        key="admin_take_class_select",
        on_change=clear_widget_cache
    )
    file_name = os.path.join(CURRENT_DIR, f"{class_name}.csv")

    if not os.path.exists(file_name):
        st.warning(f"File not found for {class_name}.")
        if st.button(f"Create Starter File for {class_name}", key=f"create_admin_{class_name}"):
            sample_df = pd.DataFrame({
                "Roll_No": [101, 102, 103],
                "Name": [f"{class_name}_Student_1", f"{class_name}_Student_2", f"{class_name}_Student_3"]
            })
            sample_df.to_csv(file_name, index=False)
            st.rerun()
        return

    df = pd.read_csv(file_name)
    st.subheader(f"Mark Attendance for {class_name} - {today_date}")

    if today_date not in df.columns:
        df[today_date] = "A"

    
    total_students = len(df)
    present_count = int((df[today_date].astype(str).str.strip().str.upper() == 'P').sum())
    absent_count = total_students - present_count
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Students", total_students)
    col2.metric("Present", present_count)
    col3.metric("Absent", absent_count)


    b1, b2 = st.columns(2)
    if b1.button(" Mark All Present", key=f"admin_all_p_{class_name}"):
        df[today_date] = 'P'
        df.to_csv(file_name, index=False)
        for index, row in df.iterrows():
            roll_no = row.get('Roll_No', index + 1)
            st.session_state[f"check_admin_{class_name}_{roll_no}_{today_date}"] = True
        st.rerun()

    if b2.button(" Mark All Absent", key=f"admin_all_a_{class_name}"):
        df[today_date] = 'A'
        df.to_csv(file_name, index=False)
        for index, row in df.iterrows():
            roll_no = row.get('Roll_No', index + 1)
            st.session_state[f"check_admin_{class_name}_{roll_no}_{today_date}"] = False
        st.rerun()

    
    with st.form(f"admin_attendance_form_{class_name}"):
        marked_attendance = {}
        st.write("**Student Checklist:**")

        for index, row in df.iterrows():
            student_name = row['Name']
            roll_no = row.get('Roll_No', index + 1)
            checkbox_key = f"check_admin_{class_name}_{roll_no}_{today_date}"

            if checkbox_key not in st.session_state:
                st.session_state[checkbox_key] = (str(row[today_date]).strip().upper() == 'P')

            is_present = st.checkbox(
                f"**{roll_no}** - {student_name}", 
                key=checkbox_key
            )
            marked_attendance[index] = 'P' if is_present else 'A'

        submit_btn = st.form_submit_button("Submit Attendance")
        if submit_btn:
            for index, status in marked_attendance.items():
                df.loc[index, today_date] = status
            df.to_csv(file_name, index=False)
            st.success(f"Attendance for {class_name} saved successfully!")
            st.rerun()


def view_attendance_admin():
    st.header("Admin - View Attendance")
    class_name = st.selectbox("Select Class", list(class_passwords.keys()), key="admin_view_class_select")
    file_name = os.path.join(CURRENT_DIR, f"{class_name}.csv")

    if not os.path.exists(file_name):
        st.error(f"No records found for {class_name}.")
        return

    df = pd.read_csv(file_name)
    st.subheader(f"Records for {class_name}")
    st.dataframe(df, use_container_width=True)

    if today_date in df.columns:
        if st.button("Generate Today's Chart", key=f"chart_btn_{class_name}"):
            counts = df[today_date].map({'P': 'Present', 'A': 'Absent'}).value_counts()
            fig, ax = plt.subplots(figsize=(5, 3))
            ax.bar(counts.index, counts.values, color=['#2ecc71', '#e74c3c'])
            ax.set_title(f"Attendance - {class_name} ({today_date})")
            ax.set_xlabel("Status")
            ax.set_ylabel("Students")
            st.pyplot(fig)
            plt.close(fig)
    else:
        st.info("No attendance recorded for today yet.")


def add_class_admin():
    st.header("Add New Class")
    new_class_name = st.text_input("Enter New Class Name (e.g., class3)")
    new_class_password = st.text_input("Enter New Class Password", type="password")

    if st.button("Add Class"):
        if new_class_name and new_class_password:
            if new_class_name in class_passwords:
                st.error("Class already exists!")
            else:
                class_passwords[new_class_name] = new_class_password
                file_name = os.path.join(CURRENT_DIR, f"{new_class_name}.csv")
                df = pd.DataFrame(columns=["Roll_No", "Name"])
                df.to_csv(file_name, index=False)
                st.success(f"Class '{new_class_name}' added successfully!")
        else:
            st.error("Please enter both class name and password.")


def remove_class_admin():
    st.header("Remove Class")
    class_to_remove = st.selectbox("Select Class to Remove", list(class_passwords.keys()))

    if st.button("Remove Class"):
        if class_to_remove in class_passwords:
            del class_passwords[class_to_remove]
            file_name = os.path.join(CURRENT_DIR, f"{class_to_remove}.csv")
            if os.path.exists(file_name):
                os.remove(file_name)
            st.success(f"Class '{class_to_remove}' removed successfully!")
            st.rerun()

def main():
    if "admin_authenticated" not in st.session_state:
        st.session_state["admin_authenticated"] = False
    if "teacher_authenticated" not in st.session_state:
        st.session_state["teacher_authenticated"] = False
    if "class_name" not in st.session_state:
        st.session_state["class_name"] = None

    st.sidebar.title("Navigation")
    portal = st.sidebar.radio("Select Portal", ["Class Teacher Portal", "Admin Portal"])

    
    if portal == "Class Teacher Portal":
        if not st.session_state["teacher_authenticated"]:
            st.header("Teacher Login")
            with st.form("teacher_login_form"):
                class_input = st.selectbox("Select Your Class", list(class_passwords.keys()))
                passw_input = st.text_input("Enter Password", type="password")
                submit = st.form_submit_button("Login")

                if submit:
                    if passw_input == class_passwords.get(class_input):
                        clear_widget_cache()
                        st.session_state["teacher_authenticated"] = True
                        st.session_state["class_name"] = class_input
                        st.success(f"Logged into {class_input}!")
                        st.rerun()
                    else:
                        st.error("Invalid class or password")
        else:
            class_name = st.session_state["class_name"]
            st.header(f"Attendance Dashboard - {class_name}")

            file_name = os.path.join(CURRENT_DIR, f"{class_name}.csv")

            if not os.path.exists(file_name):
                st.warning(f"File not found for {class_name}.")
                if st.button(f"Create Starter File for {class_name}", key=f"create_t_{class_name}"):
                    sample_df = pd.DataFrame({
                        "Roll_No": [101, 102, 103],
                        "Name": ["Aarav Kumar", "Ananya Reddy", "Rohan Verma"]
                    })
                    sample_df.to_csv(file_name, index=False)
                    st.rerun()
                return

            df = pd.read_csv(file_name)
            st.subheader(f"Mark Attendance - {today_date}")

            if today_date not in df.columns:
                df[today_date] = 'A'

        
            total_students = len(df)
            present_count = int((df[today_date].astype(str).str.strip().str.upper() == 'P').sum())
            absent_count = total_students - present_count
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Students", total_students)
            c2.metric("Present", present_count)
            c3.metric("Absent", absent_count)

            
            b1, b2 = st.columns(2)
            if b1.button(" Mark All Present", key=f"t_all_p_{class_name}"):
                df[today_date] = 'P'
                df.to_csv(file_name, index=False)
                for index, row in df.iterrows():
                    roll_no = row.get('Roll_No', index + 1)
                    st.session_state[f"check_teacher_{class_name}_{roll_no}_{today_date}"] = True
                st.rerun()

            if b2.button(" Mark All Absent", key=f"t_all_a_{class_name}"):
                df[today_date] = 'A'
                df.to_csv(file_name, index=False)
                for index, row in df.iterrows():
                    roll_no = row.get('Roll_No', index + 1)
                    st.session_state[f"check_teacher_{class_name}_{roll_no}_{today_date}"] = False
                st.rerun()

            
            with st.form(f"teacher_attendance_form_{class_name}"):
                marked_attendance = {}
                st.write("**Student Checklist:**")

                for index, row in df.iterrows():
                    student_name = row['Name']
                    roll_no = row.get('Roll_No', index + 1)
                    checkbox_key = f"check_teacher_{class_name}_{roll_no}_{today_date}"

                    if checkbox_key not in st.session_state:
                        st.session_state[checkbox_key] = (str(row[today_date]).strip().upper() == 'P')

                    checkbox_state = st.checkbox(
                        f"**{roll_no}** - {student_name}",
                        key=checkbox_key
                    )
                    marked_attendance[index] = 'P' if checkbox_state else 'A'

                submitted = st.form_submit_button("Submit Attendance")
                if submitted:
                    for index, status in marked_attendance.items():
                        df.loc[index, today_date] = status
                    df.to_csv(file_name, index=False)
                    st.success(f"Attendance for {today_date} saved successfully!")
                    st.rerun()

            
            st.divider()
            with st.expander("View Attendance Summary Table"):
                summary_df = df[['Roll_No', 'Name', today_date]].copy()
                summary_df['Status'] = summary_df[today_date].apply(lambda x: 'Present' if str(x).upper() == 'P' else 'Absent')
                st.dataframe(summary_df[['Roll_No', 'Name', 'Status']], use_container_width=True)

            if st.button("Logout Teacher"):
                clear_widget_cache()
                st.session_state["teacher_authenticated"] = False
                st.session_state["class_name"] = None
                st.rerun()

    
    elif portal == "Admin Portal":
        if not st.session_state["admin_authenticated"]:
            st.header("Admin Login")
            with st.form("admin_login_form"):
                password = st.text_input("Enter Admin Password", type="password")
                submit = st.form_submit_button("Login")
                if submit:
                    if password == admin_password:
                        clear_widget_cache()
                        st.session_state["admin_authenticated"] = True
                        st.success("Admin Login Successful!")
                        st.rerun()
                    else:
                        st.error("Invalid Admin Password")
        else:
            st.sidebar.divider()
            st.sidebar.subheader("Admin Menu")
            side = st.sidebar.radio("Actions", ["Take Attendance", "View Attendance", "Add Class", "Remove Class"])
            
            if st.sidebar.button("Logout Admin"):
                clear_widget_cache()
                st.session_state["admin_authenticated"] = False
                st.rerun()

            if side == "Take Attendance":
                take_attendance_admin()
            elif side == "View Attendance":
                view_attendance_admin()
            elif side == "Add Class":
                add_class_admin()
            elif side == "Remove Class":
                remove_class_admin()


if __name__ == "__main__":
    main()
