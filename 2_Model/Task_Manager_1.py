import tkinter as tk
from tkinter import ttk

### Modified to use the model
from Task_CRUD_Model import Task_CRUD_Model
###


class Task_Manager_1:
    '''
    This application presents a Simple Task Manager which uses

    a Task CRUD Model to add, update or delete a task to/from a list, file or a database
    and print the results in a list on the screen with a scrolling bar.

    There is no specific view handled here yet.
    '''

    def __init__(self, fill_the_list: bool = True):
        ### Modified to use the model
        self.tasks = Task_CRUD_Model(self.notify_on_file_modified)      # Create a connection to the Model

        # Fill the list for demonstration purpose
        if fill_the_list:
            for i in range(20):
                self.tasks.create(f"Task {i + 1}", (i + 2) % 4 + 1)
        ###

        self.window = tk.Tk()
        self.window.title("Tasks Manager 1")
        self.window.config(background="grey")
        self.window.minsize(width=430, height=280)

        # No selected item per default
        self.selected_item = None

        self._create_the_tasks_main_frame()
        self._create_the_new_task_frame()

    def _create_the_tasks_main_frame(self):
        # Create a main frame for the labels and the scrolling bar
        self.tasks_main_frame = tk.Frame(self.window, bg="blue")
        self.tasks_main_frame.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        # Define a table with 2 columns and a header
        self.tree = ttk.Treeview(self.tasks_main_frame, columns=("Column 1", "Column 2"), show="headings")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Define a scrollbar attached to the window based on the TreeView height
        scrollbar = tk.Scrollbar(self.tasks_main_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Config the cursor of the scrollbar to be sized/placed according to the height/position of the Treeview
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Define the header of the Columns
        self.tree.heading("Column 1", text="Title")
        self.tree.heading("Column 2", text="Priority")

        # Bind a function to the select event
        self.tree.bind("<<TreeviewSelect>>", self.on_treeview_select)

        ### Modified to use the model
        # Get the tasks from the model
        self.update_tasks_from_model()
        ###


    ### Modified to use the model
    def update_tasks_from_model(self):
        # Clear all the actual lines of the tree
        self.tree.delete(*self.tree.get_children())

        # Insert the tasks from the model
        for task in self.tasks.read():
            self.tree.insert("", tk.END, values=task, tags=task)    # 'tags' converts the values to compatible str
    ###

    def refresh(self, *args, **kwargs):
        self.update_tasks_from_model()
        self.clear_selection_and_input_fields()

    ### Added to get the notifications when the file/db is modified
    def notify_on_file_modified(self, *args, **kwargs):
        """ Called when the file/db is modified by another process """
        # Triggers the update from the main thread, requested when using SQLITE3 in particular
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
        for selected_item in self.tree.selection():
            self.tree.selection_remove(selected_item)
        self.selected_item = None
        self.entry_var.set("Enter a new task here")
        self.priority_var.set("5")
        self.add_update_button.config(text="Add")
        self.delete_button.config(state="disabled")

    def handle_add_update_task(self):
        if len(self.entry_var.get()) > 0:
            ### Modified to use the model
            if self.add_update_button['text'] == "Add":
                self.tasks.create(self.entry_var.get(), int(self.priority_var.get()))

            else:  # Update
                values_item = self.tree.item(self.selected_item, "tags")

                for idx, task_tuple in enumerate(self.tasks.read()):
                    if task_tuple[0] == values_item[0] and task_tuple[1] == int(values_item[1]):
                        self.tasks.update(idx, self.entry_var.get(), int(self.priority_var.get()))
                        break

            self.refresh()
            ###

    def handle_delete_task(self):
        ### Modified to use the model
        values_item = self.tree.item(self.selected_item, "tags")

        for idx, task_tuple in enumerate(self.tasks.read()):
            if task_tuple[0] == values_item[0] and task_tuple[1] == int(values_item[1]):
                self.tasks.delete(idx)
                break

        self.refresh()
        ###

    def _create_the_new_task_frame(self):
        self.new_task_frame = tk.Frame(self.window, bg="white")
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

        # Configure grid column weights to make the entry expand with window width
        self.new_task_frame.grid_columnconfigure(1, weight=1)

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    task_manager_1 = Task_Manager_1(False)
    task_manager_1.run()
