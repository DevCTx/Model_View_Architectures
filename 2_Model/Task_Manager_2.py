import tkinter as tk

### Modified to use the model
from Task_CRUD_Model import Task_CRUD_Model
###

class Task_Manager_2:
    """
    This application presents a Simple Task Manager that allows adding, updating or deleting a task
    to/from a list printed to the screen with a scrolling bar.

    There is no specific view or model defined here.
    """

    def __init__(self, fill_the_list: bool = True):

        ### Modified to use the model
        self.tasks = Task_CRUD_Model(self.notify_on_file_modified)      # Create a connection to the Model

        # Fill the list for demonstration purpose
        if fill_the_list:
            for i in range(20):
                self.tasks.create(f"Task {i + 1}", (i + 2) % 4 + 1)

        self.task_list = []
        self.update_tasks_from_model()
        ###

        self.window = tk.Tk()
        self.window.title("Tasks Manager 2")
        self.window.config(background="grey")
        self.window.minsize(width=430, height=280)

        self.entry_var = tk.StringVar(self.window)
        self.priority_var = tk.StringVar(self.window)
        self.popup_window = None

        self._create_the_tasks_main_frame()
        self._create_the_new_task_frame()
        self.clear_pop_up_and_input_fields()

        # Bind the mouse wheel event to the canvas
        self.window.bind_all("<MouseWheel>", self._on_canvas_mousewheel)

    ### Modified to use the model
    def update_tasks_from_model(self):
        # Just refresh the list by reading the data
        # self.tasks_list = [(task[0],task[1],task[2]) for task in self.tasks.read()]
        self.tasks_list = self.tasks.read()
    ###

    def refresh(self, *args, **kwargs):
        """ Called when the file/db is modified by another process """
        self.update_tasks_from_model()
        self.clear_pop_up_and_input_fields()

    ### Added to get the notifications when the file/db is modified
    def notify_on_file_modified(self, *args, **kwargs):
        """ Called when the file/db is modified by another process """
        self.refresh()
    ###

    def _refresh_tasks_option_frame_list(self):
        # Clear the existing tasks in the list frame
        for task_option_frame in self.tasks_list_frame.winfo_children():
            task_option_frame.destroy()

        # Rebuild the list of tasks
        self._build_tasks_list_frame()

        # # Re-grid the tasks_scrolling_canvas to the new tasks list
        self.tasks_scrolling_canvas.update_idletasks()

    def _build_tasks_list_frame(self):
        for task_list_id, task in enumerate(self.tasks_list):
            # Define a frame for each task with a label and the button options
            task_option_frame = tk.Frame(self.tasks_list_frame)
            task_option_frame.pack(fill=tk.X, expand=True)

            task_lbl = tk.Label(task_option_frame, text=f"{task[0]} - Priority : {task[1]}", bg="white", anchor="w")
            task_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)

            delete_btn = tk.Button(task_option_frame, text='🗑')
            delete_btn.bind("<Button-1>", lambda event, task_id=task_list_id: self.action_pop_up("Delete", task_id))
            delete_btn.pack(side=tk.RIGHT)

            update_btn = tk.Button(task_option_frame, text="✍")
            update_btn.bind("<Button-1>", lambda event, task_id=task_list_id: self.action_pop_up("Update", task_id))
            update_btn.pack(side=tk.RIGHT)

    def _create_the_tasks_main_frame(self):
        # Create a main frame for the labels and the scrolling bar
        self.tasks_main_frame = tk.Frame(self.window)
        self.tasks_main_frame.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        # Use the built-in scrolling option of Canvas to scroll labels in a canvas window
        self.tasks_scrolling_canvas = tk.Canvas(self.tasks_main_frame)
        self.tasks_scrolling_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Define a frame to list the tasks with the button options attached to the canvas
        self.tasks_list_frame = tk.Frame(self.tasks_scrolling_canvas)

        # Build the list of tasks and buttons in the tasks list frame
        self._build_tasks_list_frame()

        # Create a window inside the canvas to be able to display the tasks list frame
        tasks_list_canvas_window = self.tasks_scrolling_canvas.create_window(0, 0, anchor="nw",
                                                                             window=self.tasks_list_frame)

        # Create a vertical scrollbar widget in the main frame to scroll the canvas
        scrollbar = tk.Scrollbar(self.tasks_main_frame, orient=tk.VERTICAL, command=self.tasks_scrolling_canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def update_canvas_window_and_scroll_region(event):
            # Update the width of the tasks_list_canvas_window
            self.tasks_scrolling_canvas.itemconfigure(tasks_list_canvas_window, width=event.width)
            # Update the width/height of the region to scroll
            self.tasks_scrolling_canvas.configure(scrollregion=self.tasks_scrolling_canvas.bbox("all"))
            # Update the position and size of the cursor on the scrollbar
            self.tasks_scrolling_canvas.configure(yscrollcommand=scrollbar.set)

        # Bind the configure events of the canvas to automatically update the size of the tasks_list_canvas_window
        self.tasks_scrolling_canvas.bind("<Configure>", update_canvas_window_and_scroll_region)

    def _on_canvas_mousewheel(self, event):
        # Scroll the canvas vertically when the mouse wheel is used
        self.tasks_scrolling_canvas.yview_scroll(-1 * (event.delta // 120), "units")

    def _create_the_new_task_frame(self):
        button = tk.Button(self.window, text="Add Task", width=10, command=lambda: self.action_pop_up("Add"))
        button.pack(padx=20, pady=10)

    def clear_pop_up_and_input_fields(self):
        if self.popup_window is not None:
            self.popup_window.destroy()

        self._refresh_tasks_option_frame_list()

        # Update the scroll region of the canvas to include all the widgets in the tasks list frame
        self.tasks_main_frame.update_idletasks()
        self.tasks_scrolling_canvas.configure(scrollregion=self.tasks_scrolling_canvas.bbox("all"))

        self.entry_var.set("Enter a new task here")
        self.priority_var.set("5")

    def handle_add_task(self):
        if len(self.entry_var.get()) > 0:
            ### Modified to use the model
            self.tasks.create(self.entry_var.get(), int(self.priority_var.get()))

            self.refresh()
            ###

    def handle_update_task(self, task_id):
        if 0 <= task_id < len(self.tasks_list):
            ### Modified to use the model
            if len(self.entry_var.get()) > 0:

                # Find the corresponding task in the model and update it
                selected_task_tuple = self.tasks_list[task_id]

                for idx, task_tuple in enumerate(self.tasks.read()):
                    if task_tuple == selected_task_tuple :
                        self.tasks.update(idx, self.entry_var.get(), int(self.priority_var.get()))
                        break

            self.refresh()
            ###

    def handle_delete_task(self, task_id):
        if 0 <= task_id < len(self.tasks_list):
            ### Modified to use the model
            # Find the corresponding task in the model and update it
            selected_task_tuple = self.tasks_list[task_id]

            for idx, task_tuple in enumerate(self.tasks.read()):
                if task_tuple == selected_task_tuple :
                    self.tasks.delete(idx)
                    break

            self.refresh()
            ###

    def handle_no_change(self):
        self.refresh()

    def action_pop_up(self, action_var, task_id=None):
        self.popup_window = tk.Toplevel(self.window)
        self.popup_window.title(f"{action_var} Task")

        if action_var == "Add":
            self.entry_var.set("Enter a new task here")
            self.priority_var.set("5")
        else:
            self.entry_var.set(self.tasks_list[task_id][0])
            self.priority_var.set(self.tasks_list[task_id][1])

        # Title Entry
        title_label = tk.Label(self.popup_window, text="Title:", width=20)
        title_entry = tk.Entry(self.popup_window, textvariable=self.entry_var)

        # Priority Dropdown Menu
        priority_label = tk.Label(self.popup_window, text="Priority:", width=20)
        priority_menu = tk.OptionMenu(self.popup_window, self.priority_var, "1", "2", "3", "4", "5")

        cancel_button = tk.Button(self.popup_window, text="Cancel", width=20,
                                  command=self.handle_no_change)

        if action_var == "Add":
            action_button = tk.Button(self.popup_window, text=f"{action_var}", width=20,
                                      command=self.handle_add_task)
        elif action_var == "Update":
            action_button = tk.Button(self.popup_window, text=f"{action_var}", width=20,
                                      command=lambda: self.handle_update_task(task_id))
        elif action_var == "Delete":
            action_button = tk.Button(self.popup_window, text=f"{action_var}", width=20,
                                      command=lambda: self.handle_delete_task(task_id))
        else:
            action_button = tk.Button(self.popup_window, text=f"{action_var}", width=20,
                                      command=self.handle_no_change)

        # Grid the elements on the pop-up
        title_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        title_entry.grid(row=0, column=1, padx=(0, 20), pady=5, sticky="ew")
        priority_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        priority_menu.grid(row=1, column=1, padx=(0, 20), pady=5, sticky="ew")

        # Grid the buttons inside the btn_frame with uniform spacing
        cancel_button.grid(row=2, column=0, padx=20, pady=10)
        action_button.grid(row=2, column=1, padx=(0, 20), pady=10)

        # Configure grid column weights to make the entry expand with window width
        self.popup_window.grid_columnconfigure(0, weight=1)
        self.popup_window.grid_columnconfigure(1, weight=3)

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    task_manager_2 = Task_Manager_2(False)
    task_manager_2.run()
