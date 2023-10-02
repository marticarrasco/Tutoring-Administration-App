import sqlite3
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from tkinter.simpledialog import Dialog
from tkcalendar import DateEntry  # Import the DateEntry widget
from datetime import date
from datetime import datetime
import pandas as pd


label_width = 20
entry_width = 30


def add_manual_session():
    student_name = cmb_students.get()
    selected_date = date_entry.get_date()  # Get the selected date
    session_date = selected_date.strftime('%Y-%m-%d')  # Format the date as YYYY-MM-DD
    try:
        hours = float(hours_entry.get())
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid number for hours.")
        return

    # Error handling for the inputs
    if not student_name or not session_date:
        messagebox.showerror("Error", "All fields are required.")
        return

    conn = sqlite3.connect('tutoring_app.db')
    cursor = conn.cursor()

    # Fetch the student_id using the student_name
    cursor.execute("SELECT id FROM Students WHERE name = ?", (student_name,))
    student_id = cursor.fetchone()
    
    
    if student_id:
        student_id = student_id[0]  # Extract the ID from the tuple
        cursor.execute("INSERT INTO TutoringSessions (student_id, date_of_session, hours_worked, is_paid) VALUES (?, ?, ?, 0)", (student_id, session_date, hours))
        conn.commit()
    else:
        messagebox.showerror("Error", "Student not found in the database.")
        
    conn.close()
    
    earnings = compute_total_earned_by_student()
    display_monthly_earnings()
    compute_total_earned_this_year()
    refresh_sessions_list()

def refresh_sessions_list():
    """Refresh the sessions treeview from the database."""
    for row in sessions_tree.get_children():
        sessions_tree.delete(row)
    
    conn = sqlite3.connect('tutoring_app.db')
    cursor = conn.cursor()
    
    # Fetch sessions with student names using JOIN operation
    query = """
    SELECT Students.name, TutoringSessions.date_of_session, TutoringSessions.hours_worked, TutoringSessions.is_paid
    FROM TutoringSessions
    JOIN Students ON TutoringSessions.student_id = Students.id
    ORDER BY TutoringSessions.date_of_session DESC
    """
    
    cursor.execute(query)
    sessions = cursor.fetchall()
    for session in sessions:
        student, session_date, hours, is_paid = session
        formatted_date = datetime.strptime(session_date, '%Y-%m-%d').strftime('%d-%m-%Y')
        paid_status = "Yes" if is_paid else "No"
        sessions_tree.insert("", tk.END, values=(student, formatted_date, hours, paid_status))


    conn.close()


def delete_session():
    """Delete the selected session from the database."""
    selected_items = sessions_tree.selection()
    if not selected_items:
        return

    student_name, session_date, _ = sessions_tree.item(selected_items[0])['values']
    session_date_db_format = datetime.strptime(session_date, '%d-%m-%Y').strftime('%Y-%m-%d')  # Convert to database format
    
    # Confirm deletion
    confirm = messagebox.askyesno("Delete Session", f"Are you sure you want to delete the session for {student_name} on {session_date}?")
    if not confirm:
        return

    conn = sqlite3.connect('tutoring_app.db')
    cursor = conn.cursor()

    # We use a JOIN operation to get the correct session to delete using both student_name and session_date
    query = """
    DELETE FROM TutoringSessions
    WHERE student_id = (SELECT id FROM Students WHERE name = ?)
    AND date_of_session = ?
    """
    
    cursor.execute(query, (student_name, session_date_db_format))
    conn.commit()
    conn.close()

    earnings = compute_total_earned_by_student()
    display_monthly_earnings()
    compute_total_earned_this_year()
    
    refresh_sessions_list()


