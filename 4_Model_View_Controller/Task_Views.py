import textwrap
from datetime import datetime

import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from Task_Controllers import Button_List_Controller, Two_Rows_Controller, Two_Columns_Controller, Bar_Chart_Controller


class Button_List_View(tk.LabelFrame):

    def __init__(self, root_window, task_model, **kwargs):
        super().__init__(root_window, text=self.__class__.__name__, labelanchor=tk.NW, **kwargs)
        self.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # delegate all interactions with the model to the Controller
        self.controller = Button_List_Controller(task_model, self)

        self.popup_window = None
        self.create_the_new_task_frame()

        self.canvas = None
        self.scrollable_table = None
        self.create_the_main_task_frame()

        # Variable for the pop-up windows
        self.entry_var = tk.StringVar(self)
        self.priority_var = tk.StringVar(self)
        self.popup_window = None

        self.tasks_list = None
        self.notify_refresh = False
        self.refresh()  # engaging a first loading of the data

    def create_the_new_task_frame(self):
        new_task_frame = tk.Frame(self, background="white")
        new_task_frame.pack(side=tk.BOTTOM, fill=tk.X)
        add_button = tk.Button(new_task_frame, text="Add Task", width=10, command=lambda: self.action_pop_up("Add"))
        add_button.pack(padx=5, pady=8)

    def reset_input_fields(self):
        self.entry_var.set("Enter a new task here")
        self.priority_var.set("5")

    def create_the_main_task_frame(self):
        # create a Frame containing the table and the scrolling bar
        main_task_frame = tk.Frame(self)
        main_task_frame.pack(side=tk.RIGHT, fill=tk.BOTH)

        # Create a canvas to hold the table for scrolling
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        self.canvas.pack(fill=tk.X)

        # # Define a scrollable table
        self.scrollable_table = tk.Frame(self.canvas, borderwidth=1, relief=tk.SOLID)
        self.canvas.create_window((0, 0), window=self.scrollable_table, anchor=tk.NW, tags='canvas_window')

        # Create a horizontal scrollbar in the tasks_frame and link it to the canvas for the scrollable table
        y_scrollbar = tk.Scrollbar(main_task_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Config the cursor of the scrollbar to be sized/placed according to the width/position of the scrollable_table
        self.canvas.configure(yscrollcommand=y_scrollbar.set)

        # Bind the Configure event of the canvas to set it at the height of the scrollable table
        self.canvas.bind("<Configure>", self.set_canvas_height_width)

        # Bind mousewheel events to capture touchpad gestures
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

    def set_canvas_height_width(self, event):
        """This part is particularly tricky because it is based on tags and not on the instance !"""
        self.canvas.itemconfig('canvas_window', width=self.winfo_width())
        self.canvas.configure(height=self.scrollable_table.winfo_height())

    def on_mousewheel(self, event):
        # Detect vertical scroll gestures for touchpad and update the canvas's vertical scrolling
        if event.delta < 0:
            self.canvas.yview_scroll(1, tk.UNITS)
        elif event.delta > 0:
            self.canvas.yview_scroll(-1, tk.UNITS)

    def update_tasks_canvas(self):
        # Just refresh the list by reading the data
        self.tasks_list = self.controller.update_tasks_for_button_list()

        # Clear the previous widgets inside the tasks_frame if any
        for widget in self.scrollable_table.winfo_children():
            widget.destroy()

        for row, task in enumerate(self.tasks_list):
            task_lbl = tk.Label(self.scrollable_table,
                                text=f"{task[0]} - Priority : {task[1]}",
                                anchor=tk.W,
                                background="white")

            delete_btn = tk.Button(self.scrollable_table, text='🗑')
            delete_btn.bind("<Button-1>", lambda event, task_id=row: self.action_pop_up("Delete", task_id))

            update_btn = tk.Button(self.scrollable_table, text="✍")
            update_btn.bind("<Button-1>", lambda event, task_id=row: self.action_pop_up("Update", task_id))

            task_lbl.grid(row=row, column=0, sticky=tk.EW)
            update_btn.grid(row=row, column=1)
            delete_btn.grid(row=row, column=2, padx=(0, 20))     # pad x for scrollbar width

            # Configure grid column weights to make the task_lbl expand with scrollable_table width
            self.scrollable_table.grid_columnconfigure(0, weight=1)

        self.update_scroll_region()

    def update_scroll_region(self):
        # Update the scroll region of the scrolling_canvas to include all the widgets in the tasks list frame
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox(tk.ALL))
        self.set_canvas_height_width(None)

    def action_pop_up(self, action_var, task_id=None):
        self.popup_window = tk.Toplevel(self.scrollable_table)
        self.popup_window.title(f"{action_var} Task")

        if action_var == "Add":
            self.reset_input_fields()
        else:  # Update
            self.entry_var.set(self.tasks_list[task_id][0])
            self.priority_var.set(self.tasks_list[task_id][1])

        # Title Entry
        title_label = tk.Label(self.popup_window, text="Title:", width=20)
        title_entry = tk.Entry(self.popup_window, textvariable=self.entry_var)

        # Priority Dropdown Menu
        priority_label = tk.Label(self.popup_window, text="Priority:", width=20)
        priority_menu = tk.OptionMenu(self.popup_window, self.priority_var, "1", "2", "3", "4", "5")

        cancel_button = tk.Button(self.popup_window, text="Cancel", width=20,
                                  command=self.popup_cancel_button)

        if action_var == "Add":
            action_button = tk.Button(self.popup_window, text=f"{action_var}", width=20,
                                      command=self.popup_add_button)
        elif action_var == "Update":
            action_button = tk.Button(self.popup_window, text=f"{action_var}", width=20,
                                      command=lambda: self.popup_update_button(task_id))
        elif action_var == "Delete":
            action_button = tk.Button(self.popup_window, text=f"{action_var}", width=20,
                                      command=lambda: self.popup_delete_button(task_id))
        else:
            action_button = tk.Button(self.popup_window, text=f"{action_var}", width=20,
                                      command=self.popup_cancel_button)

        # Grid the elements on the pop-up
        title_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        title_entry.grid(row=0, column=1, padx=(0, 20), pady=5, sticky=tk.EW)
        priority_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        priority_menu.grid(row=1, column=1, padx=(0, 20), pady=5, sticky=tk.EW)

        # Grid the buttons inside the btn_frame with uniform spacing
        cancel_button.grid(row=2, column=0, padx=20, pady=10)
        action_button.grid(row=2, column=1, padx=(0, 20), pady=10)

        # Configure grid column weights to make the entry expand with view_frame width
        self.popup_window.grid_columnconfigure(0, weight=1)
        self.popup_window.grid_columnconfigure(1, weight=3)

    def popup_add_button(self):
        if len(self.entry_var.get()) > 0:
            self.controller.add_button(self.entry_var.get(), self.priority_var.get())

    def popup_update_button(self, task_id):
        if 0 <= task_id < len(self.tasks_list):
            if len(self.entry_var.get()) > 0:
                # Find the corresponding task in the model and update it
                selected_task_tuple = self.tasks_list[task_id]
                self.controller.update_button(selected_task_tuple, self.entry_var.get(), self.priority_var.get())

    def popup_delete_button(self, task_id):
        if 0 <= task_id < len(self.tasks_list):
            # Find the corresponding task in the model and update it
            selected_task_tuple = self.tasks_list[task_id]
            self.controller.delete_button(selected_task_tuple)

    def popup_cancel_button(self):
        self.refresh()

    def clear_pop_up_and_input_fields(self):
        if self.popup_window is not None:
            self.popup_window.destroy()
        self.reset_input_fields()

    def refresh(self):
        self.update_tasks_canvas()
        self.clear_pop_up_and_input_fields()
        self.notify_refresh = False

    def notify(self, *args, **kwargs):
        """ Called when the file/db is modified by another process and when the data is modified by another view """
        if self.notify_refresh is False:
            self.notify_refresh = True
            self.after(0, self.refresh)


