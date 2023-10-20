import textwrap
from collections import defaultdict
from datetime import datetime

import tkinter as tk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from Binding_patterns.TkinterBindings import BoundTk_StringVar, BoundTk_ListVar, BoundTk_TreeView
from Binding_patterns.SimpleBindings import Bound_List
from Task_ViewModels import Button_List_ViewModel, Two_Columns_ViewModel, Two_Rows_ViewModel, Bar_Chart_ViewModel


class Button_List_View(tk.LabelFrame):

    def __init__(self, root_window, viewmodel, **kwargs):
        super().__init__(root_window, text=self.__class__.__name__, labelanchor=tk.NW, **kwargs)

        # delegate all interactions to the view_model
        self.view_model = viewmodel

        # Variable for the pop-up windows
        self.label_var = BoundTk_StringVar("label_var", self.view_model.label_var, self)
        self.value_var = BoundTk_StringVar("value_var", self.view_model.value_var, self)
        self.popup_window = None

        # one button frame
        self.create_one_button_frame()

        # main frame
        self.canvas = None
        self.scrollable_table = None
        self.create_the_main_frame()    # create the frame, the canvas and the scrollable_table
        self.bound_tk_list = BoundTk_ListVar(
            name="bound_tk_list",
            list_type=BoundTk_StringVar,
            observable_list=self.view_model.observable_list,
            master=self.scrollable_table,
            on_list_modif=self.view_update_canvas
        )
        self.view_update_canvas()   # engaging a first loading of the data

    def on_closing(self):
        self.label_var.unbind_tk_var()
        self.value_var.unbind_tk_var()
        self.bound_tk_list.unbind_tk_list()

    def create_the_main_frame(self):
        # create a Frame containing the table and the scrolling bar
        main_frame = tk.Frame(self)
        main_frame.pack(side=tk.RIGHT, fill=tk.BOTH)

        # Create a canvas to hold the table for scrolling
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        self.canvas.pack(fill=tk.X)

        # # Define a scrollable table
        self.scrollable_table = tk.Frame(self.canvas, borderwidth=1, relief=tk.SOLID)
        self.canvas.create_window((0, 0), window=self.scrollable_table, anchor=tk.NW, tags='canvas_window')

        # Create a horizontal scrollbar in the tasks_frame and link it to the canvas for the scrollable table
        y_scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
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

    def view_update_canvas(self):
        # Clear the potential pop_up if any
        if self.popup_window is not None:
            self.popup_window.destroy()

        # Clear the previous widgets inside the tasks_frame if any
        for widget in self.scrollable_table.winfo_children():
            widget.destroy()

        for row, tk_item in enumerate(self.bound_tk_list):
            task_lbl = tk.Label(self.scrollable_table, textvariable=tk_item, anchor=tk.W, background="white")

            button1 = tk.Button(
                master=self.scrollable_table,
                text=self.view_model.list_button1_text,
                command=lambda item=row: (self.view_model.list_button1_command(item), self.view_display_popup())
            )

            button2 = tk.Button(
                master=self.scrollable_table,
                text=self.view_model.list_button2_text,
                command=lambda item=row: (self.view_model.list_button2_command(item), self.view_display_popup())
            )

            task_lbl.grid(row=row, column=0, sticky=tk.EW)
            button1.grid(row=row, column=1)
            button2.grid(row=row, column=2, padx=(0, 20))     # pad x for scrollbar width

            # Configure grid column weights to make the task_lbl expand with scrollable_table width
            self.scrollable_table.grid_columnconfigure(0, weight=1)

        # Update the scrollable table
        self.scrollable_table.update()
        # Update the canvas and scrollable region
        self.update_scroll_region()

    def update_scroll_region(self):
        # Update the scroll region of the scrolling_canvas to include all the widgets in the tasks list frame
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox(tk.ALL))
        self.set_canvas_height_width(None)

    def create_one_button_frame(self):
        frame = tk.Frame(self, background="white")
        frame.pack(side=tk.BOTTOM, fill=tk.X)
        one_button = tk.Button(
            master=frame,
            width=10,
            text=self.view_model.one_button_text,
            command=lambda: (self.view_model.one_button_command(), self.view_display_popup())
        )
        one_button.pack(padx=5, pady=8)

    def view_display_popup(self):
        self.popup_window = tk.Toplevel(self.scrollable_table)
        self.popup_window.title(f"{self.view_model.action_name} Task")

        # Label
        label_name = tk.Label(self.popup_window, text=self.view_model.label_name, width=20)
        label_entry = tk.Entry(self.popup_window, textvariable=self.label_var, state=self.view_model.state_entry)

        # Value
        value_name = tk.Label(self.popup_window, text=self.view_model.value_name, width=20)
        if self.view_model.state_entry == "readonly":
            value_menu = tk.OptionMenu(self.popup_window, self.value_var, self.value_var.get())
        else:
            value_menu = tk.OptionMenu(self.popup_window, self.value_var, *self.view_model.value_options)

        button_left = tk.Button(
            master=self.popup_window,
            width=20,
            text=self.view_model.button_left_text,
            command=lambda: (self.view_model.button_left_command(), self.popup_window.destroy())
        )

        button_right = tk.Button(
            master=self.popup_window,
            width=20,
            text=self.view_model.button_right_text,
            command=lambda: (self.view_model.button_right_command(), self.popup_window.destroy())
        )

        # Grid the elements on the pop-up
        label_name.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        label_entry.grid(row=0, column=1, padx=(0, 20), pady=5, sticky=tk.EW)
        value_name.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        value_menu.grid(row=1, column=1, padx=(0, 20), pady=5, sticky=tk.EW)

        # Grid the buttons inside the btn_frame with uniform spacing
        button_left.grid(row=2, column=0, padx=20, pady=10)
        button_right.grid(row=2, column=1, padx=(0, 20), pady=10)

        # Configure grid column weights to make the entry expand with view_frame width
        self.popup_window.grid_columnconfigure(0, weight=1)
        self.popup_window.grid_columnconfigure(1, weight=3)


