import os
import sys
import tkinter as tk
from tkinter import ttk

# Update sys.path to include the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from Observer_patterns.Observables import ObservableProperty, ObservableList


class BoundTk_Variable(tk.Variable):
    """ Sets a tk.Variable bound in both directions to a class property  """

    def __init__(self, name, observable_property: ObservableProperty, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        # calls _update_property on tk.Variable modification
        self.trace_add('write', self._update_property)
        # calls _update_variable on property modification
        self._property = observable_property.bind_property(self._update_tk_variable)
        # init the variable with the property value
        self._update_tk_variable()

    def unbind_tk_var(self):
        """ should be used on_closing window """
        self._property.unbind_property()

    def _update_property(self, *args):
        """ update the property with the variable value if different """
        value_property = self._property.get()
        value_variable = self.get()
        if value_property != value_variable:
            self._property.set(value_variable)

    def _update_tk_variable(self):
        """ update the variable with the property value if different """
        value_property = self._property.get()
        value_variable = self.get()
        if value_variable != value_property:
            self.set(value_property)


class BoundTk_ListVar(list):
    """ Sets a list of BoundTkVariable bound in both directions to a list of class properties """

    def __init__(self, name, list_type: type(BoundTk_Variable),
                 observable_list: ObservableList, master, on_list_modif=None):
        super().__init__()
        self.name = name
        self.list_type = list_type
        self.master = master
        self.on_list_size_modification = on_list_modif

        # calls _update_tk_list on list modification
        self._property_list = observable_list.bind_list(self._update_tk_list)
        for i, _property in enumerate(self._property_list) :
            self.append( self.list_type(f"{self.name}_{i}",_property, self.master) )

    def _update_tk_list(self):
        print(f"\n{self.name} _update_tk_list : property_list size changed")
        for _tk_variable in self:
            _tk_variable.unbind_tk_var()   # ObservableProperty unbind
        self.clear()
        for i, _property in enumerate(self._property_list) :
            self.append( self.list_type(f"{self.name}_{i}",_property, self.master) )
        if self.on_list_size_modification is not None:
            self.on_list_size_modification()

    def __repr__(self):
        return repr([item.get() for item in self])

    def unbind_tk_list(self):
        """ should be used on_closing window """
        for _tk_variable in self:
            _tk_variable.unbind_tk_var()   # ObservableProperty unbind
        print(f"\n{self.name} unbind_list")
        self._property_list.unbind_list()


class BoundTk_StringVar(BoundTk_Variable, tk.StringVar):
    """ Sets a StringVar bound in both directions to a class property """

    def __init__(self, name, observable_property : ObservableProperty, *args, **kwargs):
        super().__init__(name, observable_property, *args, **kwargs)


class BoundTk_IntVar(BoundTk_Variable, tk.IntVar):
    """ Sets a IntVar bound in both directions to a class property  """

    def __init__(self, name, observable_property, *args, **kwargs):
        super().__init__(name, observable_property, *args, **kwargs)

    def get(self) -> int or None:
        """ Set None as default if entered value is not formatted as Integer """
        try:
            return tk.IntVar.get(self)
        except tk.TclError:
            return None


class BoundTk_TreeView(ttk.Treeview):
    """ Sets a ttk.Treeview bound to a list of class properties (one way only) """

    def __init__(self, name, observable_list: ObservableList,
                 master, columns, show, *args, **kwargs):
        super().__init__(master=master, columns=columns, show=show, *args, **kwargs)
        self.name = name
        self.master = master
        self.columns = columns

        # calls _update_tk_list on list modification
        self._property_list = observable_list.bind_list(self._update_tk_whole_treeview)
        self._update_tk_whole_treeview()

    def _update_tk_whole_treeview(self):
        for i, _property in enumerate(self._property_list) :
            _property.unbind_property()      # ObservableProperty unbind
        self.delete(*self.get_children())

        # Insert item from the model
        for i, _property in enumerate(self._property_list) :
            _property.bind_property(lambda index=i: self._update_tk_treeview_item(index))

            # insert : 'tags' converts the values to compatible str
            self.insert( parent="", index=tk.END, values=_property.get(), tags=_property.get())

    def _update_tk_treeview_item(self, index):
        if 0 <= index < len(self.get_children()):
            self.item( item=self.get_children()[index],
                       values=self._property_list[index].get(),
                       tags=self._property_list[index].get())

    def unbind_tk_treeview(self):
        """ should be used on_closing window """
        for _property in self._property_list:
            _property.unbind_property()  # ObservableProperty unbind
        self._property_list.unbind_list()



if __name__ == "__main__":

    from datetime import datetime

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
            del self.tasks_list[selected_item]
            self.notify()

        def read(self):
            print(f"reads tasks from the model : {self.tasks_list=}")
            return self.tasks_list

        def notify(self):
            for observer in self.observers:
                observer.notify()


    class ViewModel_Simulator:

        def __init__(self, model):
            # delegate all interactions with the model to the Controller
            self.model = model
            self.task_list = []
            self.observable_prop = ObservableProperty("Priority: ")
            self.observable_list = ObservableList(self.update_and_format_task_list())

        def update_and_format_task_list(self):
            self.task_list = self.model.read()
            return [f"{task[0]}, {self.observable_prop.get()} {task[1]}" for task in self.task_list]

        def notify(self, *args, **kwargs):
            print("notify observable_list.update : update_and_format_task_list")
            self.observable_list.update(self.update_and_format_task_list())

    # MODEL
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from Task_CRUD_Model import Task_CRUD_Model

    def file_modified(*args, **kwargs):
        """ Called when the file is modified """
        if view_model_sim:
            view_model_sim.notify(*args, **kwargs)

    model_sim = Task_CRUD_Model(file_modified)  # Create a connection to the Model
    # model_sim = Model_Simulator()

    # VIEW MODEL
    view_model_sim = ViewModel_Simulator(model_sim)

    # APP
    window = tk.Tk()
    window.title("Task Manager 1")
    window.config(background="grey")

    print(f"\n{view_model_sim.observable_prop.get()=}")
    value_tk_var = BoundTk_StringVar("value_tk_var", view_model_sim.observable_prop, window)
    tk.Entry(window, textvariable=value_tk_var).pack()

    def display_value_tk_list():
        # Tkinter only accepts 3 geometry managers: pack(), grid() and place()
        #
        # pack() does not accept an index, so it assembles the blocks one after the other in the order of arrival(FIFO),
        # which does not really represent the value_tk_list order if a modification appears in the middle from the list
        #
        # grid() needs to redefine the location of all subsequent elements so this is only effective if the change
        # appears near the end
        #
        # place() does not take care of any particular order and places the widget in a location defined by coordinate
        # so will also force all others to be modified if they overlap.
        #
        # based on this observation, it appears more efficient to simply destroy all the widgets from the list
        # and recreate them for a new display
        #
        print("display_value_tk_list")
        for widget in value_tk_list.master.winfo_children():
            widget.destroy()
        for value_tk_item in value_tk_list:
            tk.Entry(value_tk_list.master, textvariable=value_tk_item).pack()
        value_tk_list.master.update()

    print(f"\n{view_model_sim.observable_list=}")
    frame = tk.LabelFrame(master=window, text="List of Entries", labelanchor=tk.NW)
    frame.pack()

    value_tk_list = BoundTk_ListVar(
        name="value_tk_list",
        list_type=BoundTk_StringVar,
        observable_list=view_model_sim.observable_list,
        master=frame,
        on_list_modif=display_value_tk_list
    )
    display_value_tk_list()

    def on_window_close():
        value_tk_var.unbind_tk_var()
        value_tk_list.unbind_tk_list()
        window.quit()

    # Clean up the binds before closing the window
    window.protocol("WM_DELETE_WINDOW", on_window_close)

    window.mainloop()

    print(f"\n{view_model_sim.observable_prop.get()=}")
    print(f"\n{value_tk_var.get()=}")
    print(f"\n{view_model_sim.observable_list=}")
    print(f"\n{value_tk_list=}")




