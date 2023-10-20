from collections import defaultdict

from Task_Controllers import Button_List_Controller, Two_Rows_Controller, Two_Columns_Controller, Bar_Chart_Controller

from Observer_patterns.Observables import ObservableProperty, ObservableList

class Button_List_ViewModel:
    def __init__(self, task_model):
        # delegate all interactions with the model to the Controller
        self.controller = Button_List_Controller(task_model, self)
        self.task_list = []

        # common
        self.label_name = "Title:"
        self.value_name = "Priority:"

        # one_button_frame
        self.one_button_text = "Add"
        self.one_button_command = self.init_add_popup

        # main frame
        self.observable_list = ObservableList(self.update_and_format_task_list())
        self.list_button1_text = "✍"
        self.list_button1_command = self.init_update_popup

        self.list_button2_text = '🗑'
        self.list_button2_command = self.init_delete_popup

        # popup_window
        self.action_name = "Add / Update / Delete"
        self.label_init = "Enter a new task here"
        self.label_var = ObservableProperty(self.label_init)
        self.value_init = "5"
        self.value_var = ObservableProperty(self.value_init)
        self.value_options = ["1", "2", "3", "4", "5"]
        self.reset_popup_var()
        self.state_entry = "normal/readonly"
        self.button_left_text = "Cancel"
        self.button_left_command = None
        self.button_left_args = None
        self.button_right_text = "Add / Update / Delete"
        self.button_right_command = None
        self.button_right_args = None

        # reload
        self.notify_reload = False

    def update_and_format_task_list(self):
        self.task_list = self.controller.get_task_list()
        return [f"{task[0]}, {self.value_name} {task[1]}" for task in self.task_list]

    def reset_popup_var(self):
        self.label_var.set(self.label_init)
        self.value_var.set(self.value_init)
        self.state_entry = "normal"

    def set_popup_var(self, label, value, state="normal"):  # with selected task values
        self.label_var.set(label)  # self.tasks_list[item_id][0])
        self.value_var.set(value)  # self.tasks_list[item_id][1])
        self.state_entry = state

    def init_add_popup(self):
        self.reset_popup_var()
        self.init_popup("Add", lambda: self.handle_add_button())

    def init_update_popup(self, item_id):
        self.set_popup_var(self.task_list[item_id][0], self.task_list[item_id][1], "normal")
        self.init_popup("Update", lambda item=item_id: self.handle_update_button(item))

    def init_delete_popup(self, item_id):
        self.set_popup_var(self.task_list[item_id][0], self.task_list[item_id][1], "readonly")
        self.init_popup("Delete", lambda item=item_id: self.handle_delete_button(item))

    def init_popup(self, action_name, action_command):
        self.action_name = action_name
        self.button_left_text = "Cancel"
        self.button_left_command = lambda: self.handle_cancel_button()
        self.button_right_text = action_name
        self.button_right_command = action_command

    def handle_cancel_button(self):
        self.notify()

    def handle_add_button(self):
        if len(self.label_var.get()) > 0:
            self.controller.add_button(self.label_var.get(), self.value_var.get())

    def handle_update_button(self, item_id):
        if 0 <= item_id < len(self.task_list):
            if len(self.label_var.get()) > 0:
                # Find the corresponding task in the model and update it
                selected_task_tuple = self.task_list[item_id]
                self.controller.update_button(selected_task_tuple, self.label_var.get(), self.value_var.get())

    def handle_delete_button(self, item_id):
        if 0 <= item_id < len(self.task_list):
            # Find the corresponding task in the model and update it
            selected_task_tuple = self.task_list[item_id]
            self.controller.delete_button(selected_task_tuple)

    def notify(self, *args, **kwargs):
        """ Called when the file/db is modified by another process and when the data is modified by another view """
        if self.notify_reload is False:
            self.notify_reload = True
            self.observable_list.update(self.update_and_format_task_list())
            self.notify_reload = False


