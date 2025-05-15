import tkinter as tk
from tkinter import ttk
import sqlite3

def setup_databases():
    """
    Function sets up the job and payments database files, if they do not exist.
    """

    conn   = sqlite3.connect("databases/jobs.db")
    cursor = conn.cursor()

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS jobs (
            job_id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_name TEXT,
            client_name TEXT,
            quote_value REAL,
            material_cost REAL,
            labour_cost REAL,
            job_status TEXT,
            notes TEXT
        )
        '''
        )

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS payments (
            payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER,
            payment_amount REAL,
            payment_date TEXT
        )
        '''
    )

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS costs (
            cost_id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER,
            category TEXT,
            amount REAL,
            date TEXT
        )
        '''
    )

    conn.commit()
    conn.close()

def new_job():
    """
    Creates a new window for submitting new job details.
    """

    def save_job():
        """
        When submit button is pressed, save new job information to job database.
        """
        conn   = sqlite3.connect("databases/jobs.db")
        cursor = conn.cursor()

        values = [] 
        for ifield in range(len(field_names)):
            values.append(entry_fields[ifield].get())
        
        cursor.execute(
            '''
            INSERT INTO jobs (job_name, client_name, quote_value, material_cost, labour_cost, job_status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?) 
            ''', (values[0], values[1], values[2], values[3], values[4], values[5], values[6])
        )

        conn.commit()
        conn.close()

        job_window.destroy()

    job_window = tk.Toplevel(root)
    job_window.title("New Job")

    field_names  = ["Job Name", "Client Name", "Quote", "Materials Cost", "Labour Cost", "Job status", "Notes"]
    entry_fields = [] 
    for ifield in range(len(field_names)):
        tk.Label(job_window, text = f"{field_names[ifield]}").grid(row=0, column=ifield)
        entry = tk.Entry(job_window)
        entry_fields.append(entry)
        entry.grid(row=1, column=ifield)

        if ifield >= 3 and ifield < 5:
            entry.insert(0, "0")
        if ifield == 5:
            entry.insert(0, "Unpaid")

    
    tk.Button(job_window, text="Submit", width=20, command=save_job).grid(row=3, column=len(field_names)-1)

def edit_job():
    """
    Creates a window for user to select a previously added job from drop down. 
    Once selected, can add a payment tied to that job, mark as complete or edit costs.
    Updates datebase for that job once done.
    """

    def show_job_details(event):
        """
        After job selected from dropdown list, display the job attributes.
        """
        # find all the jobs in the database
        conn   = sqlite3.connect("databases/jobs.db")
        cursor = conn.cursor()
        selected = combobox.get()
        
        # use dictionary to extract the job ID number and then populate fields for editing
        # with selected job based on info in the database
        job_id = info_dict[selected]

        # populate the entries
        cursor.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id))
        data = cursor.fetchone()
        print(data)

        data_strings[0].set(data[1])
        data_strings[1].set(data[2])
        data_strings[2].set(data[3])
        data_strings[4].set(data[4])
        data_strings[5].set(data[5])
        data_strings[6].set(f"{float(data[4])+float(data[5])}")
        data_strings[7].set(f"{float(data[3])-float(data_strings[6].get())}") # profit / loss
        data_strings[8].set(data[6]) # status
        data_strings[9].set(data[7])

        if float(data_strings[7].get()) <= 0:
            entry_wigits[7].config(bg="red")
        else:
            entry_wigits[7].config(bg="green")

        if data_strings[8].get() == "Unpaid":
            entry_wigits[8].config(bg="red")
        else:
            entry_wigits[8].config(bg="green")
        
        # now obtain all the payments associated with this job ID in the payments table
        cursor.execute("SELECT SUM(payment_amount) FROM payments WHERE job_id = ?", (job_id))
        total_paid = cursor.fetchone()
        print(total_paid)

        conn.close()

        # activate the add cost and add payment buttons
        add_payment.config(state="normal")
        add_cost.config(state="normal")

    def add_cost():
        pass
    def add_payment():
        """
        Add a payment to payments table and update the job display with new payment information.
        """

        def save_payment():
            pass

        # find the selected job
        conn   = sqlite3.connect("databases/jobs.db")
        cursor = conn.cursor()
        selected = combobox.get()
        
        # use dictionary to extract the job ID number and then populate fields for editing
        # with selected job based on info in the database
        job_id = info_dict[selected]
        cursor.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id))
        data = cursor.fetchone() 
        payment_window = tk.Toplevel(edit_window)
        payment_window.title(f"New Payment - {data[1]}")

        labels  = ["Payment Amount (£)", "Date (dd-mm-yy)"]
        entries = []
        for i in range(len(labels)):
            tk.Label(payment_window, text=f"{labels[i]}").grid(row=i, column=0)
            entry = tk.Entry(payment_window)
            entries.append(entries)
            entry.grid(row=i, column=1)
        
        # submit button to save it
        tk.Button(payment_window, text="Submit", command=save_payment).grid(row=len(labels), column=0, columnspan=2, sticky="ew")
            

    edit_window = tk.Toplevel(root)
    edit_window.title("Edit Job")

    # find all the jobs in the database
    conn   = sqlite3.connect("databases/jobs.db")
    cursor = conn.cursor()

    cursor.execute(
        '''
        SELECT * FROM jobs
        '''
    )
    jobs      = cursor.fetchall()
    job_names = [f"{job[0]} - {job[1]}" for job in jobs]

    # now make a dictionary tying the job names in the combo box to the job IDs in the database
    info_dict = {f"{job[0]} - {job[1]}" : f"{job[0]}" for job in jobs}

    # dropdown to select job to edit
    tk.Label(edit_window, text="Select Job").grid(row=0, column=0)
    selected_job = tk.StringVar()
    combobox     = ttk.Combobox(edit_window, textvariable=selected_job, values=job_names)
    combobox.grid(row=0, column=1)
    combobox.bind("<<ComboboxSelected>>", show_job_details)

    # display the selected information
    fields = ["Job Name", "Client Name", "Quote", "Amount Paid", "Materials Cost", "Labour Cost", "Total Cost", "Predicted Profit/Loss", "Status", "Notes"]
    data_strings = [tk.StringVar() for _ in fields]
    entry_wigits = []
    for i in range(len(fields)):
        tk.Label(edit_window, text = f"{fields[i]}", width=20).grid(row=1, column=i)
        entry  = tk.Label(edit_window, textvariable = data_strings[i], relief="sunken", bg="grey", fg="black", anchor="w", width=20)
        entry.grid(row=2, column=i)
        entry_wigits.append(entry)

    # add two deactivated buttons next to the dropdown box to ADD PAYMENT and ADD COST for a job
    add_payment = tk.Button(edit_window, text="Add Payment", width=20, command=add_payment, state="disabled")
    add_cost    = tk.Button(edit_window, text="Add Cost", width=20, command=add_cost, state="disabled")
    add_payment.grid(row=0, column=2)
    add_cost.grid(row=0, column=3)

    
setup_databases()

root = tk.Tk()
root.title("Dashboard")

tk.Button(root, text="New Job", width=20, command=new_job).pack(pady=10)
tk.Button(root, text="Edit Job", width=20, command=edit_job).pack(pady=10)


root.mainloop()
