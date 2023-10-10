# Task_Manager_1.py
from datetime import datetime
import tkinter as tk
from tkinter import ttk

from Task_CRUD_Model import Task_CRUD_Model

class Task_Manager_1:
    '''
    This application presents a Simple Task Manager which uses

    a Task CRUD Model to add, update or delete a task to/from a list, file or a database
    and print the results in a list on the screen with a scrolling bar.

    This model integrate an Object Observer mechanism and can be shared between different views

    PS : TK imposes to use only one single window so the view is now in a frame to share the window
    '''

    def __init__(self, window, task_model):

        ### Modified to share the model between views
        self.window = window
        self.tasks = task_model
        self.tasks.register_observer(self)  # Ask to be notified on modification
        self.notify_refresh = False
        ###

        ### Modified to share the model between views
        # TK imposes a single root window (Tk instance), the display has thus been modified to appear in a frame
        self.tasks_manager_1_frame = tk.LabelFrame(self.window, text="Task Manager 1", labelanchor='nw')
        self.tasks_manager_1_frame.pack(side="left", fill=tk.BOTH, expand=True)
        ###

        # No selected item per default
        self.selected_item = None

        self._create_the_tasks_main_frame()
        self._create_the_new_task_frame()

    def _create_the_tasks_main_frame(self):
        # Create a main frame for the labels and the scrolling bar
        self.tasks_main_frame = tk.Frame(self.tasks_manager_1_frame, bg="blue")
        self.tasks_main_frame.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        # Define a table with 2 columns and a header
        self.tree = ttk.Treeview(self.tasks_main_frame, columns=("Column 1", "Column 2"), show="headings")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Define a scrollbar attached to the tasks_manager_1_frame based on the TreeView height
        scrollbar = tk.Scrollbar(self.tasks_main_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Config the cursor of the scrollbar to be sized/placed according to the height/position of the Treeview
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Define the header of the Columns
        self.tree.heading("Column 1", text="Title")
        self.tree.heading("Column 2", text="Priority")

        # Bind a function to the select event
        self.tree.bind("<<TreeviewSelect>>", self.on_treeview_select)

        # Get the tasks from the model
        self.update_tasks_from_model()

    def update_tasks_from_model(self):
        # Clear all the actual lines of the tree
        self.tree.delete(*self.tree.get_children())

        # Insert the tasks from the model
        for task in self.tasks.read():
            self.tree.insert("", tk.END, values=task, tags=task)  # 'tags' converts the values to compatible str

    def refresh(self, *args, **kwargs):
        self.update_tasks_from_model()
        self.clear_selection_and_input_fields()

        ### Modified to share the model between views
        self.notify_refresh = False
        ###

    ### Modified to share the model between views
    def notify(self, *args, **kwargs):
        """ Called when the file/db is modified by another process and when the data is modified by another view """
        if self.notify_refresh is False:
            self.notify_refresh = True
            # The 'after' method from Tkinter library is employed to initiate the refresh within the main thread.
            # This setup is particularly requested when the system called this method to notify the application
            # about an external modification, especially when dealing with SQLITE3 files.
            self.window.after(0, self.refresh)
    ###

    def on_treeview_select(self, event):
        # Get the selected item line
        selected_items = self.tree.selection()  # tuple(item,...)
        if len(selected_items) == 1:  # unique selection or remove selections
            self.selected_item = selected_items[0]
            # Get the 'values' of the selected item
            values = self.tree.item(self.selected_item, "tags")
            if values:
                self.entry_var.set(values[0])
                self.priority_var.set(values[1])
                self.add_update_button.config(text="Update")
                self.delete_button.config(state="active")
        else:
            self.clear_selection_and_input_fields()

    def clear_selection_and_input_fields(self):
        if self.tree:
            for selected_item in self.tree.selection():
                self.tree.selection_remove(selected_item)
        self.selected_item = None
        self.entry_var.set("Enter a new task here")
        self.priority_var.set("5")
        self.add_update_button.config(text="Add")
        self.delete_button.config(state="disabled")

    def handle_add_update_task(self):
        if len(self.entry_var.get()) > 0:
            if self.add_update_button['text'] == "Add":
                self.tasks.create(self.entry_var.get(), int(self.priority_var.get()))
            else:  # Update
                values_item = self.tree.item(self.selected_item, "tags")
                for idx, task_tuple in enumerate(self.tasks.read()):
                    if task_tuple[0] == values_item[0] \
                            and task_tuple[1] == int(values_item[1]) \
                            and task_tuple[2] == datetime.strptime(values_item[2], '%Y-%m-%d %H:%M:%S.%f') :
                        self.tasks.update(idx, self.entry_var.get(), int(self.priority_var.get()))
                        break

            ### Modified to share the model between views
            # self.refresh()    # no more useful because call notify at each modification
            ###

    def handle_delete_task(self):
        values_item = self.tree.item(self.selected_item, "tags")
        for idx, task_tuple in enumerate(self.tasks.read()):
            if task_tuple[0] == values_item[0] \
                    and task_tuple[1] == int(values_item[1]) \
                    and task_tuple[2] == datetime.strptime(values_item[2], '%Y-%m-%d %H:%M:%S.%f'):
                self.tasks.delete(idx)
                break

        ### Modified to share the model between views
        # self.refresh()    # no more useful because call notify at each modification
        ###

    def _create_the_new_task_frame(self):
        self.new_task_frame = tk.Frame(self.tasks_manager_1_frame, bg="white")
        self.new_task_frame.pack(side=tk.BOTTOM, padx=5, pady=(0, 5), fill=tk.X, expand=True)

        self.entry_var = tk.StringVar(self.new_task_frame)
        self.priority_var = tk.StringVar(self.new_task_frame)

        # Title Entry
        title_label = tk.Label(self.new_task_frame, text="Title:")
        title_entry = tk.Entry(self.new_task_frame, textvariable=self.entry_var)

        # Priority Dropdown Menu
        priority_label = tk.Label(self.new_task_frame, text="Priority:")
        priority_menu = tk.OptionMenu(self.new_task_frame, self.priority_var, "1", "2", "3", "4", "5")

        # Add Button by default, Update Button if a task is selected
        self.add_update_button = tk.Button(self.new_task_frame, text="Add",
                                           command=self.handle_add_update_task)

        # Delete Button activated if a task is selected
        self.delete_button = tk.Button(self.new_task_frame, text="Delete",
                                       command=self.handle_delete_task, state="disabled")

        # Clear all selections and init the fields to default values
        self.clear_selection_and_input_fields()

        # Grid the frame
        title_label.grid(row=0, column=0, padx=5, pady=5)
        title_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        priority_label.grid(row=0, column=2, padx=10, pady=5)
        priority_menu.grid(row=0, column=3, padx=5, pady=5)
        self.add_update_button.grid(row=0, column=4, padx=5, pady=5)
        self.delete_button.grid(row=0, column=5, padx=5, pady=5)

        # Configure grid column weights to make the entry expand with tasks_manager_1_frame width
        self.new_task_frame.grid_columnconfigure(1, weight=1)

    def run(self):
        self.tasks_manager_1_frame.mainloop()


if __name__ == "__main__":
    task_manager_1 = None

    ### Modified to share the model between views
    # TK allows different views but requests a single Tk instance
    # so Task_Manager has been modified to now be displayed in a frame
    window = tk.Tk()
    window.title("Task Manager 1")
    window.config(background="grey")
    window.minsize(width=430, height=280)

    def file_modified(*args, **kwargs):
        if task_manager_1:
            task_manager_1.notify(*args, **kwargs)

    task_model = Task_CRUD_Model(file_modified)  # Create a connection to the Model

    # Fill the list for demonstration purpose
    fill_the_list = False
    if fill_the_list:
        for i in range(20):
            task_model.create(f"Task {i + 1}", (i + 2) % 4 + 1)

    task_manager_1 = Task_Manager_1(window, task_model)
    ###
    task_manager_1.run()
