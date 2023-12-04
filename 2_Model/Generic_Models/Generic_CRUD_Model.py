"""
    Create a Generic CRUD Model
"""
import inspect
import os
import sys
from datetime import datetime
from time import sleep
from typing import get_type_hints

from watchdog.observers import Observer

# Update sys.path to include the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from Observer_patterns.FileObserverHandler import FileObserverHandler


class Generic_CRUD_Model:
    """
    Generic CRUD Model for 'object_type' type objects to/from 'file_type' file

    The arguments of the __init__ method in the 'object_type' class must match the names of its attributes
    """

    def __init__(self, object_type: type, on_modified: callable = None, file_extension: str = None):

        # check if object_type is a class
        if not inspect.isclass(object_type):
            raise TypeError(f"'{object_type}' is not a class.")
        self.object_type = object_type

        # and if 'object_type' has an __init__ method
        if inspect.isclass(object_type) and "__init__" in dir(object_type):

            # get the field_names and field_types of the 'object_type' from the __init__ arguments
            constructor_annotations = get_type_hints(object_type.__init__)
            self.field_names = list(constructor_annotations.keys())
            self.field_types = list(constructor_annotations.values())

        else:
            raise TypeError(f"'{object_type}' must have a __init__ function to work with {self.__class__.__name__}")

        # and create a list of object_type in memory
        self.object_list: list[object_type] = []

        # The object is defined as an Observable so it can be used by different views in the same program
        # the 'notify' function will be used to notify the registered observers when needed (create/update/delete)
        super().__init__()

        self.filename = None
        self.file_observer = None
        self.file_observer_handler = None

        # If the use of a file is requested
        if file_extension is not None:
            # check is file_extension is a string
            if not isinstance(file_extension, str):
                raise TypeError(f"'{file_extension}' is not a string.")
            self.filename = f"{self.object_type.__name__}.{file_extension.lower()}"
            self._on_file_modified = on_modified
            self._init_file_objects()

            # The object is also defined as a File Observer, so the file can be shared by different programs
            # '_on_file_modified' will be called each time it receives a notification
            file_abspath = os.path.abspath(self.filename)
            self.file_observer_handler = FileObserverHandler(file_abspath, self._on_file_modified_checking_timestamp)
            self.file_observer = Observer()
            self.file_observer.schedule(self.file_observer_handler, path=os.path.dirname(file_abspath), recursive=False)
            self.file_observer.start()

            self.last_modified_timestamp = None  # Will be used to check if the file has been modified from outside

    def __del__(self) -> None:
        if self.file_observer is not None:
            self.file_observer.stop()    # Remove the observer from FileSystemEventHandler
            self.file_observer.join()    # Wait for the end of the thread
        if self.file_observer_handler:
            self.file_observer_handler.stop()  # Stop the observer handler


    def _init_file_objects(self) -> None:
        """ Can be overriden to init the file/db to store the 'object_type' objects """
        ...

    def _set_file_objects_with_last_timestamp(self) -> None:
        """ Equivalent to an inherited decorator for the classes which override set_file_objects """
        self._set_file_objects()
        if self.filename:
            self.last_modified_timestamp = os.path.getmtime(self.filename)

    def _set_file_objects(self) -> None:
        """ Can be overriden to set the object_list of 'object_type' into the file/db """
        ...

    def _get_file_objects_with_last_timestamp(self) -> None:
        """ Equivalent to an inherited decorator for the classes which override set_file_objects """
        self._get_file_objects()
        if self.filename :
            self.last_modified_timestamp = os.path.getmtime(self.filename)

    def _get_file_objects(self) -> None:
        """ Can be overriden to get the object_list of 'object_type' from the file/db """
        ...

    def _on_file_modified_checking_timestamp(self, *args, **kwargs) -> None:
        """ Equivalent to an inherited decorator for the function/method _on_file_modified """
        if self.filename:
            # Check if the timestamp of the last modification is the same that the one we already got
            sleep(0.1)  # To let the file have the time to be stored properly before taking the modified timestamp
            current_timestamp = os.path.getmtime(self.filename)
            creation_timestamp = os.path.getctime(self.filename)
            if current_timestamp != self.last_modified_timestamp and current_timestamp != creation_timestamp:
                if self._on_file_modified is not None :
                    self._on_file_modified(self, *args, **kwargs)

    def _convert_to_object_list(self, object_list):
        self.object_list = []
        for object_item in object_list:
            object_dict = {}
            for idx, object_field in enumerate(object_item):
                try:
                    if self.field_types[idx] is datetime:
                        field_value = datetime.strptime(object_field, '%Y-%m-%d %H:%M:%S.%f')
                    elif self.field_types[idx] is bool:
                        field_value = False if (object_field == 'False'
                                                or object_field is False
                                                or object_field == 0) else True
                    else:
                        field_value = self.field_types[idx](object_field)
                except (SyntaxError, ValueError):
                    raise TypeError(f"Need a converter for {self.field_types[idx]}")
                object_dict.update({self.field_names[idx]: field_value})
            self.object_list.append(self.object_type(**object_dict))

    def _check_index(self, list_idx):
        if len(self.object_list) <= 0:
            raise ValueError(f"No {self.object_type.__name__} in the list of {self.filename}")

        if list_idx < 0 or list_idx >= len(self.object_list):
            raise ValueError(f"list_idx must be between 0 and {len(self.object_list) - 1}")

    def _check_args(self, *args):
        for i, (arg, field_type_expected) in enumerate(zip(args, self.field_types)):
            if not isinstance(arg, field_type_expected):
                raise ValueError(f"Incorrect type for argument '{self.field_names[i]}':{self.field_types[i]} expected")

    def create(self, *args) -> None:
        """ Create a new 'object_type' to the end of the file """
        self._check_args(*args)
        self._get_file_objects_with_last_timestamp()
        object_item = self.object_type(*args)
        self.object_list.append(object_item)
        self._set_file_objects_with_last_timestamp()

    def read(self) -> list:
        """ Return a list of tuple containing the values of 'object_type' objects """
        self._get_file_objects_with_last_timestamp()

        # Should not be attached to Generic_CRUD_Model but to the 'object_type' class
        def read_format(object_item):
            """ Can be overridden in object_type to customize the format of objects in the read list  """
            return tuple(object_item.__dict__.values())

        return [object_item.read_format() if hasattr(object_item, "read_format")
                else read_format(object_item) for object_item in self.object_list]

    def update(self, list_idx: int, *args) -> None:
        """ Update all the values of the 'object_type' at the list_idx in the list of the file """
        self._check_args(*args)
        self._get_file_objects_with_last_timestamp()
        self._check_index(list_idx)
        self.object_list[list_idx] = self.object_type(*args)
        self._set_file_objects_with_last_timestamp()

    def delete(self, list_idx: int) -> None:
        """ Delete the 'object_type' at the list_idx in the list of the file """
        self._get_file_objects_with_last_timestamp()
        self._check_index(list_idx)
        del self.object_list[list_idx]
        self._set_file_objects_with_last_timestamp()