class Two_Columns_ViewModel:

    def __init__(self, task_model):
        # delegate all interactions with the model to the Controller
        self.controller = Two_Columns_Controller(task_model, self)
        self.task_list = []

        # common
        self.label_name = "Title:"
        self.value_name = "Priority:"

        # new item frame
        self.label_init = "Enter a new task here"
        self.label_var = ObservableProperty(self.label_init)
        self.value_init = "5"
        self.value_var = ObservableProperty(self.value_init)
        self.value_options = ["1", "2", "3", "4", "5"]
        self.button_left_text = "Add"  # "Add" / "Update"
        self.button_left_command = self.handle_add_update_button
        self.button_left_args = None
        self.button_left_state = "normal"   # "normal" / "disabled"
        self.button_right_text = "Delete"
        self.button_right_command = self.handle_delete_button
        self.button_right_args = None
        self.button_right_state = "disabled"   # "normal" / "disabled"

        # treeview frame
        self.observable_list = ObservableList(self.update_and_format_task_list())
        self.selected_item = None
        self.selected_index = None

        # reload
        self.notify_reload = False

    def update_and_format_task_list(self):
        self.task_list = self.controller.get_task_list()
        return [(str(task[0]),str(task[1])) for task in self.task_list]   # tree 2 colonnes

    def clear_input_fields(self):
        self.selected_item = None
        self.selected_index = None
        self.label_var.set(self.label_init)
        self.value_var.set(self.value_init)
        self.button_left_text= "Add"
        self.button_right_state = "disabled"

    def on_selection(self, selected_item, selected_index ):
        self.selected_item = selected_item
        self.selected_index = selected_index
        self.label_var.set(selected_item[0])
        self.value_var.set(selected_item[1])
        self.button_left_text = "Update"
        self.button_right_state = "normal"

    def handle_add_update_button(self):
        if self.selected_item:
            self.handle_update_button()
        else:
            self.handle_add_button()

    def handle_add_button(self):
        if len(self.label_var.get()) > 0:
            self.controller.add_button(self.label_var.get(), self.value_var.get())

    def handle_update_button(self):
        if len(self.label_var.get()) > 0:
            self.controller.update_button(self.task_list[self.selected_index], self.label_var.get(), self.value_var.get())

    def handle_delete_button(self):
        self.controller.delete_button(self.task_list[self.selected_index])

    def notify(self, *args, **kwargs):
        """ Called when the file/db is modified by another process and when the data is modified by another view """
        if self.notify_reload is False:
            self.notify_reload = True
            self.observable_list.update(self.update_and_format_task_list())
            self.clear_input_fields()
            self.notify_reload = False


class Two_Rows_ViewModel:

    def __init__(self, task_model):
        # delegate all interactions with the model to the Controller
        self.controller = Two_Rows_Controller(task_model, self)
        self.task_list = []

        # New Item frame
        self.button_text = "Add"
        self.button_command = self.handle_add_button

        # main frame
        self.update_task_list()
        self.label_list = ObservableList(self.format_label_list())
        self.value_list = ObservableList(self.format_value_list())

        # popup_window
        self.label_init = "Enter a new task here"
        self.label_var = ObservableProperty(self.label_init)
        self.value_init = "5"
        self.value_var = ObservableProperty(self.value_init)
        self.value_options = ["1", "2", "3", "4", "5"]
        self.reset_var()

        # reload
        self.notify_reload = False

    def update_task_list(self):
        self.task_list = self.controller.get_task_list()

    def format_label_list(self):
        return [str(task[0]) for task in self.task_list]

    def format_value_list(self):
        return [str(task[1]) for task in self.task_list]

    def reset_var(self):
        self.label_var.set(self.label_init)
        self.value_var.set(self.value_init)

    def handle_add_button(self):
        new_label = self.label_var.get()
        new_value = self.value_var.get()
        if len(self.label_var.get()) > 0:
            self.controller.add_button(new_label, new_value)
        self.reset_var()

    def update_delete_label(self, new_label_on_col, item_id):
        if 0 <= item_id < len(self.task_list):
            selected_task_tuple = self.task_list[item_id]
            same_value = selected_task_tuple[1]
            if len(new_label_on_col) > 0:
                self.controller.update_label(selected_task_tuple, new_label_on_col, same_value)
            else:
                self.controller.delete_label(selected_task_tuple)

    def update_value(self, new_value_on_col, item_id):
        if 0 <= item_id < len(self.task_list):
            selected_task_tuple = self.task_list[item_id]
            same_label = selected_task_tuple[0]
            self.controller.update_priority(selected_task_tuple, same_label, new_value_on_col)

    def notify(self, *args, **kwargs):
        """ Called when the file/db is modified by another process and when the data is modified by another view """
        if self.notify_reload is False:
            self.notify_reload = True
            self.update_task_list()
            self.label_list.update(self.format_label_list())
            self.value_list.update(self.format_value_list())
            self.notify_reload = False


class Bar_Chart_ViewModel:

    def __init__(self, task_model):
        # delegate all interactions with the model to the Controller
        self.controller = Bar_Chart_Controller(task_model, self)
        self.task_list = []

        # main frame
        self.observable_list = ObservableList(self.update_and_format_task_list())
        self.value_name = "Priority"
        self.value_options = [1, 2, 3, 4, 5]
        self.reversed_options = True    # like Priority
        self.message_no_item = "No task to display"

        # reload
        self.notify_reload = False

    def update_and_format_task_list(self):
        self.task_list = self.controller.get_task_list()
        return [(str(task[0]), str(task[1])) for task in self.task_list]  # (label, value) as string

    def notify(self, *args, **kwargs):
        """ Called when the file/db is modified by another process and when the data is modified by another view """
        if self.notify_reload is False:
            self.notify_reload = True
            self.observable_list.update(self.update_and_format_task_list())
            self.notify_reload = False
