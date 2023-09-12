# Task_Manager_3.py
import tkinter as tk

from Task_CRUD_Model import Task_CRUD_Model
from Task_Manager_1 import Task_Manager_1
from Task_Manager_2 import Task_Manager_2


if __name__ == "__main__":

    task_manager_1 = None
    task_manager_2 = None

    # TK allows different views but requests a single Tk instance
    window = tk.Tk()
    window.title("Task Manager 1 & 2")
    window.config(background="grey")
    window.minsize(width=430, height=280)

    def file_modified(*args, **kwargs):
        """ Called when the file is modified """
        if task_manager_1:
            task_manager_1.notify(*args, **kwargs)
        if task_manager_2:
            task_manager_2.notify(*args, **kwargs)

    task_model = Task_CRUD_Model(file_modified)  # Create a connection to the Model

    # Fill the list for demonstration purpose
    fill_the_list = True
    if fill_the_list:
        for i in range(20):
            task_model.create(f"Task {i + 1}", (i + 2) % 4 + 1)
    ###

    task_manager_1 = Task_Manager_1(window, task_model)
    task_manager_2 = Task_Manager_2(window, task_model)

    task_manager_2.run()
    task_manager_1.run()