def edit_session():
    """Edit the selected session's details."""
    selected_items = sessions_tree.selection()
    if not selected_items:
        return

    session_date, hours = sessions_tree.item(selected_items[0])['values'][1:]
    session_date_db_format = datetime.strptime(session_date, '%d-%m-%Y').strftime('%Y-%m-%d')  # Convert to database format
    d = EditSessionDialog(root, title="Edit Session", initial_data=(session_date, hours))
    
    # If the user provided new data, update the database
    if d.result:
        new_date, new_hours = d.result
        new_date_db_format = datetime.strptime(new_date, '%d-%m-%Y').strftime('%Y-%m-%d')  # Convert new date to database format
        try:
            new_hours = float(new_hours)
            student_name = sessions_tree.item(selected_items[0])['values'][0]
            conn = sqlite3.connect('tutoring_app.db')
            cursor = conn.cursor()
            
            query = """
            UPDATE TutoringSessions
            SET date_of_session = ?, hours_worked = ?
            WHERE student_id = (SELECT id FROM Students WHERE name = ?)
            AND date_of_session = ?
            """
            
            cursor.execute(query, (new_date_db_format, new_hours, student_name, session_date_db_format))
            conn.commit()
            conn.close()
            refresh_sessions_list()
            earnings = compute_total_earned_by_student()
            display_monthly_earnings()
            compute_total_earned_this_year()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for hours.")


