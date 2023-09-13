[Model-View Architectures](../../README.md) > [Model](../Model.md) > [Generic_Models](Generic_Models.md) 

# Generic Models : 

Here is the presentation of the **Generic Models** developed to illustrate the swapping of Models in the main program.

* ***[Generic CRUD Model](#generic-crud-model)*** is the base model and generates generic methods to **C**reate, 
**R**ead, **U**pdate and **D**elete data in a list.
* ***[Generic CSV CRUD Model](#generic-csv-crud-model)*** : is suitable for **CSV** files
* ***[Generic XML CRUD Model](#generic-xml-crud-model)*** : is suitable for **XML** files
* ***[Generic JSON CRUD Model](#generic-json-crud-model)*** : is suitable for **JSON** files
* ***[Generic SQLITE3 CRUD Model](#generic-sqlite3-crud-model)*** : is suitable for **SQLITE3** databases
* ***[Usage Example](#usage-example)*** for this models

---

## Generic CRUD Model

This model creates a **list of *object_type*** and the methods to **Create**, **Read**, **Update**, and **Delete** this 
type of objects from/to this **list**.

It is the **core of the CRUD models** and allows by inheritance to add these functionalities to any class for 
manipulating data of any kind.

---

### Initialization

To be used, a class representing the data must be defined with the **same internal attribute names** as the 
**arguments of its initialization method**. 

```python
class Task:

    def __init__(self, 
                 title: str, 
                 priority: int, 
                 active: bool = True,
                 modified_on: datetime = datetime.now(), 
                 weight: float = 1.0):
        self.title: str = title
        self.priority: int = priority
        self.active: bool = active
        self.modified_on: datetime = modified_on
        self.weight: float = weight
```

Then the model can be defined by simply giving this **object type** to the ***Generic_CRUD_Model***.

```python
tasks = Generic_CRUD_Model(Task)
```

The ***Generic_CRUD_Model*** will then create a **list** of data based on the ***object_type***, if the given argument is a class, and store the ***field names and types*** of this ***object_type*** for the future data operations.

````python
class Generic_CRUD_Model:

    def __init__(self, object_type: type, on_modified: Callable = None, file_extension: str = None):

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

````

---

### Create / Read / Update / Delete

Now, a task data can be **created** and **read** in the list as easily as a task object can be set and get.

```python
tasks.create("A first task", 3)
print(tasks.read())     # Output: [('A first task', 3, True, datetime.datetime(2023, 7, 25, 20, 48, 22, 702207), 1.0)]
tasks.update(0, "A modified task", 5)
tasks.delete(0)
```

And it can be **updated** or **deleted** by using the appropriate index of the object to manipulate.   

---

### Read Format

The ***read*** method will return a list according to the ***read_format*** that can be overriden.

```python
class Task:

    def read_format(self):
        """ Optional: customizes the format for printing objects in the read list  """
        return tuple(self.__dict__.values())
```

---

### Data in file or database

When a ***file_extension*** is provided as an argument during the initialization of the ***Generic_CRUD_Model***, it 
generates a ***filename*** based on the name of the ***object_type*** and the given ***file_extension***.

There are currently **four derived versions** of this ***Generic_CRUD_Model*** that allow data to be saved in : 
* **CSV** files, 
* **JSON** files, 
* **XML** files 
* or in an **SQLITE3** database.

Those models overwrite the ***_init_file_objects***, ***_set_files_objects*** and ***_get_file_objects*** methods to
let the ***Generic_CRUD_Model*** know how to **initiate**, **set** and **get** the data from/to this file, each time 
the ***create, read, update*** and ***delete*** methods are used.

If a ***filename*** exists, the model is also automatically registered as an ***observer*** on this file within the 
system, via the **Python's watchdog mechanism**, to be **notified** if **another program modifies it**.

More about : [Observer_patterns](../Observer_patterns/Observer_patterns.md)

---

## Generic CSV CRUD Model

The ***Generic_CSV_CRUD_Model*** is designed to work with **CSV** files and uses the ***csv*** Python library. \
It is initialized with an ***object_type*** and an optional ***notify_function*** which can be notified when the CSV 
file is modified.

**Python does not allow the direct modification of a specific line in a CSV file**. Therefore, it is necessary to 
**read** the entire file, **store** the information in memory, **modify** the relevant line, and then **rewrite** the 
entire file for a modification to take effect.

***Generic_CSV_CRUD_Model*** overwrites **three methods**:

* ***_set_file_objects***: opens the CSV file in **write** mode, insert a **header** based on the 
**initialization arguments of the generic object** (***object_type***), then write the data rows from the **list** 
(***object_list***) that have been created, modified, or deleted by the methods of ***Generic_CRUD_Model***.


* ***_get_file_objects***: opens the CSV file in **read** mode to simply **retrieve** the data and then 
**convert** it according to the **types defined in *object_type*** with ***_convert_to_object_list*** before
to store it in the ***object_list***.


* ***_init_file_objects***: In this case, this method simply calls ***_set_file_objects*** because the file is **reset** 
and **entirely rewritten** at each modification.

Note : The ***newline=""*** argument given in the open functions is to be cross-platform compatible and should avoid the 
conflict between the '\n' Linux/Unix end line character and the '\r\n' Windows end line character.

### Example of `Task.csv` file:

````csv
title,priority,active,modified_on,weight
A first task,3,True,2023-07-25 20:57:08.549630,1.0
A modified task,4,False,2023-07-25 20:57:08.597780,4.5
````

---

## Generic XML CRUD Model

The ***Generic_XML_CRUD_Model*** class is designed to work with **XML** files and uses the ***xml.etree*** Python 
library. \
It is initialized with an ***object_type*** and an optional ***notify_function*** which can be notified when the XML 
file is modified.

**Python doesn't require loading the entire XML file into memory before making modifications**. 
However, for the sake of **simplicity** and **better comprehension**, I followed the similar approach that for the CSV 
files. Therefore, it also reads the entire file, store the information in memory, and modify the relevant line, before 
to rewrite the entire file when a modification need to be applied. 

This class defines **three methods**:

* ***_set_file_objects***: This method generates **XML elements** according to the names of the ***object_type*** 
attributes. It creates a '**Tasks**' root Element and for each object of the list, a '**Task**' 
SubElement with its **attributes as tags**, store the **value of them as text** and their **types as xml attributes**. 
\
\
Then, the file is **formatted with indentations** for a better human readability, and store as an **utf-8 encoding** 
standard **XML file**.


* ***_get_file_objects***: This method is responsible for **parsing the XML file**, retrieving the root, and storing 
each of its elements in the ***object_type*** list. Before adding them to the list, it ensures that the elements are 
correctly **converted** to their respective data types using ***_convert_to_object_list*** method. 
\
\
Please note that the 
data type in the XML file is stored for informational purposes only and is not used in this conversion process.


* ***_init_file_objects***: Same as for CSV files, this method simply calls ***_set_file_objects*** because the file is 
**reset** and **entirely rewritten** at each modification.

### Example of `Task.xml`  file :
````xml
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
````

---

## Generic JSON CRUD Model

This model uses the ***json*** Python library and is designed to work with **JSON** files.

It defines a **metaclass** called ***Json_Object_Meta***, which is responsible for adding **encoder** and **decoder** 
methods to the classes that use it and so allows to convert the **object_type of any kind** into a **JSON format** and 
vice versa.

```python
class Task(metaclass=Json_Object_Meta)
```

The ***Generic_Json_CRUD_Model*** is an extension of the ***Generic_CRUD_Model*** and so overrides the **three same 
methods** :

* ***_set_file_objects***: which opens the JSON file in **write** mode and uses the ***Encoder*** method from the 
**metaclass** to **convert** the ***object_type*** objects into a **JSON format**.


* ***_get_file_objects***: This method opens the JSON file in **read** mode and utilizes the ***Decoder*** method from 
the **metaclass** to **convert** the **JSON-formatted** lines into **JSON objects** and convert them to the appropriate 
***object_type*** using the same ***_convert_to_object_list*** method. 
\
\
Using this method, it is possible to retrieve a format that JSON 
cannot convert in its original way, such as **datetime** attributes, as they are stored as **text** in the JSON file 
and reconverted based on the type of the ***object_type*** structure.


* ***_init_file_objects***: Likewise, this method simply calls ***_set_file_objects*** because the 
file is **reset** and **entirely rewritten** at each modification.

### Example of `Task.json` file :
````json
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
````

---

## Generic SQLITE3 CRUD Model

The ***Generic_SQLITE3_CRUD_Model*** is an extension of the ***Generic_CRUD_Model*** and has been defined to work with 
**SQLITE3** database, which is a specific database format stored in a single file. It uses the ***sqlite3*** Python 
library. But contrary to the CSV, XML or JSON files, as database, it appears evident to deploy a different strategy 
to ***create***, ***update*** and ***delete*** the data from/to it.

That's why these different methods have been **rewritten** in this model to better fit this database.

* ***_init_file_objects*** : this method initializes a **connection** to the **SQLITE3** database or creates it if it 
does not exist. It creates a **database** named as the ***object_type*** given in argument to the ***\_\_init\_\_*** 
method (using the ***filename*** attribute of ***Generic_CRUD_Model***) and also creates a **table** with that name.


* ***create*** : reuses this connection to create an **insert** into this table


* ***update*** : reuses this connection and **update** an ***object_type*** object in the database **if its index is 
valid**.


* ***delete*** : reuses this connection and **delete** an ***object_type*** object from the database **if its index is 
valid**.


* ***_get_file_objects***: simply **selects** all data from the database ***object_type*** and converts it into 
more appropriate types using the ***_convert_to_object_list*** method.


* and ***_type_to_sqlite3***: does the exact opposite, converting attribute types from ***object_type*** to formats 
more appropriate for the **SQLITE3** database. 

### Example of a `Task` table in a `Task.sqlite3` database:
| title           | priority  | active | modified_on                | weight |
| --------------- | --------- | ------ | -------------------------- | ------ |
| A first task    | 3         | 1      | 2023-07-26 11:55:46.780436 | 1.0    |
| A modified task | 4         | 0      | 2023-07-26 11:55:46.835892 | 4.5    |
    

---

### SQLITE3 File Observer 

Please note that the system will notify the changes on the SQLITE3 file but not on the specific 'object_type' table.\
For another use of this SQLITE3 database, a better notification mechanism might be needed to be more accurate.

---

## Usage Example

For each of these generic models, an **identical usage example** is provided at the end of the file 
and can be run as **main program** to verify that the **method of usage remains the same**, but the **results vary 
depending on the specific model being used**.

The printing format will follow the output of the [read format](#read-format) :

```commandline
[('A first task', 3, True, datetime.datetime(2023, 7, 25, 20, 57, 8, 549630), 1.0),
('A second task', 6, True, datetime.datetime(2023, 7, 25, 20, 57, 8, 587785), 6.5)]
```

---

[Model-View Architectures](../../README.md) > [Model](../Model.md) > [Generic_Models](Generic_Models.md)