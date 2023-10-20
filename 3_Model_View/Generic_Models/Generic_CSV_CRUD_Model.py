"""
    Create a Generic CRUD Model for CSV File
"""
import csv
from typing import Callable

if __name__ == "__main__":  # To test the sample at the end of the file
    from Generic_CRUD_Model import Generic_CRUD_Model
else:  # if used as module
    from .Generic_CRUD_Model import Generic_CRUD_Model


class Generic_CSV_CRUD_Model(Generic_CRUD_Model):
    """
    Create a Generic CRUD Model for CSV File

    Fieldnames of the CSV file are based on the arguments of the 'object_type' __init__ method

    The arguments of the __init__ in the 'object_type' class must match the names of its attributes
    to work with Generic_CRUD_Model.

    The _set_file_objects and _get_file_objects will be called by Generic_CRUD_Model to set or get the
    object_list of 'object_type' to/from the file
    """

    def __init__(self, object_type: type, notify_function: Callable = None):
        # init the object_type, the field_names, the field_types, an object_list, the filename, call init_file_objects
        super().__init__(object_type, notify_function, "CSV")

    def _init_file_objects(self) -> None:
        try :
            self._get_file_objects()
        except FileNotFoundError :
            self._set_file_objects()

    def _set_file_objects(self) -> None:
        """ specific to CSV files """
        with open(self.filename, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=self.field_names)
            writer.writeheader()
            for object_item in self.object_list:
                writer.writerow(object_item.__dict__)

    def _get_file_objects(self) -> None:
        """ specific to CSV files """
        with open(self.filename, 'r', newline='') as file:
            reader = csv.DictReader(file, fieldnames=self.field_names)
            next(reader)  # skip the header
            csv_values_list = [tuple(csv_dict.values()) for csv_dict in reader]
            # Convert the values from CSV to the type of 'object_type'
            self._convert_to_object_list(csv_values_list)


if __name__ == "__main__":
    from datetime import datetime


    class Task:

        def __init__(self, title: str,
                     priority: int,
                     active: bool = True,
                     modified_on: datetime = datetime.now(),
                     weight: float = 1.0):
            """
            The arguments of __init__ must match the names of its attributes to work with Generic_CRUD_Model
            """
            self.title: str = title
            self.priority: int = priority
            self.active: bool = active
            self.modified_on: datetime = modified_on
            self.weight: float = weight

        def read_format(self):
            """ Optional: customizes the format for printing objects in the read list  """
            return tuple(self.__dict__.values())

        def __str__(self):
            """ Optional : Define the format to print as string """
            return f"{self.read_format()}"


    ### Added to share the Model between Views
    class Model_User:
        def __init__(self, model, notify_function: Callable):
            self.model = model
            self.notify_function = notify_function

        def notify(self, *args, **kwargs):
            self.notify_function(*args, **kwargs)
    ###

    task = Task("Sample", 3)
    print(task)
    # Output : ('Sample', 3, True, datetime.datetime(2023, 7, 25, 20, 57, 8, 549630), 1.0)

    # Create CRUD Model for Task objects with a CSV File
    tasks = Generic_CSV_CRUD_Model(Task, lambda *args, **kwargs: print(f"\nFileModifiedEvent : {args[1]}"))

    ### Added to share the Model between Views
    model_user1 = Model_User(tasks, lambda *args, **kwargs: print(f"User 1 notified"))
    tasks.add_observer(model_user1.notify)

    model_user2 = Model_User(tasks, lambda *args, **kwargs: print(f"User 2 notified"))
    tasks.add_observer(model_user2.notify)
    ###

    # Create a first task
    tasks.create("A first task", 3)
    print(tasks.read())
    # Output:
    # [('A first task', 3, True, datetime.datetime(2023, 7, 25, 20, 57, 8, 549630), 1.0)]

    # Create a second task
    tasks.create("A second task", 6, True, datetime.now(), 6.5)
    print(tasks.read())
    # Output:
    # [('A first task', 3, True, datetime.datetime(2023, 7, 25, 20, 57, 8, 549630), 1.0),
    # ('A second task', 6, True, datetime.datetime(2023, 7, 25, 20, 57, 8, 587785), 6.5)]

    # Update the second task
    tasks.update(1, "A modified task", 4, False, datetime.now(), 4.5)
    print(tasks.read())
    # Output:
    # [('A first task', 3, True, datetime.datetime(2023, 7, 25, 20, 57, 8, 549630), 1.0),
    # ('A modified task', 4, False, datetime.datetime(2023, 7, 25, 20, 57, 8, 597780), 4.5)]

    """
    Here is the 'Task.csv' file at this step :
    title,priority,active,modified_on,weight
    A first task,3,True,2023-07-25 20:57:08.549630,1.0
    A modified task,4,False,2023-07-25 20:57:08.597780,4.5
    """
    #
    # # Delete the first task
    # tasks.delete(0)
    # print(tasks.read())
    # # Output:
    # # [('A modified task', 4, False, datetime.datetime(2023, 7, 25, 20, 51, 7, 800344), 4.5)]
    #
    # # Delete the second task
    # tasks.delete(0)
    # print(tasks.read())
    # # Output: []

    """
    Here is the 'Task.csv' file at this step :
    title,priority,active,modified_on,weight
    """