class Two_Columns_View(tk.LabelFrame):

    def __init__(self, root_window, viewmodel, **kwargs):
        super().__init__(root_window, text=self.__class__.__name__, labelanchor=tk.NW, **kwargs)

        # delegate all interactions to the view_model
        self.view_model = viewmodel

        # Treeview Frame
        self.bound_tk_tree = None
        self.create_the_main_task_frame()   # engaging a first loading of the data

        # New Item Frame
        self.label_var = BoundTk_StringVar("label_var", self.view_model.label_var, self)
        self.value_var = BoundTk_StringVar("value_var", self.view_model.value_var, self)
        self.create_the_new_item_frame()

    def on_closing(self):
        self.label_var.unbind_tk_var()
        self.value_var.unbind_tk_var()
        self.bound_tk_tree.unbind_tk_treeview()

    def create_the_new_item_frame(self):
        new_task_frame = tk.Frame(self, bg="white")
        new_task_frame.pack(side=tk.BOTTOM, padx=5, pady=(0, 5), fill=tk.X)

        # Label
        label_name = tk.Label(new_task_frame, text=self.view_model.label_name)
        label_entry = tk.Entry(new_task_frame, textvariable=self.label_var)

        # Value
        value_name = tk.Label(new_task_frame, text=self.view_model.value_name)
        value_menu = tk.OptionMenu(new_task_frame, self.value_var, *self.view_model.value_options)

        self.button_left = tk.Button(
            master=new_task_frame,
            command=lambda: (self.view_model.button_left_command(), self.update_select_and_button_configs())
        )

        self.button_right = tk.Button(
            master=new_task_frame,
            command=lambda: (self.view_model.button_right_command(), self.update_select_and_button_configs())
        )
        self.update_select_and_button_configs()

        # Grid the frame : Label_Name [Entry] Value_Name [Menu] [Button_left] [Button_right]
        label_name.grid(row=0, column=0, padx=5, pady=5)
        label_entry.grid(row=0, column=1, padx=5, pady=5)
        value_name.grid(row=0, column=2, padx=10, pady=5)
        value_menu.grid(row=0, column=3, padx=5, pady=5)
        self.button_left.grid(row=0, column=4, padx=5, pady=5)
        self.button_right.grid(row=0, column=5, padx=5, pady=5)

        # Configure grid column weights to make the title_entry expand with the new_task_frame width
        new_task_frame.grid_columnconfigure(1, weight=1)
        label_entry.grid(sticky=tk.EW)

    def update_select_and_button_configs(self):
        self.button_left.config(
            text=self.view_model.button_left_text,
            state=tk.DISABLED if self.view_model.button_left_state == "disabled" else tk.NORMAL,
        )
        self.button_right.config(
            text=self.view_model.button_right_text,
            state=tk.DISABLED if self.view_model.button_right_state == "disabled" else tk.NORMAL
        )
        if self.view_model.selected_item is None :
            for selected_item in self.bound_tk_tree.selection():
                self.bound_tk_tree.selection_remove(selected_item)

    def create_the_main_task_frame(self):
        # Create a main frame for the labels and the scrolling bar
        main_task_frame = tk.Frame(self)
        main_task_frame.pack(side=tk.TOP, padx=5, pady=5, fill=tk.BOTH, expand=True)

        self.bound_tk_tree = BoundTk_TreeView(
            name="bound_tk_tree",
            observable_list=self.view_model.observable_list,
            master=main_task_frame,
            columns=("Column 1", "Column 2"),
            show="headings"
        )
        # Define the header of the Columns
        self.bound_tk_tree.heading("Column 1", text=self.view_model.label_name)
        self.bound_tk_tree.heading("Column 2", text=self.view_model.value_name)

        self.bound_tk_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Define a scrollbar attached to the main_task_frame based on the TreeView height
        y_scrollbar = tk.Scrollbar(main_task_frame, orient=tk.VERTICAL, command=self.bound_tk_tree.yview)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Config the cursor of the scrollbar to be sized/placed according to the height/position of the Treeview
        self.bound_tk_tree.configure(yscrollcommand=y_scrollbar.set)

        # Bind mousewheel events to capture touchpad gestures
        self.bound_tk_tree.bind("<MouseWheel>", self.on_mousewheel)

        # Bind a function to the select event
        self.bound_tk_tree.bind("<<TreeviewSelect>>", self.on_treeview_selection)

    def on_mousewheel(self, event):
        # Detect horizontal scroll gestures for touchpad and update the canvas's horizontal scrolling
        if event.delta < 0:
            self.bound_tk_tree.yview_scroll(1, tk.UNITS)
        elif event.delta > 0:
            self.bound_tk_tree.yview_scroll(-1, tk.UNITS)

    def on_treeview_selection(self, event):
        # Get the selected item line
        selected_items = self.bound_tk_tree.selection()  # tuple(item,...)

        if len(selected_items) >= 1:
            # Get the 'values' of the selected item
            item = self.bound_tk_tree.item(selected_items[0], "tags")
            index = self.bound_tk_tree.index(selected_items[0])

            if len(selected_items) == 1 and item != self.view_model.selected_item:
                # unique selection
                self.view_model.on_selection(item, index)
            else: # remove the selections or unselect the unique selection
                self.view_model.clear_input_fields()
        self.update_select_and_button_configs()


