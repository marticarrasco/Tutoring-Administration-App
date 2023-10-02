# 🎓 **Tutoring Administration App** 🎓

Easily manage your tutoring sessions with this intuitive, GUI-based application built with Python's `tkinter`.

![Tutoring App Screenshot](Screenshot.png)

## ✨ **Features** 
- 📚 **Student Management**: Add, edit, or delete student details with ease.
- ⏳ **Session Mastery**: Log tutoring sessions manually, track whether they've been paid for, and keep them organized.
- 💰 **Earnings Insights**: Track your earnings per student and get monthly and yearly summaries.
- 📊 **Excel Exports**: Need a report? Export your data to an Excel file in seconds!
- 🔄 **Database Migrations**: Easily migrate your existing database to accommodate new features.

## 🚀 **Getting Started**

### **Prerequisites**
Ensure you have the following installed:
- Python 3.x
- SQLite3

### **Dependencies**
Install the necessary Python packages:
'''
pip install pandas openpyxl tkcalendar
'''

### **Initialization**
First things first, set up your database:

'''
python databaseInitializer.py
'''
### **Migration (if you're updating from a previous version)**
To incorporate the new `is_paid` feature into your existing database, run:

'''
python migrationProgramme.py
'''

### **Launch the App**
Now, you're all set! Launch the app and get started:
'''
python app.py
'''

## 📘 **How to Use**

1. **Manage Students**: Set up your students and their hourly rates.
2. **Log Sessions**: Add details for each tutoring session, and easily track if they've been paid for.
3. **View & Edit**: Browse sessions, make edits, or remove them.
4. **Track Earnings**: Always know what you've earned and which sessions are still pending payment.
5. **Export Data**: Create Excel reports anytime you need.

## 📜 **License**
This project is licensed under the MIT License.
