# Task_Manager.py
import tkinter as tk

from Task_CRUD_Model import Task_CRUD_Model
from Task_Views import Two_Columns_View
from Task_Views import Two_Rows_View
from Task_Views import Bar_Chart_View
from Task_Views import Button_List_View


if __name__ == "__main__":

    two_rows_view = None
    bar_chart_view = None
    button_list_view = None
    two_columns_view = None

    # TK allows different views but requests a single Tk instance
    window = tk.Tk()
    window.title("Task Manager")
    window.config(background="grey")

    def file_modified(*args, **kwargs):
        """ Called when the file is modified """
        if two_rows_view:
            two_rows_view.notify(*args, **kwargs)
        if bar_chart_view:
            bar_chart_view.notify(*args, **kwargs)
        if button_list_view:
            button_list_view.notify(*args, **kwargs)
        if two_columns_view:
            two_columns_view.notify(*args, **kwargs)

    task_model = Task_CRUD_Model(file_modified)  # Create a connection to the Model

    # Fill the list for demonstration purpose
    fill_the_list = False
    if fill_the_list:
        for i in range(10):
            task_model.create(f"Task {i + 1}", (i + 2) % 4 + 1)
    ###

    two_rows_view = Two_Rows_View(window, task_model)
    bar_chart_view = Bar_Chart_View(window, task_model)
    button_list_view = Button_List_View(window, task_model)
    two_columns_view = Two_Columns_View(window, task_model)

    button_list_view.grid(column=0, row=0, sticky=tk.NSEW)
    two_columns_view.grid(column=1, row=0, sticky=tk.NSEW)
    bar_chart_view.grid(column=2, row=0, sticky=tk.NSEW)
    two_rows_view.grid(column=0, columnspan=3, row=1, sticky=tk.NSEW)

    window.mainloop()
