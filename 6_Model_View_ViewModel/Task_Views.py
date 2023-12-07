import atexit
import textwrap
from collections import defaultdict
import io

import tkinter as tk

from PIL import Image, ImageTk
import matplotlib

# Avoid UserWarning: Starting a Matplotlib GUI outside the main thread will likely fail.
matplotlib.use('agg')
from matplotlib import pyplot as plt

from Binding_patterns.TkinterBindings import BoundTk_StringVar, BoundTk_ListVar, BoundTk_TreeView
from Binding_patterns.SimpleBindings import Bound_List


class Button_List_View(tk.LabelFrame):

    def __init__(self, root_window, viewmodel, **kwargs):
        super().__init__(root_window, text=self.__class__.__name__, labelanchor=tk.NW, **kwargs)

        # delegate all interactions to the view_model
        self.view_model: Button_List_ViewModel_API = viewmodel

        # Variable for the pop-up windows
        self.label_var = BoundTk_StringVar("label_var", self.view_model.label_var, self)
        self.value_var = BoundTk_StringVar("value_var", self.view_model.value_var, self)
        self.popup_window = None

        # main frame
        self.canvas = None
        self.scrollable_table = None
        self.label_value_tk_list = BoundTk_ListVar(
            name="bound_tk_list",
            list_type=BoundTk_StringVar,
            observable_list=self.view_model.label_value_list,
            master=self.scrollable_table,
            on_list_modif=self.update_main_frame
        )
        atexit.register(self.on_closing)
        self.run()

    def on_closing(self):
        self.label_var.unbind_tk_var()
        self.value_var.unbind_tk_var()
        self.label_value_tk_list.unbind_tk_list()

    def run(self):
        ''' All properties and data should be initialized before to launch this method '''
        # one button frame
        self.create_one_button_frame()
        # main frame
        self.create_the_main_frame()  # create the frame, the canvas and the scrollable_table
        self.update_main_frame()  # engaging a first loading of the data

    def create_one_button_frame(self):
        frame = tk.Frame(self, background="white")
        frame.pack(side=tk.BOTTOM, fill=tk.X)
        one_button = tk.Button(
            master=frame,
            padx=4,
            text=self.view_model.one_button_text,
            command=lambda: (self.view_model.one_button_command(), self.display_popup())
        )
        one_button.pack(padx=5, pady=8)

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

    def update_main_frame(self):
        # Clear the potential pop_up if any
        if self.popup_window is not None:
            self.popup_window.destroy()

        # Clear the previous widgets inside the tasks_frame if any
        for widget in self.scrollable_table.winfo_children():
            widget.destroy()

        for row, tk_item in enumerate(self.label_value_tk_list):
            task_lbl = tk.Label(self.scrollable_table, textvariable=tk_item, anchor=tk.W, background="white")

            button1 = tk.Button(
                master=self.scrollable_table,
                text=self.view_model.list_button1_text,
                command=lambda item=row: (self.view_model.list_button1_command(item), self.display_popup())
            )

            button2 = tk.Button(
                master=self.scrollable_table,
                text=self.view_model.list_button2_text,
                command=lambda item=row: (self.view_model.list_button2_command(item), self.display_popup())
            )

            task_lbl.grid(row=row, column=0, sticky=tk.EW)
            button1.grid(row=row, column=1)
            button2.grid(row=row, column=2, padx=(0, 20))  # pad x for scrollbar width

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

    def display_popup(self):
        self.popup_window = tk.Toplevel(self)
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
        self.view_model: Two_Columns_ViewModel_API = viewmodel

        # New Item Frame
        self.label_var = BoundTk_StringVar("label_var", self.view_model.label_var, self)
        self.value_var = BoundTk_StringVar("value_var", self.view_model.value_var, self)

        # Treeview Frame
        self.bound_tk_tree = None
        self.button_left = None
        self.button_right = None

        atexit.register(self.on_closing)
        self.run()

    def on_closing(self):
        self.label_var.unbind_tk_var()
        self.value_var.unbind_tk_var()
        self.bound_tk_tree.unbind_tk_treeview()

    def run(self):
        ''' All properties and data should be initialized before to launch this method '''
        # Treeview Frame
        self.create_the_main_frame()  # engaging a first loading of the data

        # New Item Frame
        self.create_the_new_item_frame()

    def create_the_main_frame(self):
        # Create a main frame for the labels and the scrolling bar
        main_frame = tk.Frame(self)
        main_frame.pack(side=tk.TOP, padx=5, pady=5, fill=tk.BOTH, expand=True)

        self.bound_tk_tree = BoundTk_TreeView(
            name="bound_tk_tree",
            observable_list=self.view_model.label_value_tuple_list,
            master=main_frame,
            columns=("Column 1", "Column 2"),
            show="headings"
        )
        # Define the header of the Columns
        self.bound_tk_tree.heading("Column 1", text=self.view_model.label_name)
        self.bound_tk_tree.heading("Column 2", text=self.view_model.value_name)
        self.bound_tk_tree.grid(row=0, column=0, sticky=tk.NSEW)

        # Define a scrollbar attached to the main_frame based on the TreeView height
        y_scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.bound_tk_tree.yview)
        y_scrollbar.grid(row=0, column=1, sticky=tk.NS)

        # Config the cursor of the scrollbar to be sized/placed according to the height/position of the Treeview
        self.bound_tk_tree.configure(yscrollcommand=y_scrollbar.set)

        # Defines the weight of the columns in case of reduction
        main_frame.grid_rowconfigure(0, weight=1)  # tree enlarges/reduces its  height
        main_frame.grid_columnconfigure(0, weight=1)  # tree enlarges/reduces its width
        main_frame.grid_columnconfigure(1, weight=0)  # y_scrollbar does not enlarge/reduce its width

        # Bind mousewheel events to capture touchpad gestures
        self.bound_tk_tree.bind("<MouseWheel>", self.on_mousewheel)

        # Bind a function to the select event
        self.bound_tk_tree.bind("<<TreeviewSelect>>", self.on_treeview_selection)

    def create_the_new_item_frame(self):
        new_item_frame = tk.Frame(self, bg="white")
        new_item_frame.pack(side=tk.BOTTOM, padx=5, pady=(0, 5), fill=tk.X)

        # Label
        label_name = tk.Label(new_item_frame, text=self.view_model.label_name)
        label_entry = tk.Entry(new_item_frame, textvariable=self.label_var)

        # Value
        value_name = tk.Label(new_item_frame, text=self.view_model.value_name)
        value_menu = tk.OptionMenu(new_item_frame, self.value_var, *self.view_model.value_options)

        self.button_left = tk.Button(
            master=new_item_frame,
            command=lambda: (self.view_model.button_left_command(), self.update_selection_and_buttons())
        )

        self.button_right = tk.Button(
            master=new_item_frame,
            command=lambda: (self.view_model.button_right_command(), self.update_selection_and_buttons())
        )

        # Grid the frame : Label_Name [Entry] Value_Name [Menu] [Button_left] [Button_right]
        label_name.grid(row=0, column=0, padx=5, pady=5)
        label_entry.grid(row=0, column=1, padx=5, pady=5)
        value_name.grid(row=0, column=2, padx=10, pady=5)
        value_menu.grid(row=0, column=3, padx=5, pady=5)
        self.button_left.grid(row=0, column=4, padx=5, pady=5)
        self.button_right.grid(row=0, column=5, padx=5, pady=5)

        # Configure grid column weights to make the title_entry expand with the new_item_frame width
        new_item_frame.grid_columnconfigure(1, weight=1)
        label_entry.grid(sticky=tk.EW)

    def update_selection_and_buttons(self):
        self.button_left.config(
            text=self.view_model.button_left_text,
            state=self.view_model.button_left_state
        )
        self.button_right.config(
            text=self.view_model.button_right_text,
            state=self.view_model.button_right_state
        )
        if len(self.view_model.selected_item_dict) == 0:
            for selected_item in self.bound_tk_tree.selection():
                self.bound_tk_tree.selection_remove(selected_item)

    def on_mousewheel(self, event):
        # Detect horizontal scroll gestures for touchpad and update the canvas's horizontal scrolling
        if event.delta < 0:
            self.bound_tk_tree.yview_scroll(1, tk.UNITS)
        elif event.delta > 0:
            self.bound_tk_tree.yview_scroll(-1, tk.UNITS)

    # def on_treeview_selection(self, event):
    #     # Get the selected item line
    #     selected_items = self.bound_tk_tree.selection()  # tuple(item,...)
    #
    #     if len(selected_items) >= 1:
    #         # Get the 'values' of the selected item
    #         item = self.bound_tk_tree.item(selected_items[0], "tags")
    #         index = self.bound_tk_tree.index(selected_items[0])
    #
    #         if len(selected_items) == 1 and item != self.view_model.selected_item:
    #             # unique selection
    #             self.view_model.on_unique_selection(item, index)
    #         else: # remove the selections or unselect the unique selection
    #             self.view_model.clear_input_fields()
    #     self.update_selection_and_buttons()

    def on_treeview_selection(self, event):
        self.view_model.selected_item_dict.clear()  # dict[index_item] = item_tuple
        # Get the selected item line
        for item in self.bound_tk_tree.selection():  # tuple(item,...)
            self.view_model.selected_item_dict[self.bound_tk_tree.index(item)] = self.bound_tk_tree.item(item, "tags")
        self.view_model.on_selected_items()
        self.update_selection_and_buttons()


