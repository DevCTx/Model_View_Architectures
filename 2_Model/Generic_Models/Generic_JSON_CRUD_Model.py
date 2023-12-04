"""
    Create a Generic CRUD Model for Json File
"""
import json
from datetime import datetime   # used in Encoder

if __name__ == "__main__":  # To test the sample at the end of the file
    from Generic_CRUD_Model import Generic_CRUD_Model
else:   # if used as module
    from .Generic_CRUD_Model import Generic_CRUD_Model

class Json_Object_Meta(type):
    """" Metaclass responsible for adding the Encoder and Decoder methods to the class that uses it """

    def __new__(cls, name, bases, attrs):
        # Get the name of the class which called the metaclass
        object_type = super().__new__(cls, name, bases, attrs)

        # Define a generic JSON Encoder to convert an 'object_type' object into a Json dictionary
        class Encoder(json.JSONEncoder):
            def default(self, object_item):
                return self._object_type_encoder(object_item)

            def _object_type_encoder(self, object_item):
                if isinstance(object_item, object_type):
                    # Convert the values from 'object_type' to a JSON compatible type
                    compatible_object_item = {}
                    for (key, value) in object_item.__dict__.items():
                        if isinstance(value, datetime):     # JSONEncoder does not support datetime by default
                            value = value.strftime("%Y-%m-%d %H:%M:%S.%f")
                        compatible_object_item.update({key:value})
                    json_dict = compatible_object_item
                    return json_dict
                else:
                    return super().default(object_item)

        # Define a generic JSON Decoder to convert a Json dictionary into an 'object_type' object
        class Decoder(json.JSONDecoder):
            def __init__(self):
                super().__init__(object_hook=self._object_type_decoder)

            def _object_type_decoder(self, json_dict):
                object_item = object_type(**json_dict)
                return object_item

        object_type.Encoder = Encoder
        object_type.Decoder = Decoder

        return object_type


class Generic_JSON_CRUD_Model(Generic_CRUD_Model):
    """
    Create a Generic CRUD Model for JSON File

    Fieldnames of the JSON file are based on the arguments of the 'object_type' __init__ method

    The arguments of the __init__ in the 'object_type' class must match the names of its attributes
    to work with Generic_CRUD_Model.

    The _set_file_objects and _get_file_objects will be called by Generic_CRUD_Model to set or get the
    object_list of 'object_type' to/from the file
    """

    def __init__(self, object_type: type, notify_function : callable = None):
        # init the object_type, the field_names, the field_types, an object_list, the filename, call init_file_objects
        super().__init__(object_type, notify_function, "JSON")

    def _init_file_objects(self) -> None:
        try :
            self._get_file_objects()
        except FileNotFoundError :
            self._set_file_objects()

    def _set_file_objects(self) -> None:
        """ specific to JSON files """
        with open(self.filename, 'w') as file:
            try :
                json.dump( self.object_list, file, indent=2, cls=self.object_type.Encoder)
            except AttributeError as e :
                raise TypeError(f"Metaclass is missing to your class : "  
                                f"{self.object_type.__name__}(metaclass=Json_Object_Meta)") from e

    def _get_file_objects(self) -> None:
        """ specific to JSON files """
        with open(self.filename, 'r') as file:
            try:
                json_object_list = json.load(file, cls=self.object_type.Decoder)
            except AttributeError as e :
                raise TypeError(f"Metaclass is missing to your class : "  
                                f"{self.object_type.__name__}(metaclass=Json_Object_Meta)") from e

        json_values_list = [tuple(json_object.__dict__.values()) for json_object in json_object_list]
        # Convert the values from JSON to the correct type of 'object_type' (like datetime for example)
        self._convert_to_object_list(json_values_list)


if __name__ == "__main__":
    from datetime import datetime

    class Task(metaclass=Json_Object_Meta):

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
    tasks = Generic_JSON_CRUD_Model(Task, lambda *args : print(f"\nFileModifiedEvent : {args[1]}"))

    # Create a first task
    tasks.create("A first task", 3)
    print(tasks.read())
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

    """
    Here is the 'Task.json' file at this step :
    [
      {
        "title": "A first task",
        "priority": 3,
        "active": true,
        "modified_on": "2023-07-25 20:48:22.702207",
        "weight": 1.0
      },
      {
        "title": "A modified task",
        "priority": 4,
        "active": false,
        "modified_on": "2023-07-25 20:48:22.755209",
        "weight": 4.5
      }
    ]
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
    Here is the 'Task.json' file at this step :
    []
    """