def refresh_students_list():
    """Refresh the students combobox and treeview from the database."""
    for row in tree.get_children():
        tree.delete(row)
    cmb_students['values'] = []
    
    conn = sqlite3.connect('tutoring_app.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, price_per_hour FROM Students")
    students = cursor.fetchall()
    for student in students:
        tree.insert("", tk.END, values=student)
        current_values = list(cmb_students['values'])
        current_values.append(student[0])
        cmb_students['values'] = current_values
    conn.close()

def add_student():
    """Add a new student to the database."""
    name = name_entry.get()
    try:
        hourly_rate = float(hourly_rate_entry.get())
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid hourly rate.")
        return
    
    conn = sqlite3.connect('tutoring_app.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Students (name, price_per_hour) VALUES (?, ?)", (name, hourly_rate))
    conn.commit()
    conn.close()
    refresh_students_list()

def delete_student():
    """Delete the selected student from the database."""
    selected_items = tree.selection()
    if not selected_items:
        return

    student_name = tree.item(selected_items[0])['values'][0]
    conn = sqlite3.connect('tutoring_app.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Students WHERE name=?", (student_name,))
    conn.commit()
    conn.close()
    
    refresh_students_list()

def edit_student():
    """Edit the selected student's details."""
    selected_items = tree.selection()
    if not selected_items:
        return

    student_name, hourly_rate = tree.item(selected_items[0])['values']
    d = EditStudentDialog(root, title="Edit Student", initial_data=(student_name, hourly_rate))
    
    # If the user provided new data, update the database
    if d.result:
        new_name, new_hourly_rate = d.result
        try:
            new_hourly_rate = float(new_hourly_rate)
            conn = sqlite3.connect('tutoring_app.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE Students SET name=?, price_per_hour=? WHERE name=?", (new_name, new_hourly_rate, student_name))
            conn.commit()
            conn.close()
            refresh_students_list()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid hourly rate.")

def export_to_excel():
    conn = sqlite3.connect('tutoring_app.db')

    # Fetch students data
    students_df = pd.read_sql_query("SELECT * FROM Students", conn)
    
    # Fetch sessions data
    sessions_df = pd.read_sql_query("""
    SELECT Students.name, TutoringSessions.date_of_session, TutoringSessions.hours_worked
    FROM TutoringSessions
    JOIN Students ON TutoringSessions.student_id = Students.id
    """, conn)

    # Create a Pandas Excel writer using XlsxWriter as the engine
    with pd.ExcelWriter('tutoring_data.xlsx', engine='openpyxl') as writer:
        students_df.to_excel(writer, sheet_name='Students', index=False)
        sessions_df.to_excel(writer, sheet_name='Sessions', index=False)

    conn.close()
    messagebox.showinfo("Info", "Data exported to tutoring_data.xlsx successfully!")

class EditStudentDialog(Dialog):
    """A custom dialog for editing student details."""

    def body(self, master):
        ttk.Label(master, width=label_width, text="Name:").grid(row=0)
        ttk.Label(master, width=label_width, text="Hourly Rate:").grid(row=1)

        self.name_entry = ttk.Entry(master, width=entry_width)
        self.name_entry.grid(row=0, column=1)
        self.name_entry.insert(0, self.init_data[0])

        self.hourly_rate_entry = ttk.Entry(master, width=entry_width)
        self.hourly_rate_entry.grid(row=1, column=1)
        self.hourly_rate_entry.insert(0, self.init_data[1])

        return self.name_entry  # initial focus

    def apply(self):
        self.result = (self.name_entry.get(), self.hourly_rate_entry.get())

    def __init__(self, parent, title=None, initial_data=("", "")):
        self.init_data = initial_data
        super().__init__(parent, title)

class EditSessionDialog(Dialog):
    """A custom dialog for editing session details."""

    def body(self, master):
        ttk.Label(master, width=label_width, text="Date:").grid(row=0)
        ttk.Label(master, width=label_width, text="Hours:").grid(row=1)

        self.date_entry = ttk.Entry(master, width=entry_width)
        self.date_entry.grid(row=0, column=1)
        self.date_entry.insert(0, self.init_data[0])

        self.hours_entry = ttk.Entry(master, width=entry_width)
        self.hours_entry.grid(row=1, column=1)
        self.hours_entry.insert(0, self.init_data[1])

        return self.date_entry  # initial focus

    def apply(self):
        self.result = (self.date_entry.get(), self.hours_entry.get())

    def __init__(self, parent, title=None, initial_data=("", "")):
        self.init_data = initial_data
        super().__init__(parent, title)
    
# Main window setup
root = tk.Tk()
root.title("Tutoring Administration App")
#root.state('zoomed')

# Frame for manual session entry
frame_manual_entry = ttk.LabelFrame(root, text="Manual Session Entry", padding=(10, 5))
frame_manual_entry.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

# Widgets for manual session entry
lbl_students = ttk.Label(frame_manual_entry, width=label_width, text="Select Student:")
lbl_students.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

cmb_students = ttk.Combobox(frame_manual_entry, width=entry_width-2, state="readonly")
cmb_students.grid(row=0, column=1, padx=5, pady=5)

lbl_date = ttk.Label(frame_manual_entry, width=label_width, text="Date:")
lbl_date.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

date_entry = DateEntry(frame_manual_entry, date_pattern='dd-mm-y', background='darkblue', width=entry_width-2,
                       foreground='white', borderwidth=2, locale="en_US", year=date.today().year)
date_entry.grid(row=1, column=1, padx=5, pady=5)

lbl_hours = ttk.Label(frame_manual_entry, width=label_width, text="Hours:")
lbl_hours.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)

hours_entry = ttk.Entry(frame_manual_entry, width=entry_width+1)
hours_entry.grid(row=2, column=1, padx=5, pady=5)

btn_add_session = ttk.Button(frame_manual_entry, text="Add Session", command=add_manual_session)
btn_add_session.grid(row=3, column=0, columnspan=2, pady=10, sticky=tk.W)

# Frame for displaying sessions
frame_sessions = ttk.LabelFrame(root, text="Sessions", padding=(10, 5))
frame_sessions.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

# Update sessions_tree to include a new column for payment status
sessions_tree = ttk.Treeview(frame_sessions, columns=('Student', 'Date', 'Hours', 'Paid'), show='headings')
sessions_tree.heading('Student', text='Student')
sessions_tree.heading('Date', text='Date')
sessions_tree.heading('Hours', text='Hours')
sessions_tree.heading('Paid', text='Paid')  # New heading for payment status
sessions_tree.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)


refresh_sessions_list()

def mark_as_paid():
    selected_items = sessions_tree.selection()
    if not selected_items:
        return
    student_name, session_date, _, _ = sessions_tree.item(selected_items[0])['values']
    session_date_db_format = datetime.strptime(session_date, '%d-%m-%Y').strftime('%Y-%m-%d')  # Convert to database format
    
    conn = sqlite3.connect('tutoring_app.db')
    cursor = conn.cursor()
    
    cursor.execute("UPDATE TutoringSessions SET is_paid=1 WHERE student_id = (SELECT id FROM Students WHERE name = ?) AND date_of_session = ?", (student_name, session_date_db_format))
    conn.commit()
    conn.close()
    
    refresh_sessions_list()

def mark_as_unpaid():
    # similar to mark_as_paid, but set is_paid=0
    selected_items = sessions_tree.selection()
    if not selected_items:
        return
    student_name, session_date, _, _ = sessions_tree.item(selected_items[0])['values']
    session_date_db_format = datetime.strptime(session_date, '%d-%m-%Y').strftime('%Y-%m-%d')  # Convert to database format
    
    conn = sqlite3.connect('tutoring_app.db')
    cursor = conn.cursor()
    
    cursor.execute("UPDATE TutoringSessions SET is_paid=0 WHERE student_id = (SELECT id FROM Students WHERE name = ?) AND date_of_session = ?", (student_name, session_date_db_format))
    conn.commit()
    conn.close()
    
    refresh_sessions_list()

# Add buttons for marking sessions as paid or unpaid
btn_mark_paid = ttk.Button(frame_sessions, text="Mark as Paid", command=mark_as_paid)
btn_mark_paid.pack(pady=5, side=tk.LEFT, padx=5)

btn_mark_unpaid = ttk.Button(frame_sessions, text="Mark as Unpaid", command=mark_as_unpaid)
btn_mark_unpaid.pack(pady=5, side=tk.LEFT, padx=5)


btn_edit_session = ttk.Button(frame_sessions, text="Edit Session", command=edit_session)
btn_edit_session.pack(pady=5, side=tk.LEFT, padx=5)

btn_delete_session = ttk.Button(frame_sessions, text="Delete Session", command=delete_session)
btn_delete_session.pack(pady=5, side=tk.LEFT, padx=5)

# Frame for CRUD operations on students
frame_crud_students = ttk.LabelFrame(root, text="Manage Students", padding=(10, 5))
frame_crud_students.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")

# Widgets for CRUD operations on students
lbl_name = ttk.Label(frame_crud_students, width=label_width, text="Name:")
lbl_name.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

name_entry = ttk.Entry(frame_crud_students, width=entry_width)
name_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

lbl_hourly_rate = ttk.Label(frame_crud_students, width=label_width, text="Hourly Rate:")
lbl_hourly_rate.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

hourly_rate_entry = ttk.Entry(frame_crud_students, width=entry_width)
hourly_rate_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

btn_add_student = ttk.Button(frame_crud_students, text="Add Student", command=add_student)
btn_add_student.grid(row=2, column=0, columnspan=2, pady=10, sticky=tk.W)

tree = ttk.Treeview(frame_crud_students, columns=('Name', 'Hourly Rate'), show='headings')
tree.heading('Name', text='Name')
tree.heading('Hourly Rate', text='Hourly Rate')
tree.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
frame_crud_students.grid_columnconfigure(1, weight=1)  # This allows the Treeview to expand horizontally
frame_crud_students.grid_rowconfigure(4, weight=1)  # This allows the Treeview to expand vertically

refresh_students_list()

btn_edit_student = ttk.Button(frame_crud_students, text="Edit Student", command=edit_student)
btn_edit_student.grid(row=5, column=0, padx=5, pady=5, sticky='ew')

btn_delete_student = ttk.Button(frame_crud_students, text="Delete Student", command=delete_student)
btn_delete_student.grid(row=5, column=1, padx=5, pady=5, sticky='ew')

# Create a statistics frame to the right
stats_frame = ttk.LabelFrame(root, text="Statistics", padding=(10, 5))
stats_frame.grid(row=0, column=1, rowspan=3, padx=10, pady=5, sticky="nsew")

inner_stats_frame = ttk.Frame(stats_frame)
inner_stats_frame.pack(fill=tk.BOTH, expand=True)


export_button = ttk.Button(stats_frame, text="Export to Excel", command=export_to_excel)
export_button.pack(side=tk.BOTTOM, pady=10, fill=tk.X)


def compute_total_earned_by_student():
    conn = sqlite3.connect('tutoring_app.db')
    cursor = conn.cursor()

    # Compute total money earned by each student using JOIN operation
    query = """
    SELECT Students.name, SUM(TutoringSessions.hours_worked * Students.price_per_hour)
    FROM Students
    JOIN TutoringSessions ON TutoringSessions.student_id = Students.id
    GROUP BY Students.name
    """
    
    cursor.execute(query)
    earnings = cursor.fetchall()
    
    # Display earnings in stats_frame
    for idx, (student, amount) in enumerate(earnings):
        ttk.Label(inner_stats_frame, text=f"{student}: ${amount:.2f}").grid(row=idx, column=0, padx=5, pady=5, sticky=tk.W)

    
    conn.close()
    return earnings

earnings = compute_total_earned_by_student()


def display_monthly_earnings():
    conn = sqlite3.connect('tutoring_app.db')
    cursor = conn.cursor()

    current_month = datetime.now().month
    current_year = datetime.now().year
    
    # Compute total money earned for the month using JOIN operation
    query = """
    SELECT SUM(TutoringSessions.hours_worked * Students.price_per_hour)
    FROM Students
    JOIN TutoringSessions ON TutoringSessions.student_id = Students.id
    WHERE strftime('%m', date_of_session) = ? AND strftime('%Y', date_of_session) = ?
    """
    
    cursor.execute(query, (str(current_month).zfill(2), str(current_year)))
    total = cursor.fetchone()[0]
    
    # Display total earnings for the month in stats_frame
    ttk.Label(inner_stats_frame, text=f"Total for {current_month}/{current_year}: ${total if total else 0:.2f}").grid(row=len(earnings), column=0, padx=5, pady=5, sticky=tk.W)
    
    conn.close()

display_monthly_earnings()

def compute_monthly_earnings():
    conn = sqlite3.connect('tutoring_app.db')
    cursor = conn.cursor()

    # Compute earnings for each month where work was recorded
    query = """
    SELECT strftime('%m-%Y', date_of_session) as month_year, SUM(TutoringSessions.hours_worked * Students.price_per_hour)
    FROM Students
    JOIN TutoringSessions ON TutoringSessions.student_id = Students.id
    GROUP BY month_year
    ORDER BY datetime(date_of_session)
    """

    cursor.execute(query)
    monthly_earnings = cursor.fetchall()
    
    conn.close()
    print(monthly_earnings)
    return monthly_earnings

def display_monthly_earnings():
    earnings = compute_monthly_earnings()
    
    # Assuming you have a label or some widget where you display statistics
    for idx, (month_year, amount) in enumerate(earnings, start=len(earnings) + 3):  # Adjust the start index accordingly
        ttk.Label(inner_stats_frame, text=f"{month_year}: ${amount:.2f}").grid(row=idx, column=0, padx=5, pady=5, sticky=tk.W)

def compute_total_earned_this_year():
    conn = sqlite3.connect('tutoring_app.db')
    cursor = conn.cursor()

    current_year = datetime.now().year
    
    # Compute total money earned for the year using JOIN operation
    query = """
    SELECT SUM(TutoringSessions.hours_worked * Students.price_per_hour)
    FROM Students
    JOIN TutoringSessions ON TutoringSessions.student_id = Students.id
    WHERE strftime('%Y', date_of_session) = ?
    """
    
    cursor.execute(query, (str(current_year),))
    total = cursor.fetchone()[0]
    
    # Display total earnings for the year in stats_frame
    ttk.Label(inner_stats_frame, text=f"Total for {current_year}: ${total if total else 0:.2f}").grid(row=len(earnings) + 1, column=0, padx=5, pady=5, sticky=tk.W)
    
    conn.close()

compute_total_earned_this_year()

def compute_highest_earning_month():
    try:
        conn = sqlite3.connect('tutoring_app.db')
        cursor = conn.cursor()

        current_year = datetime.now().year
        
        # Find the month with highest earnings for the year
        query = """
        SELECT strftime('%m', date_of_session), SUM(TutoringSessions.hours_worked * Students.price_per_hour)
        FROM Students
        JOIN TutoringSessions ON TutoringSessions.student_id = Students.id
        WHERE strftime('%Y', date_of_session) = ?
        GROUP BY strftime('%m', date_of_session)
        ORDER BY SUM(TutoringSessions.hours_worked * Students.price_per_hour) DESC
        LIMIT 1
        """
        
        cursor.execute(query, (str(current_year),))
        month, total = cursor.fetchone()
        
        # Display month with highest earnings for the year in stats_frame
        #   ttk.Label(inner_stats_frame, text=f"Highest in {month}/{current_year}: ${total if total else 0:.2f}").grid(row=len(earnings) + 2, column=0, padx=5, pady=5, sticky=tk.W)
        conn.close()
    except:
        pass

compute_highest_earning_month()
display_monthly_earnings()


refresh_sessions_list()

root.mainloop()
