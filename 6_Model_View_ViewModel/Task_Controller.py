import atexit
import traceback
from datetime import datetime


class Task_Controller:

    def __init__(self, task_model, observer: callable):
        super().__init__()
        self.tasks = task_model
        self.observer = observer
        self.tasks.add_observer(self.observer)
        atexit.register(self.on_closing)

    def on_closing(self):
        self.tasks.remove_observer(self.observer)

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

    # replace add_button
    def create_task(self, task_name, task_priority):
        self.tasks.create(task_name, int(task_priority))

    # replace update_button / update_label / update_priority
    def update_task(self, selected_item, new_task_name, new_task_priority):
        read_index = self._get_read_index(selected_item)
        if read_index is not None:
            self.tasks.update(read_index, new_task_name, int(new_task_priority))

    # replace delete_button / delete_label
    def delete_task(self, selected_item):
        read_index = self._get_read_index(selected_item)
        if read_index is not None:
            self.tasks.delete(read_index)

    # replace get_task_list
    def read_tasks(self):
        return [(task[0], str(task[1]), task[2].strftime("%Y-%m-%d %H:%M:%S.%f")) for task in self.tasks.read()]



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
    controller = Task_Controller(my_task_model, my_view.notify)  # Two_Columns_Controller
    controller2 = Task_Controller(my_task_model, my_view.notify)   # Bar_Chart_Controller

    # Output:
    # View notified for a refresh

    # Create a first task
    controller.create_task("A first task", "3")  # add_button("A first task", "3")
    task_list = controller.read_tasks()  # get_task_list()
    print(task_list, end='\n\n')
    # Output:
    # [('A first task', '3', '2023-09-19 16:43:55.647454')]
    # View notified for a refresh

    # Create a second task
    controller.create_task("A second task", "6") # add_button("A second task", "6")
    task_list = controller.read_tasks()      # get_task_list()
    print(task_list, end='\n\n')
    # Output:
    # [('A first task', '3', '2023-09-19 16:43:55.647454'),
    # ('A second task', '6', '2023-09-19 16:43:55.670727')]
    # View notified for a refresh

    # Update the second task
    item_tuple = task_list[1]
    controller.update_task(item_tuple, "A modified task", 4)  # update_button(item_tuple, "A modified task", 4)
    task_list = controller.read_tasks()  # get_task_list()
    print(task_list, end='\n\n')
    # Output:
    # [('A first task', '3', '2023-09-19 16:43:55.647454'),
    # ('A modified task', '4', '2023-09-19 16:43:55.681733')]
    # View notified for a refresh

    # Delete the first task
    item_tuple = task_list[0]
    controller.delete_task(item_tuple)    # delete_button(item_tuple)
    task_list = controller.read_tasks()  # get_task_list()
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
                task_list = controller.read_tasks()  # get_task_list()
                print(task_list, end='\n\n')
        except KeyboardInterrupt:
            pass
    else:
        print("\033[93m" + f"*** NO FILES OR DATABASE ***" + "\033[0m" + "\n")