class Two_Columns_View(tk.LabelFrame):

    def __init__(self, root_window, task_model, **kwargs):
        super().__init__(root_window, text=self.__class__.__name__, labelanchor=tk.NW, **kwargs)
        self.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # delegate all interactions with the model to the Controller
        self.controller = Two_Columns_Controller(task_model, self)

        self.entry_var = None
        self.priority_var = None
        self.add_update_button = None
        self.delete_button = None
        self.create_the_new_task_frame()

        self.tree = None
        self.selected_item = None
        self.create_the_main_task_frame()

        self.notify_refresh = False
        self.refresh()  # engaging a first loading of the data

    def create_the_new_task_frame(self):
        new_task_frame = tk.Frame(self, bg="white")
        new_task_frame.pack(side=tk.BOTTOM, padx=5, pady=(0, 5), fill=tk.X)

        self.entry_var = tk.StringVar(new_task_frame)
        self.priority_var = tk.StringVar(new_task_frame)

        # Title Entry
        title_label = tk.Label(new_task_frame, text="Title:")
        title_entry = tk.Entry(new_task_frame, textvariable=self.entry_var)

        # Priority Dropdown Menu
        priority_label = tk.Label(new_task_frame, text="Priority:")
        priority_menu = tk.OptionMenu(new_task_frame, self.priority_var, "1", "2", "3", "4", "5")

        # Add Button by default, Update Button if a task is selected
        self.add_update_button = tk.Button(new_task_frame, text="Add", command=self.handle_add_update)

        # Delete Button activated if a task is selected
        self.delete_button = tk.Button(new_task_frame, text="Delete", command=self.handle_delete, state=tk.DISABLED)

        # Grid the frame : Title [Entry] Priority [Menu] [Add/Update] [Delete]
        title_label.grid(row=0, column=0, padx=5, pady=5)
        title_entry.grid(row=0, column=1, padx=5, pady=5)
        priority_label.grid(row=0, column=2, padx=10, pady=5)
        priority_menu.grid(row=0, column=3, padx=5, pady=5)
        self.add_update_button.grid(row=0, column=4, padx=5, pady=5)
        self.delete_button.grid(row=0, column=5, padx=5, pady=5)

        # Configure grid column weights to make the title_entry expand with the new_task_frame width
        new_task_frame.grid_columnconfigure(1, weight=1)
        title_entry.grid(sticky=tk.EW)

    def handle_add_update(self):
        if len(self.entry_var.get()) > 0:
            if self.add_update_button['text'] == "Add":
                self.controller.add_button(self.entry_var.get(), self.priority_var.get())
            else:  # Update
                values_item = self.tree.item(self.selected_item, "tags")
                self.controller.update_button(values_item, self.entry_var.get(), self.priority_var.get())

    def handle_delete(self):
        values_item = self.tree.item(self.selected_item, "tags")
        self.controller.delete_button(values_item)

    def clear_selection_and_input_fields(self):
        if self.tree:
            for selected_item in self.tree.selection():
                self.tree.selection_remove(selected_item)
        self.selected_item = None
        self.entry_var.set("Enter a new task here")
        self.priority_var.set("5")
        self.add_update_button.config(text="Add")
        self.delete_button.config(state=tk.DISABLED)

    def create_the_main_task_frame(self):
        # Create a main frame for the labels and the scrolling bar
        main_task_frame = tk.Frame(self)
        main_task_frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)

        # Define a table with 2 columns and a header
        self.tree = ttk.Treeview(main_task_frame, columns=("Column 1", "Column 2"), show="headings")
        # Define the header of the Columns
        self.tree.heading("Column 1", text="Title")
        self.tree.heading("Column 2", text="Priority")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Define a scrollbar attached to the main_task_frame based on the TreeView height
        y_scrollbar = tk.Scrollbar(main_task_frame, orient=tk.VERTICAL, command=self.tree.yview)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Config the cursor of the scrollbar to be sized/placed according to the height/position of the Treeview
        self.tree.configure(yscrollcommand=y_scrollbar.set)

        # Bind mousewheel events to capture touchpad gestures
        self.tree.bind("<MouseWheel>", self.on_mousewheel)

        # Bind a function to the select event
        self.tree.bind("<<TreeviewSelect>>", self.on_treeview_select)

    def on_mousewheel(self, event):
        # Detect horizontal scroll gestures for touchpad and update the canvas's horizontal scrolling
        if event.delta < 0:
            self.tree.yview_scroll(1, tk.UNITS)
        elif event.delta > 0:
            self.tree.yview_scroll(-1, tk.UNITS)

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
                self.delete_button.config(state=tk.ACTIVE)
        else:
            self.clear_selection_and_input_fields()

    def update_tasks_main_frame(self):
        # Clear all the actual lines of the tree
        self.tree.delete(*self.tree.get_children())

        # Insert the tasks from the model
        task_list = self.controller.update_tasks_for_tree()
        for task in task_list:
            self.tree.insert("", tk.END, values=task, tags=task)  # 'tags' converts the values to compatible str

    def refresh(self):
        # Get the tasks from the model
        self.update_tasks_main_frame()
        # Clear all selections and init the fields to default values
        self.clear_selection_and_input_fields()
        self.notify_refresh = False

    def notify(self, *args, **kwargs):
        """ Called when the file/db is modified by another process and when the data is modified by another view """
        if self.notify_refresh is False:
            self.notify_refresh = True
            # The 'after' method from Tkinter library is employed to initiate the refresh within the main thread.
            # This setup is particularly requested when the system called this method to notify the application
            # about an external modification, especially when dealing with SQLITE3 files.
            self.after(0, self.refresh)


