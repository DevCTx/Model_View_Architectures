from collections import defaultdict

from Observer_patterns.Observables import ObservableProperty, ObservableList

from Task_ViewModels_API import Bar_Chart_ViewModel_API
from Task_ViewModels_API import Two_Rows_ViewModel_API
from Task_ViewModels_API import Two_Columns_ViewModel_API
from Task_ViewModels_API import Button_List_ViewModel_API

from Task_Controller import Task_Controller


class Button_List_ViewModel(Button_List_ViewModel_API):

    def __init__(self, task_model):
        super().__init__()

        # delegate all interactions with the model to the Controller
        self.controller = Task_Controller(task_model, self.notify)
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
        self.refreshing = False

    def update_and_format_task_list(self):
        self.task_list = self.controller.read_tasks()
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
            self.controller.create_task(self.label_var.get(), self.value_var.get())

    def handle_update_button(self, item_id):
        if 0 <= item_id < len(self.task_list):
            if len(self.label_var.get()) > 0:
                # Find the corresponding task in the model and update it
                selected_task_tuple = self.task_list[item_id]
                self.controller.update_task(selected_task_tuple, self.label_var.get(), self.value_var.get())

    def handle_delete_button(self, item_id):
        if 0 <= item_id < len(self.task_list):
            # Find the corresponding task in the model and update it
            selected_task_tuple = self.task_list[item_id]
            self.controller.delete_task(selected_task_tuple)

    def refresh(self):
        self.refreshing = True
        self.observable_list.update(self.update_and_format_task_list())
        self.refreshing = False

    def notify(self, *args, **kwargs):
        """ Called when the file/db is modified by another process and when the data is modified by another view """
        if self.refreshing is False:
            self.refresh()

class Two_Columns_ViewModel(Two_Columns_ViewModel_API):

    def __init__(self, task_model):
        super().__init__()

        # delegate all interactions with the model to the Controller
        self.controller = Task_Controller(task_model, self.notify)
        self.task_list = []

        # common
        self.label_name = "Title:"
        self.value_name = "Priority:"

        # new item frame
        self.label_init = "Enter a new task here"
        self.value_init = "5"
        self.label_var = ObservableProperty(self.label_init)
        self.value_var = ObservableProperty(self.value_init)
        self.value_options = ["1", "2", "3", "4", "5"]
        self.button_left_text = "Add"  # "Add" / "Update"
        self.button_left_command = self.handle_add_update_button
        self.button_left_state = "normal"   # "normal" / "disabled"
        self.button_right_text = "Delete"
        self.button_right_command = self.handle_delete_button
        self.button_right_state = "disabled"   # "normal" / "disabled"

        # treeview frame
        self.label_value_tuple_list = ObservableList(self.update_and_format_task_list())
        self.selected_item_dict = defaultdict(tuple)

        # reload
        self.refreshing = False

    def update_and_format_task_list(self):
        self.task_list = self.controller.read_tasks()
        return [(str(task[0]), str(task[1])) for task in self.task_list]   # tree 2 colonnes

    def on_selected_items(self):
        if len(self.selected_item_dict) == 1:
            self.on_unique_selection()
        else:  # refuses multi selections or unselects the unique selection
            self.clear_input_fields()

    def on_unique_selection(self):  # selected_item, selected_index ):
        item_tuple = list(self.selected_item_dict.values())[0]
        self.label_var.set(item_tuple[0])
        self.value_var.set(item_tuple[1])
        self.button_left_text = "Update"
        self.button_right_state = "normal"

    def clear_input_fields(self):
        self.selected_item_dict.clear()
        self.label_var.set(self.label_init)
        self.value_var.set(self.value_init)
        self.button_left_text = "Add"
        self.button_right_state = "disabled"

    def handle_add_update_button(self):
        if len(self.selected_item_dict):
            self.handle_update_button()
        else:
            self.handle_add_button()

    def handle_add_button(self):
        if len(self.label_var.get()) > 0:
            self.controller.create_task(self.label_var.get(), self.value_var.get())

    def handle_update_button(self):
        if len(self.label_var.get()) > 0:
            item_index = list(self.selected_item_dict.keys())[0]
            self.controller.update_task(
                self.task_list[item_index],
                self.label_var.get(),
                self.value_var.get()
            )

    def handle_delete_button(self):
        item_index = list(self.selected_item_dict.keys())[0]
        self.controller.delete_task(self.task_list[item_index])

    def refresh(self):
        self.refreshing = True
        self.label_value_tuple_list.update(self.update_and_format_task_list())
        self.clear_input_fields()
        self.refreshing = False

    def notify(self, *args, **kwargs):
        """ Called when the file/db is modified by another process and when the data is modified by another view """
        if self.refreshing is False:
            self.refresh()


class Two_Rows_ViewModel(Two_Rows_ViewModel_API):

    def __init__(self, task_model):
        super().__init__()

        # delegate all interactions with the model to the Controller
        self.controller = Task_Controller(task_model, self.notify)
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
        self.refreshing = False

    def update_task_list(self):
        self.task_list = self.controller.read_tasks()

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
            self.controller.create_task(new_label, new_value)
        self.reset_var()

    def on_label_return(self, new_label_on_col, item_id):
        if 0 <= item_id < len(self.task_list):
            selected_task_tuple = self.task_list[item_id]
            same_value = selected_task_tuple[1]
            if len(new_label_on_col) > 0:   # Update
                self.controller.update_task(selected_task_tuple, new_label_on_col, same_value)
            else:   # Delete
                self.controller.delete_task(selected_task_tuple)

    def on_modified_value(self, new_value_on_col, item_id):
        if 0 <= item_id < len(self.task_list):
            selected_task_tuple = self.task_list[item_id]
            same_label = selected_task_tuple[0]
            self.controller.update_task(selected_task_tuple, same_label, new_value_on_col)

    def refresh(self):
        self.refreshing = True
        self.update_task_list()
        self.label_list.update(self.format_label_list())
        self.value_list.update(self.format_value_list())
        self.refreshing = False

    def notify(self, *args, **kwargs):
        """ Called when the file/db is modified by another process and when the data is modified by another view """
        if self.refreshing is False:
            self.refresh()


class Bar_Chart_ViewModel(Bar_Chart_ViewModel_API):

    def __init__(self, task_model):
        super().__init__()

        # delegate all interactions with the model to the Controller
        self.controller = Task_Controller(task_model, self.notify)
        self.task_list = []

        # main frame
        self.label_value_tuple_list = ObservableList(self.update_and_format_task_list())
        self.value_name = "Priority"
        self.value_options = [1, 2, 3, 4, 5]
        self.reversed_options = True    # like Priority
        self.no_item_message = "No task to display"

        # reload
        self.refreshing = False

    def update_and_format_task_list(self):
        self.task_list = self.controller.read_tasks()
        return [(str(task[0]), str(task[1])) for task in self.task_list]  # (label, value) as string

    def refresh(self):
        self.refreshing = True
        self.label_value_tuple_list.update(self.update_and_format_task_list())
        self.refreshing = False

    def notify(self, *args, **kwargs):
        """ Called when the file/db is modified by another process and when the data is modified by another view """
        if self.refreshing is False:
            self.refresh()