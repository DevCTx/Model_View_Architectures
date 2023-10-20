import traceback
from datetime import datetime


class Main_Controller:

    def __init__(self):
        self.tasks = None
        if type(self) is Main_Controller:
            raise TypeError("Main_Controller cannot be instantiated directly, must be inherited")

    def _get_read_index(self, selected_item):
        try:
            selected_tuple = (
                selected_item[0],
                int(selected_item[1]),
                datetime.strptime(selected_item[2], '%Y-%m-%d %H:%M:%S.%f'),
            )
        except (IndexError, ValueError):
            print("Error between selected item and model", traceback.format_exc())
        else:
            for idx, read_tuple in enumerate(self.tasks.read()):
                if read_tuple == selected_tuple:
                    return idx
        return None

    def _create_task(self, task_name, task_priority):
        self.tasks.create(task_name, int(task_priority))

    def _update_task(self, selected_item, new_task_name, new_task_priority):
        read_index = self._get_read_index(selected_item)
        if read_index is not None:
            self.tasks.update(read_index, new_task_name, int(new_task_priority))

    def _delete_task(self, selected_item):
        read_index = self._get_read_index(selected_item)
        if read_index is not None:
            self.tasks.delete(read_index)

    def _read_tasks(self):
        return [(task[0], str(task[1]), task[2].strftime("%Y-%m-%d %H:%M:%S.%f")) for task in self.tasks.read()]


class Button_List_Controller(Main_Controller):

    def __init__(self, task_model, view):
        super().__init__()
        self.tasks = task_model
        self.tasks.add_observer(view.notify)

    def add_button(self, task_name, task_priority):
        self._create_task(task_name, int(task_priority))

    def update_button(self, selected_item, new_task_name, new_task_priority):
        self._update_task(selected_item, new_task_name, new_task_priority)

    def delete_button(self, selected_item):
        self._delete_task(selected_item)

    def update_tasks_for_button_list(self):
        return self._read_tasks()


class Two_Columns_Controller(Main_Controller):

    def __init__(self, task_model, view):
        super().__init__()
        self.tasks = task_model
        self.tasks.add_observer(view.notify)

    def add_button(self, task_name, task_priority):
        self._create_task(task_name, int(task_priority))

    def update_button(self, selected_item, new_task_name, new_task_priority):
        self._update_task(selected_item, new_task_name, new_task_priority)

    def delete_button(self, selected_item):
        self._delete_task(selected_item)

    def update_tasks_for_tree(self):
        return self._read_tasks()


class Two_Rows_Controller(Main_Controller):

    def __init__(self, task_model, view):
        super().__init__()
        self.tasks = task_model
        self.tasks.add_observer(view.notify)

    def add_button(self, task_name, task_priority):
        self._create_task(task_name, int(task_priority))

    def update_label(self, selected_item, new_task_name, same_task_priority):
        self._update_task(selected_item, new_task_name, same_task_priority)

    def delete_label(self, selected_item):
        self._delete_task(selected_item)

    def update_priority(self, selected_item, same_task_name, new_task_priority):
        self._update_task(selected_item, same_task_name, new_task_priority)

    def update_tasks_for_table(self):
        return self._read_tasks()


class Bar_Chart_Controller(Main_Controller):

    def __init__(self, task_model, view):
        super().__init__()
        self.tasks = task_model
        self.tasks.add_observer(view.notify)

    def update_tasks_for_barchart(self):
        return self._read_tasks()


if __name__ == "__main__":

    from Task_CRUD_Model import Task_CRUD_Model

    # Simulate a view (only need a notify function)
    class View_Simulator:
        def notify(self, *args, **kwargs):
            print(f"{self} notified for a refresh\n", *args, **kwargs)

    my_view = View_Simulator()

    # Create the model
    def file_modified(*args, **kwargs):
        if my_view:
            my_view.notify(*args, **kwargs)

    my_task_model = Task_CRUD_Model(file_modified)  # which defines the Generic_CRUD_Model to use

    # Create the controller of the view using the model
    controller = Two_Columns_Controller(my_task_model, View_Simulator())
    controller2 = Bar_Chart_Controller(my_task_model, View_Simulator())

    # Output:
    # View notified for a refresh

    # Create a first task
    controller.add_button("A first task", "3")
    task_list = controller.update_tasks_for_tree()
    print(task_list, end='\n\n')
    # Output:
    # [('A first task', '3', '2023-09-19 16:43:55.647454')]
    # View notified for a refresh

    # Create a second task
    controller.add_button("A second task", "6")
    task_list = controller.update_tasks_for_tree()
    print(task_list, end='\n\n')
    # Output:
    # [('A first task', '3', '2023-09-19 16:43:55.647454'),
    # ('A second task', '6', '2023-09-19 16:43:55.670727')]
    # View notified for a refresh

    # Update the second task
    item_tuple = task_list[1]
    controller.update_button(item_tuple, "A modified task", 4)
    task_list = controller.update_tasks_for_tree()
    print(task_list, end='\n\n')
    # Output:
    # [('A first task', '3', '2023-09-19 16:43:55.647454'),
    # ('A modified task', '4', '2023-09-19 16:43:55.681733')]
    # View notified for a refresh

    # Delete the first task
    item_tuple = task_list[0]
    controller.delete_button(item_tuple)
    task_list = controller.update_tasks_for_tree()
    print(task_list, end='\n\n')
    # Output:
    # [('A modified task', '4', '2023-09-19 16:43:55.681733')]
    # View notified for a refresh

    # # Delete the second task
    # item_tuple = (task_list[0][0], str(task_list[0][1]), task_list[0][2].strftime("%Y-%m-%d %H:%M:%S.%f"))
    # controller.delete_button(item_tuple)
    # task_list = controller.get_tasks()
    # print(task_list, end='\n\n')
    # # Output: []
    # # View notified for a refresh

    if my_task_model.filename:
        print("\033[93m" + f"*** TRY TO MODIFY '{my_task_model.filename}' " +
              "WHILE THE FILE REFRESH EVERY SECOND ***" + "\033[0m" + "\n")
        import time

        try:
            while True:
                time.sleep(1)
                task_list = controller.update_tasks_for_tree()
                print(task_list, end='\n\n')
        except KeyboardInterrupt:
            pass
    else:
        print("\033[93m" + f"*** NO FILES OR DATABASE ***" + "\033[0m" + "\n")
