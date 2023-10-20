# Task_Manager.py
import tkinter as tk

from Task_CRUD_Model import Task_CRUD_Model
from Task_Views import Two_Columns_View
from Task_Views import Two_Rows_View
from Task_Views import Bar_Chart_View
from Task_Views import Button_List_View


if __name__ == "__main__":

    task_manager_1 = None
    task_manager_2 = None
    task_manager_3 = None
    task_manager_4 = None

    # TK allows different views but requests a single Tk instance
    window = tk.Tk()
    window.title("Task Manager")
    window.config(background="grey")

    def file_modified(*args, **kwargs):
        """ Called when the file is modified """
        if task_manager_1:
            task_manager_1.notify(*args, **kwargs)
        if task_manager_2:
            task_manager_2.notify(*args, **kwargs)
        if task_manager_3:
            task_manager_3.notify(*args, **kwargs)
        if task_manager_4:
            task_manager_4.notify(*args, **kwargs)

    task_model = Task_CRUD_Model(file_modified)  # Create a connection to the Model

    # Fill the list for demonstration purpose
    fill_the_list = True
    if fill_the_list:
        for i in range(10):
            task_model.create(f"Task {i + 1}", (i + 2) % 4 + 1)
    ###

    task_manager_1 = Two_Rows_View(window, task_model)
    task_manager_2 = Bar_Chart_View(window, task_model)
    task_manager_3 = Button_List_View(window, task_model)
    task_manager_4 = Two_Columns_View(window, task_model)

    window.mainloop()
