"""
    Create a Generic CRUD Model for XML File
"""
from xml.etree import ElementTree as ET

if __name__ == "__main__":  # To test the sample at the end of the file
    from Generic_CRUD_Model import Generic_CRUD_Model
else:   # if used as module
    from .Generic_CRUD_Model import Generic_CRUD_Model


class Generic_XML_CRUD_Model(Generic_CRUD_Model):
    """
    Create a Generic CRUD Model for XML File

    Fieldnames of the XML file are based on the arguments of the 'object_type' __init__ method

    The arguments of the __init__ in the 'object_type' class must match the names of its attributes
    to work with Generic_CRUD_Model.

    The _set_file_objects and _get_file_objects will be called by Generic_CRUD_Model to set or get the
    object_list of 'object_type' to/from the file
    """

    def __init__(self, object_type: type, notify_function: callable = None):
        # init the object_type, the field_names, the field_types, an object_list, the filename, call init_file_objects
        super().__init__(object_type, notify_function, "XML")

    def _init_file_objects(self) -> None:
        try:
            self._get_file_objects()
        except FileNotFoundError:
            self._set_file_objects()

    def _set_file_objects(self) -> None:
        """ specific to XML files """
        # define a general 'object_type + s' attribute for the whole list
        objects_root = ET.Element(f"{self.object_type.__name__}s")
        for object_item in self.object_list:
            # define an 'object_type' attribute for each object of the list
            object_element = ET.SubElement(objects_root, self.object_type.__name__)
            for idx, (key, value) in enumerate(object_item.__dict__.items()):
                # define each 'attribute' of the 'object_type' class as an <'attribute'> element
                object_sub_element = ET.SubElement(object_element, key)
                # define an attribute 'type' in each <'attribute'> element to store the attribute type
                object_sub_element.attrib = {'type': str(self.field_types[idx].__name__)}
                # and store the attribute value as a string in the text of the <'attribute'> element
                object_sub_element.text = str(value)
        # make it more readable
        ET.indent(objects_root)
        # and write it at the root of the file
        tree = ET.ElementTree(objects_root)
        tree.write(self.filename, encoding="utf-8", xml_declaration=True)

    def _get_file_objects(self) -> None:
        """ specific to XML files """
        self.object_list = []
        tree = ET.parse(self.filename)
        xml_root = tree.getroot()
        xml_values_list = []
        for xml_element in xml_root:
            xml_values_list.append([xml_sub_element.text for xml_sub_element in xml_element])
        # Convert the values from XML to the type of 'object_type'
        self._convert_to_object_list(xml_values_list)


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
        def __init__(self, model, notify_function: callable):
            self.model = model
            self.notify_function = notify_function

        def notify(self, *args, **kwargs):
            self.notify_function(*args, **kwargs)
    ###

    task = Task("Sample", 3)
    print(task)
    # Output : ('Sample', 3, True, datetime.datetime(2023, 7, 25, 21, 0, 14, 18657), 1.0)

    # Create CRUD Model for Task objects with a CSV File
    tasks = Generic_XML_CRUD_Model(Task, lambda *args: print(f"\nFileModifiedEvent : {args[1]}"))

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
    Here is the 'Task.csv' file at this step :
    <?xml version='1.0' encoding='utf-8'?>
    <Tasks>
      <Task>
        <title type="str">A first task</title>
        <priority type="int">3</priority>
        <active type="bool">True</active>
        <modified_on type="datetime">2023-07-25 21:00:14.018657</modified_on>
        <weight type="float">1.0</weight>
      </Task>
      <Task>
        <title type="str">A modified task</title>
        <priority type="int">4</priority>
        <active type="bool">False</active>
        <modified_on type="datetime">2023-07-25 21:00:14.061288</modified_on>
        <weight type="float">4.5</weight>
      </Task>
    </Tasks>
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
    Here is the 'Task.csv' file at this step :
    <?xml version='1.0' encoding='utf-8'?>
    <Tasks />
    """
