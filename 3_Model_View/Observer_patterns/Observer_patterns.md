[Model-View Architectures](../../README.md) > [3_Model_View](../../3_Model_View/Model_View.md) > [Observer_patterns](../../3_Model_View/Observer_patterns/Observer_patterns.md) 

# Observer patterns : 

This part references the different **observer mechanisms** used by the application.

* [Object Observer](#object-observer) : observer on an intern object.
* [File Observer](#file-observer-handler) : observer on an extern file.

---

An **Observer Pattern** is a **behavioral pattern** commonly used in software engineering. 
It defines a **one-to-many** dependency between objects, so that when **one object** (the subject) changes its state, 
**all dependent objects** (the observers) are automatically notified and updated. 

This facilitates synchronization between objects without them needing to know each other.\
Everything is registered by the model they use without the need to know who is using it.

All they need to do is be on the list of observers to be notified.

---

## Object Observer

The simplest one is the **Object Observer** which simply sets an **observer** to an **observable** object.

The ***Observable*** object has no knowledge of the **Observer** objects but has a list of **"observers"** to notify. 

This mechanism is possible by calling the ***notify*** method of each object registered in this list. \
This therefore means that a ***notify*** method must be defined in **each observer** whatever its type.

To show how to implement this step, an ***ObjectObserver*** class has been defined as an example with a ***notify*** 
method and an automatic call to the ***register_observer*** method of the ***observable*** object during its 
initialization.

```python
class ObjectObserver:

    def __init__(self, observable):
        observable.register_observer(self)

    def notify(self, observable, *args, **kwargs):
        print(self, "Got", args, kwargs, "From", observable)
```

The ***Observable*** class has only 3 little methods :
* ***register_observer*** : for registering an observer into the 'observers' list when the observation is needed.
* ***remove_observer*** : for removing an observer from the 'observers' list when the observation is not more needed.
* ***notify_observers*** : for calling the notify methods of each object registered in the 'observers' list.

```python
class Observable:

    def __init__(self):
        self._observers = []

    def register_observer(self, observer):
        if not hasattr(observer,"notify") :
            raise NotImplementedError("The class needs a 'notify' method in order to register as an observer")
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer):
        if observer in self._observers:
            self._observers.remove(observer)

    def notify_observers(self, *args, **kwargs):
        for obs in self._observers:
            obs.notify(self, *args, **kwargs)
```

***Note***: It might have been interesting to create an **abstract** class of ***ObjectObserver*** to make the user 
derived from it. But since the models are already generic and maybe not so easy to understand, I decided not to overload 
the code and to keep it simple by integrating the mechanism directly.

More about : [Observer_pattern on Wikipedia](https://en.wikipedia.org/wiki/Observer_pattern#Python)

---

## File Observer Handler

Here is the same kind of notifier except that this one is specially designed to **observe files out of the application 
scope**.

It uses the **Observer** and **FileSystemEventHandler** mechanisms of the **watchdog** Python library for being 
notified by the **monitoring file system events**.  

The application needs to create a ***FileObserverHandler*** object with in parameters :
* the **absolute path of the file** (***shared_file***) to observe 
* and the reference of the **notify function** (***notify_on_modified***) to call when a 
modification appears on this file.

```python
if __name__ == "__main__":

    shared_file = os.path.abspath("shared_file.txt")
    
    def notify_on_modified(event):
        print(f"notify_on_modified : {event}")
    
    file_observer_handler = FileObserverHandler(shared_file, notify_on_modified)
```

then it needs to create an ***Observer*** object to register this **file_observer_handler** into the list of 
'**observers to notify**'.

```python
    observer = Observer()
    observer.schedule(file_observer_handler, path=os.path.dirname(shared_file), recursive=False)
    observer.start()
```

***FileObserverHandler*** inherits from ***FileSystemEventHandler*** and overrides the ***on_modified*** method, but it 
may also override ***on_created***, ***on_deleted***, ***on_moved***, ***on_opened***, ***on_closed***, or 
***on_any_event*** to be notified for these other kind of events.

```python
class FileObserverHandler(FileSystemEventHandler):

    def __init__(self, shared_file_abspath, notify_function):
        self.shared_file_abspath = shared_file_abspath
        self.notify_function = notify_function

    def on_modified(self, event):
        if event.is_directory:
            return
        if event.src_path == self.shared_file_abspath:
            self.notify_function(event)
```

More about : [FileSystemEventHandler on https://pythonhosted.org/](https://pythonhosted.org/watchdog/api.html#watchdog.events.FileSystemEventHandler)

---

[Model-View Architectures](../../README.md) > [3_Model_View](../../3_Model_View/Model_View.md) > [Observer_patterns](../../3_Model_View/Observer_patterns/Observer_patterns.md)