class Two_Rows_View(tk.LabelFrame):

    def __init__(self, root_window, task_model, **kwargs):
        super().__init__(root_window, text=self.__class__.__name__, labelanchor=tk.NW, **kwargs)
        self.pack(side=tk.BOTTOM, fill=tk.X)

        # delegate all interactions with the model to the Controller
        self.controller = Two_Rows_Controller(task_model, self)

        self.entry_var_new = None
        self.priority_var_new = None
        self.create_the_new_task_frame()

        self.canvas = None
        self.scrollable_table = None
        self.create_the_main_task_frame()

        self.tasks_list = None
        self.entry_var_list = None
        self.entry_list = None
        self.priority_var_list = None
        self.refresh()  # engaging a first loading of the data
        self.notify_refresh = False

    def create_the_new_task_frame(self):
        new_task_frame = tk.Frame(self, bg="white")
        new_task_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.entry_var_new = tk.StringVar(new_task_frame)
        self.priority_var_new = tk.StringVar(new_task_frame)

        # Title Entry
        title_entry = tk.Entry(new_task_frame, textvariable=self.entry_var_new)

        # Priority Dropdown Menu
        priority_menu = tk.OptionMenu(new_task_frame, self.priority_var_new, "1", "2", "3", "4", "5")

        # Add Button by default, Update Button if a task is selected
        add_button = tk.Button(new_task_frame, text="Add", command=self.handle_add_task)

        # Grid the frame
        title_entry.grid(row=0, column=0, padx=5, pady=5)
        priority_menu.grid(row=0, column=1, padx=5, pady=5)
        add_button.grid(row=0, column=2, padx=5, pady=5)

        # Configure grid column weights to make the title_entry expand with new_task_frame width
        new_task_frame.grid_columnconfigure(0, weight=1)
        title_entry.grid(sticky=tk.EW)

    def reset_input_fields(self):
        self.entry_var_new.set("Enter a new task here")
        self.priority_var_new.set("5")

    def handle_add_task(self):
        if len(self.entry_var_new.get()) > 0:
            self.controller.add_button(self.entry_var_new.get(), self.priority_var_new.get())

    def create_the_main_task_frame(self):
        # create a Frame containing the table and the scrolling bar
        main_task_frame = tk.Frame(self)
        main_task_frame.pack(side=tk.TOP, fill=tk.X)

        # Create a canvas to hold the table for scrolling
        self.canvas = tk.Canvas(main_task_frame, borderwidth=0, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # # Define a scrollable table
        self.scrollable_table = tk.Frame(self.canvas, borderwidth=1, relief=tk.SOLID)
        self.canvas.create_window((0, 0), window=self.scrollable_table, anchor=tk.NW)

        # Create a horizontal scrollbar in the tasks_frame and link it to the canvas for the scrollable table
        x_scrollbar = tk.Scrollbar(main_task_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Config the cursor of the scrollbar to be sized/placed according to the width/position of the scrollable_table
        self.canvas.configure(xscrollcommand=x_scrollbar.set)

        # Bind the Configure event of the canvas to set it at the height of the scrollable table
        self.canvas.bind("<Configure>", self.set_canvas_height)

        # Bind mousewheel events to capture touchpad gestures
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

    def set_canvas_height(self, event):
        self.canvas.configure(height=self.scrollable_table.winfo_height())

    def on_mousewheel(self, event):
        # Detect horizontal scroll gestures for touchpad and update the canvas's horizontal scrolling
        if event.delta < 0:
            self.canvas.xview_scroll(1, tk.UNITS)
        elif event.delta > 0:
            self.canvas.xview_scroll(-1, tk.UNITS)

    def update_tasks_canvas(self):
        # Get the data from the model through the controller
        self.tasks_list = self.controller.update_tasks_for_table()

        # Clear the previous widgets inside the scrollable_table if any
        for widget in self.scrollable_table.winfo_children():
            widget.destroy()

        self.entry_var_list = []
        self.entry_list = []
        self.priority_var_list = []

        for col, task in enumerate(self.tasks_list):
            # Set an Entry to see/modify the task name
            entry_var = tk.StringVar(self.scrollable_table, task[0])
            self.entry_var_list.append(entry_var)

            task_entry = tk.Entry(self.scrollable_table,
                                  textvariable=self.entry_var_list[col],
                                  width=len(self.entry_var_list[col].get()) + 2,
                                  borderwidth=1,
                                  relief=tk.RIDGE)
            self.entry_list.append(task_entry)

            self.entry_list[col].grid(row=0, column=col, sticky=tk.NSEW, padx=2, pady=(2, 0))

            # The width of the entry automatically adjust with the size of the variable (when typing)
            self.entry_list[col].bind("<KeyRelease>", lambda event, column=col: self.adjust_entry_width(column))

            # Initialize <Return> keypad or <FocusOut> to validate the task_entry and update it to the model
            self.entry_list[col].bind("<Return>", lambda event, column=col: self.update_delete_label(column))

            # Set an Option Menu to see/modify the priority
            priority_var = tk.StringVar(self.scrollable_table, task[1])
            self.priority_var_list.append(priority_var)

            priority_menu = tk.OptionMenu(self.scrollable_table, self.priority_var_list[col], "1", "2", "3", "4", "5")
            priority_menu.grid(row=1, column=col, sticky=tk.NSEW, pady=(0, 1))

            # Bind an event to the StringVar to trigger when the option is selected
            self.priority_var_list[col].trace_add("write", lambda *args, column=col: self.update_priority(column))

            self.update_scroll_region()

    def adjust_entry_width(self, column):
        # Adapt the length of the entry while typing
        new_entry_width = len(self.entry_var_list[column].get()) + 2
        self.entry_list[column].configure(width=new_entry_width)
        self.update_scroll_region()

    def update_scroll_region(self):
        # Update canvas scrolling region
        self.scrollable_table.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
        self.set_canvas_height(None)

    def update_delete_label(self, column):
        if 0 <= column < len(self.tasks_list):
            task_to_modify = self.tasks_list[column]
            new_entry_on_col = self.entry_var_list[column].get()
            priority_on_col = task_to_modify[1]
            if len(new_entry_on_col) > 0:
                self.controller.update_label(task_to_modify, new_entry_on_col, priority_on_col)
            else:
                self.controller.delete_label(task_to_modify)

    def update_priority(self, column):
        if 0 <= column < len(self.tasks_list):
            task_to_modify = self.tasks_list[column]
            entry_on_col = task_to_modify[0]
            new_priority_on_col = self.priority_var_list[column].get()
            self.controller.update_priority(task_to_modify, entry_on_col, new_priority_on_col)

    def refresh(self):
        # Get the tasks from the model
        self.update_tasks_canvas()
        # Clear all selections and init the fields to default values
        self.reset_input_fields()
        self.notify_refresh = False

    def notify(self, *args, **kwargs):
        """ Called when the file/db is modified by another process and when the data is modified by another view """
        if self.notify_refresh is False:
            self.notify_refresh = True
            # The 'after' method from Tkinter library is employed to initiate the refresh within the main thread.
            # This setup is particularly requested when the system called this method to notify the application
            # about an external modification, especially when dealing with SQLITE3 files.
            self.after(0, self.refresh)


class Bar_Chart_View(tk.LabelFrame):

    def __init__(self, root_window, task_model, **kwargs):
        super().__init__(root_window, text=self.__class__.__name__, labelanchor=tk.NW, **kwargs)
        self.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.controller = Bar_Chart_Controller(task_model, self)

        # Create a graph in a Canvas with Matplotlib
        self.figure, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(figure=self.figure, master=self)
        # Clean up the canvas before closing the window
        root_window.protocol("WM_DELETE_WINDOW", self.on_window_close)

        # Create a label in case of no task to display
        self.message_label = tk.Label(self, text="No task to display", font=("Helvetica", 16))

        self.notify_refresh = False
        self.refresh()  # engaging a first loading of the data

    def on_window_close(self):
        # Clean up the canvas
        if hasattr(self, 'canvas'):
            self.canvas.get_tk_widget().destroy()
        self.quit()

    def refresh_canvas(self):
        tasks = self.controller.update_tasks_for_barchart()

        if not tasks:
            # Clear the previous graph if any
            if hasattr(self, 'ax'):
                self.ax.clear()
            if hasattr(self, 'canvas'):
                self.canvas.get_tk_widget().pack_forget()
            self.message_label.pack(fill=tk.BOTH, expand=True)
        else:
            # Hide the "No tasks to display" label if it's currently packed
            self.message_label.pack_forget()

            task_names, priorities_int = zip(*[(task[0], task[1]) for task in tasks])

            # The highest bar will be the highest priority so the lowest value (the bigger is priority 1)
            priority_labels = {
                '1': 5,
                '2': 4,
                '3': 3,
                '4': 2,
                '5': 1
            }
            priorities_graph = [priority_labels[str(priority_int)] for priority_int in priorities_int]

            # Clear the previous graph if any
            if hasattr(self, 'ax'):
                self.ax.clear()

            # Create a new bar graph using pyplot
            x_values = range(len(task_names))
            self.ax.bar(x_values, priorities_graph, color='skyblue')

            # Label the axes
            self.ax.set_ylabel('Priority')
            self.ax.set_yticks(list(priority_labels.values()))
            self.ax.set_yticklabels(list(priority_labels.keys()))

            # Convert the range object to a list of integers
            tick_positions = list(range(len(task_names)))
            # Wrap task names to fit the bar width
            wrapped_task_names = [textwrap.fill(task_name, width=16) for task_name in task_names]
            # Set the positions of the ticks and their labels
            self.ax.set_xticks(tick_positions)
            self.ax.set_xticklabels(wrapped_task_names, rotation=45)

            # Auto Adjust the position of the graph within the figure according to the length of task names
            max_len = max([len(n) for n in task_names])
            enlarge_bottom = 0.1 if max_len <= 4 \
                else 0.2 if max_len <= 8 \
                else 0.25 if max_len <= 16 \
                else 0.3 if max_len <= 32 \
                else 0.4
            self.ax.figure.subplots_adjust(bottom=enlarge_bottom, top=0.95)

            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def refresh(self):
        # Get the tasks from the model
        self.refresh_canvas()
        self.notify_refresh = False

    def notify(self, *args, **kwargs):
        """ Called when the data is modified by another view """
        if self.notify_refresh is False:
            self.notify_refresh = True
            self.after(0, self.refresh)


if __name__ == "__main__":

    class Model_Simulator:
        def __init__(self):
            print("init a task model")
            self.tasks_list = [
                ('Task 1', 1, datetime(2023, 7, 25, 20, 48, 22, 702207)),
                ('Task 2', 2, datetime(2023, 7, 25, 20, 48, 22, 702208)),
                ('Task 3', 3, datetime(2023, 7, 25, 20, 48, 22, 702209)),
                ('Task 4', 4, datetime(2023, 7, 25, 20, 48, 22, 702210)),
                ('Task 5', 5, datetime(2023, 7, 25, 20, 48, 22, 702209)),
                ('Task 6', 1, datetime(2023, 7, 25, 20, 48, 22, 702210)),
            ]
            self.observers = []

        def add_observer(self, observer : callable):
            self.observers.append(observer)
            print(f"add_observer {observer=} on the task model")

        def create(self, task_name, task_priority):
            print(f"create a task into the model : {task_name=} {task_priority=}")
            self.tasks_list.append((task_name, task_priority, datetime(2023, 7, 25, 20, 48, 22, 702207)))
            self.notify()

        def update(self, selected_item, new_name, new_priority):
            print(f"update a task into the model : {selected_item=} {new_name=} {new_priority=}")
            self.tasks_list[selected_item] = (new_name, new_priority, datetime(2023, 7, 25, 20, 48, 22, 702207))
            self.notify()

        def delete(self, selected_item):
            print(f"delete a task from the model : {selected_item=} ")
            self.tasks_list.__delitem__(selected_item)
            self.notify()

        def read(self):
            print(f"reads tasks from the model : {self.tasks_list=}")
            return self.tasks_list

        def notify(self):
            for observer in self.observers:
                observer.notify()


    window = tk.Tk()
    window.title("Task Manager 1")
    window.config(background="grey")

    model_simulator = Model_Simulator()

    view1 = Two_Rows_View(window, model_simulator)
    view2 = Bar_Chart_View(window, model_simulator)
    view3 = Button_List_View(window, model_simulator)
    view4 = Two_Columns_View(window, model_simulator)

    window.mainloop()
