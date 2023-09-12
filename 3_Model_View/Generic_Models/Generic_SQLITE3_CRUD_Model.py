"""
    Create a Generic CRUD Model for SQLITE3 File
"""
import sqlite3
from typing import Callable
from datetime import datetime   # used in _type_to_sqlite3

if __name__ == "__main__":  # To test the sample at the end of the file
    from Generic_CRUD_Model import Generic_CRUD_Model
else:   # if used as module
    from .Generic_CRUD_Model import Generic_CRUD_Model


class Generic_SQLITE3_CRUD_Model(Generic_CRUD_Model):
    """
    Create a Generic CRUD Model for SQLITE3 Database

    Fieldnames of the SQLITE3 table are based on the arguments of the 'object_type' __init__ method

    The arguments of the __init__ in the 'object_type' class must match the names of its attributes
    to work with Generic_CRUD_Model.

    The _set_file_objects and _get_file_objects will be called by Generic_CRUD_Model to set or get the
    object_list of 'object_type' to/from the database
    """

    def __init__(self, object_type: type, notify_function : Callable = None): #, drop_table_if_exists: bool = False):
        self.db = None
        self.cursor = None
        #self.drop_table_if_exists = drop_table_if_exists

        # init the object_type, the field_names, the field_types, an object_list, the filename, call init_file_objects
        super().__init__(object_type, notify_function, "SQLITE3")
        # The system will notify the changes on the .sqlite3 file but not on the specific 'object_type' table.
        # For another use of this sqlite3 database, a better notification mechanism might be needed to be more accurate.

    def _init_file_objects(self):
        self.db = sqlite3.connect(self.filename)
        self.cursor = self.db.cursor()
        sqlite3_mapping = {
            'int': 'INTEGER NOT NULL',
            'bool': 'INTEGER NOT NULL',  # No bool type, (0 for False, 1 for True)
            'str': 'TEXT NOT NULL',
            'float': 'REAL NOT NULL',
            'datetime': 'TEXT NOT NULL',
        }
        field_pairs = [z for z in zip(self.field_names, self.field_types)]
        field_list = [f"{field_name} {sqlite3_mapping[field_type.__name__]}" for (field_name, field_type) in
                      field_pairs]

        # if self.drop_table_if_exists:
        #     statement = f"DROP TABLE IF EXISTS {self.object_type.__name__}"
        #     self.cursor.execute(statement)

        statement = f"CREATE TABLE IF NOT EXISTS {self.object_type.__name__} ({', '.join(field_list)})"
        self.cursor.execute(statement)
        self.db.commit()

        self._get_file_objects_with_last_timestamp()

    def _get_file_objects(self):
        """ Get the object_list of 'object_type' from the sqlite3 database """
        statement = f"SELECT * FROM {self.object_type.__name__}"
        sqlite3_values_list = [sqlite3_item for sqlite3_item in self.cursor.execute(statement)]
        # Convert the values from SQLITE3 to the type of 'object_type'
        self._convert_to_object_list(sqlite3_values_list)

    @staticmethod
    def _type_to_sqlite3(v):
        """ Convert the type of 'object_type' to compatible SQLITE3 type """
        if isinstance(v, int):
            return str(v)
        elif isinstance(v, float):
            return str(v)
        elif isinstance(v, bool):
            return str(v)
        elif isinstance(v, str):
            return f"'{v}'"
        elif isinstance(v, datetime):
            return f"'{v.strftime('%Y-%m-%d %H:%M:%S.%f')}'"
        else:
            raise TypeError(f"Converter for {type(v)} needed")

    def create(self, *args) -> None:
        """ Create a new 'object_type' in the database """
        self._check_args(*args)
        # Convert into a 'object_type' object before to store in database to get the possible default values
        object_item = self.object_type(*args)
        compatible_object_item_values = [self._type_to_sqlite3(v) for v in object_item.__dict__.values()]

        statement = f"INSERT INTO {self.object_type.__name__} " \
                    f"({', '.join(object_item.__dict__.keys())}) " \
                    f"VALUES ({', '.join(compatible_object_item_values)})"
        self.cursor.execute(statement)
        self.db.commit()

        self._get_file_objects_with_last_timestamp()

        ### Added to share the Model between Views
        self.notify_observers()
        ###


    def update(self, list_idx: int, *args) -> None:
        """ Update all the values of the 'object_type' at the list_idx in the list of the file """
        self._check_index(list_idx)
        object_old = self.object_list[list_idx]
        compatible_object_old_values = [self._type_to_sqlite3(v) for v in object_old.__dict__.values()]

        self._check_args(*args)
        # Convert into a 'object_type' object before to store in database to get the possible default values
        object_new = self.object_type(*args)
        compatible_object_new_values = [self._type_to_sqlite3(v) for v in object_new.__dict__.values()]

        statement = f"UPDATE {self.object_type.__name__} SET " \
                    f"({', '.join(object_new.__dict__.keys())})=({', '.join(compatible_object_new_values)}) " \
                    f"WHERE ({', '.join(object_old.__dict__.keys())})=({', '.join(compatible_object_old_values)})"
        self.cursor.execute(statement)
        self.db.commit()

        self._get_file_objects_with_last_timestamp()

        ### Added to share the Model between Views
        self.notify_observers()
        ###

    def delete(self, list_idx: int) -> None:
        """ Delete the 'object_type' at the list_idx in the list of the file """
        self._check_index(list_idx)
        # Convert into a 'object_type' object before to store in database to get the possible default values
        object_item = self.object_list[list_idx]
        compatible_object_item_values = [self._type_to_sqlite3(v) for v in object_item.__dict__.values()]

        statement = f"DELETE FROM {self.object_type.__name__} " \
                    f"WHERE ({', '.join(object_item.__dict__.keys())})=({', '.join(compatible_object_item_values)})"
        self.cursor.execute(statement)
        self.db.commit()

        self._get_file_objects_with_last_timestamp()

        ### Added to share the Model between Views
        self.notify_observers()
        ###


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
    # Output : ('Sample', 3, True, datetime.datetime(2023, 7, 25, 21, 0, 14, 18657), 1.0)

    # Create CRUD Model for Task objects with a CSV File
    tasks = Generic_SQLITE3_CRUD_Model(Task, lambda *args : print(f"\nFileModifiedEvent : {args[1]}"))

    ### Added to share the Model between Views
    model_user1 = Model_User(tasks, lambda *args, **kwargs: print(f"User 1 notified"))
    tasks.register_observer(model_user1)

    model_user2 = Model_User(tasks, lambda *args, **kwargs: print(f"User 2 notified"))
    tasks.register_observer(model_user2)
    ###

    # Create a first task
    tasks.create("A first task", 3)
    print(tasks.read())
    # Output:
    # [('A first task', 3, True, datetime.datetime(2023, 7, 25, 21, 0, 14, 18657), 1.0)]

    # Create a second task
    tasks.create("A second task", 6, True, datetime.now(), 6.5)
    print(tasks.read())
    # Output:
    # [('A first task', 3, True, datetime.datetime(2023, 7, 25, 21, 0, 14, 18657), 1.0),
    # ('A second task', 6, True, datetime.datetime(2023, 7, 25, 21, 0, 14, 49183), 6.5)]

    # Update the second task
    tasks.update(1, "A modified task", 4, False, datetime.now(), 4.5)
    print(tasks.read())
    # Output:
    # [('A first task', 3, True, datetime.datetime(2023, 7, 25, 21, 0, 14, 18657), 1.0),
    # ('A modified task', 4, False, datetime.datetime(2023, 7, 25, 21, 0, 14, 61288), 4.5)]

    """
    # Here is the 'Task' table in 'Task.sqlite3' database at this step :

    | title           | priority  | active | modified_on                | weight |
    |-----------------|-----------|--------|----------------------------|--------|
    | A first task    | 3         | 1      | 2023-07-25 21:00:14.018657 | 1.0    |
    | A modified task | 4         | 0      | 2023-07-25 21:00:14.061288 | 4.5    |

    """

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
    # Here is the 'Task' table in 'Task.sqlite3' database at this step :

    | title           | priority  | active | modified_on                | weight |
    |-----------------|-----------|--------|----------------------------|--------|

    """