if __name__ == "__main__":

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


    task = Task("Sample", 3)
    print(task)
    # Output : ('Sample', 3, True, datetime.datetime(2023, 7, 25, 20, 48, 22, 702207), 1.0)

    # Create CRUD Model for Task objects with a CSV File
    tasks = Generic_CRUD_Model(Task)

    # Create a first task
    tasks.create("A first task", 3)
    # Output:
    # [('A first task', 3, True, datetime.datetime(2023, 7, 25, 20, 48, 22, 702207), 1.0)]

    # Create a second task
    tasks.create("A second task", 6, True, datetime.now(), 6.5)
    print(tasks.read())
    # Output:
    # [('A first task', 3, True, datetime.datetime(2023, 7, 25, 20, 48, 22, 702207), 1.0),
    # ('A second task', 6, True, datetime.datetime(2023, 7, 25, 20, 48, 22, 736206), 6.5)]

    # Update the second task
    tasks.update(1, "A modified task", 4, False, datetime.now(), 4.5)
    print(tasks.read())
    # Output:
    # [('A first task', 3, True, datetime.datetime(2023, 7, 25, 20, 48, 22, 702207), 1.0),
    # ('A modified task', 4, False, datetime.datetime(2023, 7, 25, 20, 48, 22, 755209), 4.5)]

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