class Two_Rows_View(tk.LabelFrame):

    def __init__(self, root_window, viewmodel, **kwargs):
        super().__init__(root_window, text=self.__class__.__name__, labelanchor=tk.NW, **kwargs)

        # delegate all interactions to the view_model
        self.view_model = viewmodel

        # New Item Frame
        self.label_var = BoundTk_StringVar("label_var", self.view_model.label_var, self)    #entry_var_new
        self.value_var = BoundTk_StringVar("value_var", self.view_model.value_var, self)    #priority_var_new
        self.create_the_new_item_frame()

        self.canvas = None
        self.scrollable_table = None
        self.create_the_main_frame()
        self.bound_tk_labels = BoundTk_ListVar(
            name="label_list",
            list_type=BoundTk_StringVar,
            observable_list=self.view_model.label_list,
            master=self.scrollable_table,
            on_list_modif=self.view_update_canvas
        )
        self.bound_tk_values = BoundTk_ListVar(
            name="value_list",
            list_type=BoundTk_StringVar,
            observable_list=self.view_model.value_list,
            master=self.scrollable_table,
            on_list_modif=self.view_update_canvas
        )
        self.view_update_canvas()   # engaging a first loading of the data

        # self.refresh()  # engaging a first loading of the data
        # self.notify_refresh = False

    def on_closing(self):
        self.label_var.unbind_tk_var()
        self.value_var.unbind_tk_var()
        self.bound_tk_labels.unbind_tk_list()
        self.bound_tk_values.unbind_tk_list()

    def create_the_new_item_frame(self):
        new_task_frame = tk.Frame(self, bg="white")
        new_task_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Label
        label_entry = tk.Entry(new_task_frame, textvariable=self.label_var)

        # Value
        value_menu = tk.OptionMenu(new_task_frame, self.value_var, *self.view_model.value_options)

        # One Button
        one_button = tk.Button(
            master=new_task_frame,
            text=self.view_model.button_text,
            command=self.view_model.button_command
        )

        # Grid the frame
        label_entry.grid(row=0, column=0, padx=5, pady=5)
        value_menu.grid(row=0, column=1, padx=5, pady=5)
        one_button.grid(row=0, column=2, padx=5, pady=5)

        # Configure grid column weights to make the title_entry expand with new_task_frame width
        new_task_frame.grid_columnconfigure(0, weight=1)
        label_entry.grid(sticky=tk.EW)

    def create_the_main_frame(self):
        # create a Frame containing the table and the scrolling bar
        main_frame = tk.Frame(self)
        main_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Create a canvas to hold the table for scrolling
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)      # peut être main_task_frame
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # # Define a scrollable table
        self.scrollable_table = tk.Frame(self.canvas, borderwidth=1, relief=tk.SOLID)
        self.canvas.create_window((0, 0), window=self.scrollable_table, anchor=tk.NW)

        # Create a horizontal scrollbar in the tasks_frame and link it to the canvas for the scrollable table
        x_scrollbar = tk.Scrollbar(main_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
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

    def view_update_canvas(self):
        # Clear the previous widgets inside the scrollable_table if any
        for widget in self.scrollable_table.winfo_children():
            widget.destroy()

        for col in range(len(self.bound_tk_labels)):

            # Set an Entry to see/modify the item label
            label_entry = tk.Entry(
                self.scrollable_table,
                textvariable=self.bound_tk_labels[col],
                width=len(self.bound_tk_labels[col].get()) + 2,
                borderwidth=1,
                relief=tk.RIDGE
            )

            label_entry.grid(row=0, column=col, sticky=tk.NSEW, padx=2, pady=(2, 0))

            # The width of the entry automatically adjust with the size of the variable (when typing)
            label_entry.bind(
                sequence="<KeyRelease>",
                func=lambda event, ent=label_entry, column=col: self.adjust_entry_width(ent, column)
            )

            # Initialize <Return> keypad or <FocusOut> to validate the task_entry and update it to the model
            label_entry.bind(
                sequence="<Return>",
                func=lambda event, var=self.bound_tk_labels[col], column=col:
                    self.view_model.update_delete_label(var.get(), column)
            )

            if len(self.bound_tk_values) > col :
                # Set an Option Menu to see/modify the priority
                value_menu = tk.OptionMenu(
                    self.scrollable_table,
                    self.bound_tk_values[col],
                    *self.view_model.value_options
                )
                value_menu.grid(row=1, column=col, sticky=tk.NSEW, pady=(0, 1))

                # Bind an event to the StringVar to trigger when the option is selected
                self.bound_tk_values[col].trace_add(
                    mode="write",
                    callback=lambda *args, var=self.bound_tk_values[col], column=col:
                        self.view_model.update_value(var.get(), column)
                )
                # _update_property() is called after update_value() so the property returns wrong values in this last
                # therefore the right value is directly passed as argument to the update_value() method

            self.update_scroll_region()

    def update_scroll_region(self):
        # Update canvas scrolling region
        self.scrollable_table.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
        self.set_canvas_height(None)

    def adjust_entry_width(self, entry, column):
        # Adapt the length of the entry while typing
        entry.configure(width=len(self.bound_tk_labels[column].get()) + 2)
        self.update_scroll_region()


class Bar_Chart_View(tk.LabelFrame):

    def __init__(self, root_window, viewmodel, **kwargs):
        super().__init__(root_window, text=self.__class__.__name__, labelanchor=tk.NW, **kwargs)

        # delegate all interactions to the view_model
        self.view_model = viewmodel

        # Create a graph in a Canvas with Matplotlib
        self.figure, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(figure=self.figure, master=self)
        # Clean up the canvas before closing the window
        root_window.protocol("WM_DELETE_WINDOW", self.on_window_close)

        # Create a label in case of no task to display
        self.message_label = tk.Label(
            master=self,
            text=self.view_model.message_no_item if hasattr(self.view_model,'message_no_item') else "No item",
            font=("Helvetica", 16)
        )

        self.bound_tuples = Bound_List(
            name="bound_tuples",
            observable_list=self.view_model.observable_list,
            on_size_modified=self.view_update_canvas,
            on_item_modified=self.view_update_canvas
        )
        self.view_update_canvas()   # engaging a first loading of the data

    def on_window_close(self):
        self.bound_tuples.unbind_list()

        # Clean up the canvas
        if hasattr(self, 'canvas'):
            self.canvas.get_tk_widget().destroy()
        self.quit()

    def view_update_canvas(self, index=None):
        if len(self.bound_tuples) == 0:
            # Clear the previous graph if any
            if hasattr(self, 'ax'):
                self.ax.clear()
            if hasattr(self, 'canvas'):
                self.canvas.get_tk_widget().pack_forget()
            self.message_label.pack(fill=tk.BOTH, expand=True)
        else:
            # Hide the "No tasks to display" label if it's currently packed
            self.message_label.pack_forget()

            item_labels, item_values = zip(*[(item_tuple[0], item_tuple[1]) for item_tuple in self.bound_tuples])

            # The highest bar will be the highest priority so the lowest value (the bigger is priority 1)
            # if self.view_model.value_options = [1,2,3,4]
            # value_labels = {'1'=4,'2'=3,'3'=2,'4'=1}
            value_labels = defaultdict(int)
            if hasattr(self.view_model, "value_options"):
                if hasattr(self.view_model, "reversed_options") and self.view_model.reversed_options:
                    for i, option in enumerate(self.view_model.value_options):
                        value_labels[str(option)] = int(str(self.view_model.value_options[-1 - i]))
                else:
                    for i, option in enumerate(self.view_model.value_options):
                        value_labels[str(option)] = int(str(option))

            # convert the item_values into values for graph (reversed)
            graph_values = [value_labels[str(item_value)] for item_value in item_values]

            # Clear the previous graph if any
            if hasattr(self, 'ax'):
                self.ax.clear()

            # Create a new bar graph using pyplot
            x_values = range(len(item_labels))
            self.ax.bar(x_values, graph_values, color='skyblue')

            # Label the axes
            if hasattr(self.view_model, "value_name"):
                self.ax.set_ylabel(self.view_model.value_name)
            self.ax.set_yticks(list(value_labels.values()))
            self.ax.set_yticklabels(list(value_labels.keys()))

            # Convert the range object to a list of integers
            tick_positions = list(range(len(item_labels)))
            # Wrap task names to fit the bar width
            wrapped_item_labels = [textwrap.fill(item_label, width=16) for item_label in item_labels]
            # Set the positions of the ticks and their labels
            self.ax.set_xticks(tick_positions)
            self.ax.set_xticklabels(wrapped_item_labels, rotation=45)

            # Auto Adjust the position of the graph within the figure according to the length of task names
            max_len = max([len(n) for n in item_labels])
            enlarge_bottom = 0.1 if max_len <= 4 \
                else 0.2 if max_len <= 8 \
                else 0.25 if max_len <= 16 \
                else 0.3 if max_len <= 32 \
                else 0.4
            self.ax.figure.subplots_adjust(bottom=enlarge_bottom, top=0.95)

            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)



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

    # MODEL
    from Task_CRUD_Model import Task_CRUD_Model

    button_list_viewmodel = None
    two_columns_viewmodel = None
    two_rows_viewmodel = None
    bar_chart_viewmodel = None

    def file_modified(*args, **kwargs):
        """ Called when the file is modified """
        if button_list_viewmodel:
            button_list_viewmodel.notify(*args, **kwargs)
        if two_columns_viewmodel:
            two_columns_viewmodel.notify(*args, **kwargs)
        if two_rows_viewmodel:
            two_rows_viewmodel.notify(*args, **kwargs)
        if bar_chart_viewmodel:
            bar_chart_viewmodel.notify(*args, **kwargs)

    model_sim = Task_CRUD_Model(file_modified)  # Create a connection to the Model
    # model_sim = Model_Simulator()

    # VIEW MODEL
    button_list_viewmodel = Button_List_ViewModel(model_sim)
    two_columns_viewmodel = Two_Columns_ViewModel(model_sim)
    two_rows_viewmodel = Two_Rows_ViewModel(model_sim)
    bar_chart_viewmodel = Bar_Chart_ViewModel(model_sim)

    # VIEW
    view_1 = None
    view_2 = None
    view_3 = None
    view_4 = None

    # APP
    window = tk.Tk()
    window.title("Test Task Views")
    window.config(background="grey")
    #window.geometry("900x300")

    def on_closing():
        if view_1:
            view_1.on_closing()
        if view_2:
            view_2.on_closing()
        if view_3:
            view_3.on_closing()
        if view_4:
            view_4.on_closing()
        window.quit()

    # Clean up the binds before closing the window
    window.protocol("WM_DELETE_WINDOW", on_closing)

    view_1 = Two_Rows_View(window, two_rows_viewmodel)
    view_2 = Bar_Chart_View(window, bar_chart_viewmodel)
    view_3 = Button_List_View(window, button_list_viewmodel)
    view_4 = Two_Columns_View(window, two_columns_viewmodel)

    # with pack
    view_1.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
    view_2.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    view_3.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    view_4.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    # # with grid
    # view_1.grid(row=1, column=0, columnspan=3, sticky=tk.NSEW)
    # view_2.grid(row=0,column=0, sticky=tk.NSEW)
    # view_3.grid(row=0,column=1, sticky=tk.NSEW)
    # view_4.grid(row=0,column=2, sticky=tk.NSEW)
    # # How to react by window resizing
    # window.grid_columnconfigure(0, weight=2)
    # window.grid_columnconfigure(1, weight=1)
    # window.grid_columnconfigure(2, weight=1)
    # window.grid_rowconfigure(0, weight=3)
    # window.grid_rowconfigure(1, weight=1)

    window.mainloop()
