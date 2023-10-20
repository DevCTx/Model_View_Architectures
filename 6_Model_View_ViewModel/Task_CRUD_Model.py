from datetime import datetime
from typing import Callable

from Generic_Models.Generic_CRUD_Model import Generic_CRUD_Model
from Generic_Models.Generic_CSV_CRUD_Model import Generic_CSV_CRUD_Model
from Generic_Models.Generic_JSON_CRUD_Model import Generic_JSON_CRUD_Model, Json_Object_Meta
from Generic_Models.Generic_XML_CRUD_Model import Generic_XML_CRUD_Model
from Generic_Models.Generic_SQLITE3_CRUD_Model import Generic_SQLITE3_CRUD_Model


class Task(metaclass=Json_Object_Meta):     # needed for Generic_JSON_CRUD_Model

    def __init__(self, title: str, priority: int, modified_on: datetime = datetime.now()):
        """
        The arguments of __init__ must match the names of its attributes to work with Generic_CRUD_Model
        """
        self.title: str = title
        self.priority: int = priority
        self.modified_on: datetime = modified_on

    def read_format(self):
        """ Optional: customizes the format for printing objects in the read list  """
        return tuple(self.__dict__.values())

    def __str__(self):
        """ Optional : Define the format to print as string """
        return f"{self.read_format()}"


class Task_CRUD_Model(Generic_CSV_CRUD_Model):
    """
    Create a complete CRUD Model for storing 'Task' Object in :
    - a CSV File named 'Task.csv' if it inherits from 'Generic_CSV_CRUD_Model'
    - a JSON File named 'Task.json' if it inherits from 'Generic_JSON_CRUD_Model'
    - an XML File named 'Task.xml' if it inherits from 'Generic_XML_CRUD_Model'
    - an SQLITE3 Database named 'Task.sqlite3' if it inherits from 'Generic_SQLITE3_CRUD_Model'
    _ a simple list if it inherits from 'Generic_CRUD_Model'
    """

    def __init__(self, notify_function: Callable = None):
        super().__init__(Task, notify_function)

    def create(self, title: str, priority: int):
        super().create(title, priority, datetime.now())

    def update(self, list_idx: int, title: str, priority: int):
        # Includes the date and time of modification
        super().update(list_idx, title, priority, datetime.now())


if __name__ == "__main__":

    class Model_User:
        def __init__(self, model, notify_function: Callable):
            self.model = model
            self.notify_function = notify_function

        def notify(self, *args, **kwargs):
            self.notify_function(*args, **kwargs)

    task = Task("Sample", 3)
    print(task)  # Output : ('Sample', 3)

    # Create CRUD Model for Task objects with a File or a database depending on the inheritance
    tasks = Task_CRUD_Model(lambda *args: print(f"\nFileModifiedEvent : {args[1]}"))

    model_user1 = Model_User(tasks, lambda *args, **kwargs: print(f"User 1 notified"))
    tasks.add_observer(model_user1.notify)

    model_user2 = Model_User(tasks, lambda *args, **kwargs: print(f"User 2 notified"))
    tasks.add_observer(model_user2.notify)

    # Create a first task
    tasks.create("A first task", 3)
    print(tasks.read())  # Output: [('A first task', 3)]

    # Create a second task
    tasks.create("A second task", 6)
    print(tasks.read())  # Output:   [('A first task', 3), ('A second task', 6)]

    # Update the second task
    tasks.update(1, "A modified task", 4)
    print(tasks.read())  # Output:   [('A first task', 3), ('A modified task', 4)]

    """
    # Here is the 'Task.csv' file at this step if it inherits from Generic_CSV_CRUD_Model :
    title,priority,modified_on
    A first task,3,2023-09-07 13:59:57.012410
    A modified task,4,2023-09-07 13:59:57.045406

    # Here is the 'Task.json' file at this step if it inherits from Generic_JSON_CRUD_Model :
    [
      {
        "title": "A first task",
        "priority": 3,
        "modified_on": "2023-09-07 14:00:54.572235"
      },
      {
        "title": "A modified task",
        "priority": 4,
        "modified_on": "2023-09-07 14:00:54.614238"
      }
    ]

    # Here is the 'Task.xml' file at this step if it inherits from Generic_XML_CRUD_Model :
    <?xml version='1.0' encoding='utf-8'?>
    <Tasks>
      <Task>
        <title type="str">A first task</title>
        <priority type="int">3</priority>
        <modified_on type="datetime">2023-09-07 14:00:28.640257</modified_on>
      </Task>
      <Task>
        <title type="str">A modified task</title>
        <priority type="int">4</priority>
        <modified_on type="datetime">2023-09-07 14:00:28.680263</modified_on>
      </Task>
    </Tasks>

    # Here is the 'Task' table in 'Task.sqlite3' database at this step if it inherits from Generic_SQLITE3_CRUD_Model :

    | title           | priority  | modified_on                |
    |-----------------|-----------|----------------------------|
    | A first task    | 3         | 2023-07-26 11:55:46.780436 |
    | A modified task | 4         | 2023-07-26 11:55:46.835892 |

    """
    # # Delete the first task
    # tasks.delete(0)
    # print(tasks.read())
    # # Output:   [('A modified task', 4)]
    #
    # # Delete the second task
    # tasks.delete(0)
    # print(tasks.read())
    # # Output: []