class Two_Rows_View(tk.LabelFrame):

    def __init__(self, root_window, viewmodel, **kwargs):
        super().__init__(root_window, text=self.__class__.__name__, labelanchor=tk.NW, **kwargs)

        # delegate all interactions to the view_model
        self.view_model: Two_Rows_ViewModel_API = viewmodel

        # New Item Frame
        self.label_var = BoundTk_StringVar("label_var", self.view_model.label_var, self)  # entry_var_new
        self.value_var = BoundTk_StringVar("value_var", self.view_model.value_var, self)  # priority_var_new

        # Main Frame
        self.canvas = None
        self.scrollable_table = None

        self.bound_tk_labels = BoundTk_ListVar(
            name="label_list",
            list_type=BoundTk_StringVar,
            observable_list=self.view_model.label_list,
            master=self.scrollable_table,
            on_list_modif=self.update_main_frame
        )

        self.bound_tk_values = BoundTk_ListVar(
            name="value_list",
            list_type=BoundTk_StringVar,
            observable_list=self.view_model.value_list,
            master=self.scrollable_table,
            on_list_modif=self.update_main_frame
        )

        atexit.register(self.on_closing)
        self.run()

    def on_closing(self):
        self.label_var.unbind_tk_var()
        self.value_var.unbind_tk_var()
        self.bound_tk_labels.unbind_tk_list()
        self.bound_tk_values.unbind_tk_list()

    def run(self):
        # New Item Frame
        self.create_the_new_item_frame()
        # Main Frame
        self.create_the_main_frame()
        self.update_main_frame()  # engaging a first loading of the data

    def create_the_new_item_frame(self):
        new_item_frame = tk.Frame(self, bg="white")
        new_item_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Label
        label_entry = tk.Entry(new_item_frame, textvariable=self.label_var)

        # Value
        value_menu = tk.OptionMenu(new_item_frame, self.value_var, *self.view_model.value_options)

        # One Button
        one_button = tk.Button(
            master=new_item_frame,
            text=self.view_model.button_text,
            command=self.view_model.button_command
        )

        # Grid the frame
        label_entry.grid(row=0, column=0, padx=5, pady=5)
        value_menu.grid(row=0, column=1, padx=5, pady=5)
        one_button.grid(row=0, column=2, padx=5, pady=5)

        # Configure grid column weights to make the title_entry expand with new_item_frame width
        new_item_frame.grid_columnconfigure(0, weight=1)
        label_entry.grid(sticky=tk.EW)

    def create_the_main_frame(self):
        # create a Frame containing the table and the scrolling bar
        main_frame = tk.Frame(self)
        main_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Create a canvas to hold the table for scrolling
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)  # peut être main_item_frame
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # # Define a scrollable table
        self.scrollable_table = tk.Frame(self.canvas, borderwidth=1, relief=tk.SOLID)
        self.canvas.create_window((0, 0), window=self.scrollable_table, anchor=tk.NW)

        # Create a horizontal scrollbar in the items_frame and link it to the canvas for the scrollable table
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

    def update_main_frame(self):
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
                func=lambda event, ent=label_entry, label=self.bound_tk_labels[col].get():
                self.adjust_entry_width(ent, label)
            )

            # Initialize <Return> keypad to validate the item_entry and update it to the model
            label_entry.bind(
                sequence="<Return>",
                func=lambda event, var=self.bound_tk_labels[col], index=col:
                self.view_model.on_label_return(var.get(), index)
            )

            if len(self.bound_tk_values) > col:
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
                    callback=lambda *args, var=self.bound_tk_values[col], index=col:
                    self.view_model.on_modified_value(var.get(), index)
                )

            self.update_scroll_region()

    def adjust_entry_width(self, entry, label):
        # Adapt the length of the entry while typing
        new_entry_width = len(label) + 2
        entry.configure(width=new_entry_width)
        self.update_scroll_region()

    def update_scroll_region(self):
        # Update canvas scrolling region
        self.scrollable_table.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
        self.set_canvas_height(None)


class Bar_Chart_View(tk.LabelFrame):

    def __init__(self, root_window, viewmodel, **kwargs):
        super().__init__(root_window, text=self.__class__.__name__, labelanchor=tk.NW, **kwargs)

        # delegate all interactions to the view_model
        self.view_model: Bar_Chart_ViewModel_API = viewmodel

        # Create a label in case of no task to display
        self.image_label = tk.Label(
            master=self,
            text=self.view_model.no_item_message,
            font=("Helvetica", 14),
            image=""
        )

        self.bound_tuples = Bound_List(
            name="bound_tuples",
            observable_list=self.view_model.label_value_tuple_list,
            on_size_modified=self.update_main_frame,
            on_item_modified=self.update_main_frame
        )
        atexit.register(self.on_closing)

        self.configure_event_id = None
        self.run()

    def on_closing(self):
        self.bound_tuples.unbind_list()

    def run(self):
        self.update_main_frame()  # engaging a first loading of the data
        self.bind("<Configure>", self.on_configure)

    def on_configure(self, event):
        # Resize the image only when the window size did not change for 50ms to avoid lags when resizing
        if self.configure_event_id:
            self.after_cancel(self.configure_event_id)
        self.configure_event_id = self.after(50, self.resize_image)

    def resize_image(self):
        x_borders = 8  # 2 * 4
        y_borders = 23  # 2 * 4 + 15 (text of label frame)
        if len(self.bound_tuples) > 0:
            self.set_image_label(super().winfo_width() - x_borders, super().winfo_height() - y_borders)

    def update_main_frame(self, index=None):
        self.image_label.pack_forget()  # Allow to the image to be resized properly
        if len(self.bound_tuples) == 0:
            self.set_text_label()
        else:
            self.set_image_label(600, 400)
        self.image_label.pack(fill=tk.BOTH, expand=True)

    def set_text_label(self):
        self.image_label.config(text=self.view_model.no_item_message, image="", padx=20)
        self.image_label.image = None

    def set_image_label(self, width, height):
        # Update the content of the new graph
        image_data = self.design_chart(width, height)

        # Create a PhotoImage object from the base64-encoded image
        img = Image.open(io.BytesIO(image_data))
        photo = ImageTk.PhotoImage(img)

        # This line keeps a reference to the image to prevent it from being garbage collected
        self.image_label.config(text="", image=photo, padx=0)
        self.image_label.image = photo

    def design_chart(self, width, height):
        DPI = 100
        # Create a new figure and axis
        figure, ax = plt.subplots(figsize=(width / DPI, height / DPI), dpi=DPI)

        item_labels, item_values = zip(*[(item[0], item[1]) for item in self.bound_tuples])

        # The highest bar will be the highest priority so the lowest value (the bigger is priority 1)
        # if self.value_options = [1,2,3,4]
        # value_tags = {'1'=4,'2'=3,'3'=2,'4'=1}
        value_tags = defaultdict(int)
        if len(self.view_model.value_options) > 0:
            if self.view_model.reversed_options:
                for i, option in enumerate(self.view_model.value_options):
                    value_tags[str(option)] = int(str(self.view_model.value_options[-1 - i]))
            else:
                for i, option in enumerate(self.view_model.value_options):
                    value_tags[str(option)] = int(str(option))

        # convert the item_values into values for graph (reversed)
        graph_values = [value_tags[str(item_value)] for item_value in item_values]

        # Create a new bar graph using pyplot
        x_values = range(len(item_labels))
        ax.bar(x_values, graph_values, color='skyblue')

        # Label the axes
        ax.set_ylabel(self.view_model.value_name)
        ax.set_yticks(list(value_tags.values()))
        ax.set_yticklabels(list(value_tags.keys()))

        # Convert the range object to a list of integers
        tick_positions = list(range(len(item_labels)))
        # Wrap task names to fit the bar width
        wrapped_item_labels = [textwrap.fill(item_label, width=16) for item_label in item_labels]
        # Set the positions of the ticks and their labels
        ax.set_xticks(tick_positions)
        ax.set_xticklabels(wrapped_item_labels, rotation=45)

        # Auto Adjust the position of the graph within the figure according to the length of item labels
        max_len = max([len(n) for n in item_labels])
        enlarge_bottom = 0.1 if max_len <= 4 \
            else 0.2 if max_len <= 8 \
            else 0.25 if max_len <= 16 \
            else 0.3 if max_len <= 32 \
            else 0.4
        ax.figure.subplots_adjust(bottom=enlarge_bottom, top=0.95)

        # Create a BytesIO buffer to store the image in memory in binary
        buffer = io.BytesIO()
        # Save the plot in the BytesIO buffer instead of a file in binary
        plt.savefig(buffer, format='png')
        # Delete the figure and close the plot after saving it to the buffer
        figure.clf()
        plt.close()

        # Retrieve the image data as a byte string
        buffer.seek(0)
        image_data = buffer.getvalue()
        buffer.close()
        return image_data


if __name__ == "__main__":

    import tkinter as tk

    from Observer_patterns.Observables import ObservableList, ObservableProperty

    from Task_ViewModels_API import Bar_Chart_ViewModel_API
    from Task_ViewModels_API import Two_Rows_ViewModel_API
    from Task_ViewModels_API import Two_Columns_ViewModel_API
    from Task_ViewModels_API import Button_List_ViewModel_API

    def param_button_list_viewmodel(viewmodel: Button_List_ViewModel_API):
        # The view should be limited to its API not to use GUI technology methods

        # common
        viewmodel.label_name = "label_name"
        viewmodel.value_name = "value_name"
        # one_button_frame
        viewmodel.one_button_text = "one_button_text"
        viewmodel.one_button_command = lambda: print("one_button_command clicked")
        # main frame
        viewmodel.label_value_list = ObservableList(["Text1", "Text2", "Text3", "Text4", "Text5"])
        viewmodel.list_button1_text = "list_button1_text"
        viewmodel.list_button1_command = lambda row: print("list_button1_command clicked row", row)
        viewmodel.list_button2_text = 'list_button2_text'

        # view.list_button2_command = lambda row: print("list_button2_command clicked", row)
        def set_nouveau(row):
            viewmodel.label_value_list[row].set("Nouveau")

        viewmodel.list_button2_command = lambda row: (
            set_nouveau(row),
            print("list_button2_command clicked row", row)
        )
        # popup_window
        viewmodel.action_name = "action_name"
        viewmodel.label_var = ObservableProperty("label_var")
        viewmodel.value_var = ObservableProperty("value_var")
        viewmodel.value_options = ["1", "2", "3", "4", "5"]
        viewmodel.state_entry = "normal"  # "normal/readonly"
        viewmodel.button_left_text = "button_left_text"
        viewmodel.button_left_command = lambda: print("button_left_command clicked")
        viewmodel.button_right_text = "button_right_text"
        viewmodel.button_right_command = lambda: print("button_right_command clicked")


    def param_two_columns_viewmodel(viewmodel: Two_Columns_ViewModel_API):
        # The view should be limited to its API not to use GUI technology methods

        # common
        viewmodel.label_name = "label_name"
        viewmodel.value_name = "value_name"

        # new item frame
        viewmodel.label_var = ObservableProperty("label_var_text")
        viewmodel.value_var = ObservableProperty("value_var_text")
        viewmodel.value_options = ["1", "2", "3", "4", "5"]
        viewmodel.button_left_text = "button_left_text"  # "Add" / "Update"
        viewmodel.button_left_command = lambda: print("button_left_command clicked")
        viewmodel.button_left_state = "normal"  # "normal" / "disabled"
        viewmodel.button_right_text = "button_right_text"
        viewmodel.button_right_command = lambda: print("button_right_command clicked")
        viewmodel.button_right_state = "disabled"  # "normal" / "disabled"

        # main frame
        tuple_list = [("Label1", "Value1"), ("Label2", "Value2"), ("Label3", "Value3")]
        viewmodel.label_value_tuple_list = ObservableList(tuple_list)
        viewmodel.on_selected_items = lambda: print("on_selected_items clicked", viewmodel.selected_item_dict)
        viewmodel.selected_item_dict.clear()  # dict[index_item] = item_tuple


    def param_two_rows_viewmodel(viewmodel: Two_Rows_ViewModel_API):
        # The view should be limited to its API not to use GUI technology methods

        # Main Frame
        viewmodel.label_list = ObservableList(["Label1", "Label2", "Label3"])
        viewmodel.on_label_return = lambda label, index: print("on_label_return tapped", label, index)
        viewmodel.value_list = ObservableList(["Value1", "Value2", "Value3"])
        viewmodel.on_modified_value = lambda value, index: print("on_modified_value clicked", value, index)
        # New Item frame
        viewmodel.label_var = ObservableProperty("label_var_text")
        viewmodel.value_var = ObservableProperty("value_var_text")
        viewmodel.value_options = ["1", "2", "3", "4", "5"]
        viewmodel.button_text = "button_text"  # One button
        viewmodel.button_command = lambda: print("button_command clicked")


    def param_bar_chart_viewmodel(viewmodel: Bar_Chart_ViewModel_API):
        # The view should be limited to its API not to use GUI technology methods

        # Main Frame
        viewmodel.value_name = "value_name"
        viewmodel.value_options = ["1", "2", "3", "4", "5"]
        viewmodel.reversed_options = False
        viewmodel.no_item_message = "No item"
        viewmodel.label_value_tuple_list = ObservableList([("Label1", "2"), ("Label2", "1"), ("Label3", "3")])


    def open_window():
        win = tk.Tk()
        win.title("Test Task Views")
        win.config(background="grey")
        return win


    try:
        while True:
            print("1. Button_List_View")
            print("2. Two_Columns_View")
            print("3. Two_Rows_View")
            print("4. Bar_Chart_View")
            print("0. Quit")
            choice = input("Your choice : ")

            if choice == "1":
                window = open_window()

                button_list_viewmodel = Button_List_ViewModel_API()
                param_button_list_viewmodel(button_list_viewmodel)

                button_list_view = Button_List_View(window, button_list_viewmodel)
                button_list_view.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

                window.mainloop()

            elif choice == "2":
                window = open_window()

                two_columns_viewmodel = Two_Columns_ViewModel_API()
                param_two_columns_viewmodel(two_columns_viewmodel)

                two_columns_view = Two_Columns_View(window, two_columns_viewmodel)
                two_columns_view.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

                window.mainloop()

            elif choice == "3":
                window = open_window()

                two_rows_viewmodel = Two_Rows_ViewModel_API()
                param_two_rows_viewmodel(two_rows_viewmodel)

                two_rows_view = Two_Rows_View(window, two_rows_viewmodel)
                two_rows_view.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

                window.mainloop()

            elif choice == "4":
                window = open_window()

                bar_chart_viewmodel = Bar_Chart_ViewModel_API()
                param_bar_chart_viewmodel(bar_chart_viewmodel)

                bar_chart_view = Bar_Chart_View(window, bar_chart_viewmodel)
                bar_chart_view.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

                window.mainloop()

            elif choice == "0":
                break

            else:
                print("This option is not available")

    except KeyboardInterrupt:
        pass
