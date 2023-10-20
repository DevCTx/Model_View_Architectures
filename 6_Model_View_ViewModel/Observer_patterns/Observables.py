# https://en.wikipedia.org/wiki/Observer_pattern#Python
from difflib import Differ


class Observable:

    def __init__(self):
        self._observers = []
        self._unbind = None

    def add_observer(self, observer: callable):
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: callable):
        if observer in self._observers:
            self._observers.remove(observer)

    def notify_observers(self, *args, **kwargs):
        for observer in self._observers:
            observer(*args, **kwargs)

    def bind(self, observer: callable):
        self.add_observer(observer)

        def unbind_function():
            self.remove_observer(observer)

        self._unbind = unbind_function
        return self


class ObservableProperty(Observable):

    def __init__(self, value=None):
        super().__init__()
        self._value = value

    def get(self):
        return self._value

    def set(self, value):
        if self._value != value:
            # print(f"notify_observers on modified property : {self._value} -> {value}")
            self._value = value
            self.notify_observers()  # on modified property

    def bind_property(self, observer):
        return self.bind(observer)  # ObservableProperty bind

    def unbind_property(self):
        if self._unbind is not None:
            self._unbind()  # ObservableProperty unbind


class ObservableList(Observable, list):

    def __init__(self, value_list=None):
        super().__init__()
        for i, value in enumerate(value_list):
            self.append(value)

    def append(self, _object) -> None:
        if isinstance(_object, ObservableProperty):
            super().append(_object)
        else:
            super().append(ObservableProperty(_object))

    def insert(self, index, _object) -> None:
        if isinstance(_object, ObservableProperty):
            super().insert(index, _object)
        else:
            super().insert(index, ObservableProperty(_object))

    def update(self, value_list=None):
        if len(self) == len(value_list):
            # If the list has the same size, only set the values and notify the binds of the set values
            for index, value in enumerate(value_list):
                self[index].set(value)  # check the value to know if it needs to be updated
        else:
            # If the list has a different size, update the whole list
            # and notify the list binds for scrollbars and screen cleaning
            diff = list(Differ().compare([item.get() for item in self], value_list))
            index = 0
            for step in diff:
                if step[:2] == '- ':
                    # print(f"ObservableList update : unbind_property and del : [{index}]")
                    self[index].unbind_property()
                    del self[index]
                elif step[:2] == '+ ':
                    def type_param(given_type, param_str):
                        """ Build a value from a given type and a string (including tuples)
                        >>> type_param(int, "2")
                        2
                        >>> type_param(str, "2")
                        '2'
                        >>> type_param(tuple, "(2, 3)")
                        (2, 3)
                        >>> type_param(tuple, "('2', '3')")
                        ('2', '3')
                        >>> type_param(list, "(2, 3)")
                        [2, 3]
                        >>> type_param(list, "('2', '3')")
                        ['2', '3']
                        >>> type_param(str, "33, Priority: 3")
                        '33, Priority: 3'
                        """
                        if given_type in (tuple, list):
                            import ast
                            return given_type(ast.literal_eval(param_str))
                        else:
                            return given_type(param_str)

                    value = type_param(type(value_list[index]), step[2:])
                    # print(f"ObservableList update : insert : [{index}]={value}")
                    self.insert(index, value)
                    index += 1
                elif step[:2] != '? ':
                    index += 1
            self.notify_observers()  # on modified list

    def bind_list(self, observer):
        return self.bind(observer)  # ObservableList bind

    def unbind_list(self):
        if self._unbind is not None:
            self._unbind()  # ObservableList unbind

    def __repr__(self):
        return repr([item.get() for item in self])


class ObserverObject:
    def __init__(self, observable):
        observable.add_observer(self.notify)

    def notify(self, observable, *args, **kwargs):
        print(self, "Got", args, kwargs, "From", observable)


if __name__ == "__main__":
    subject = Observable()
    object_observer1 = ObserverObject(subject)
    object_observer2 = ObserverObject(subject)
    subject.notify_observers("notification", kw="test")

    ### Output :
    # <__main__.ObserverObject object at 0x00000165AC0B9490> Got ('notification',) {'kw': 'test'} From <__main__.Observable object at 0x00000165AC0B9410>
    # <__main__.ObserverObject object at 0x00000165AC0B9610> Got ('notification',) {'kw': 'test'} From <__main__.Observable object at 0x00000165AC0B9410>

    op2 = ObservableProperty('test2')
    print(f"{op2.get()=}")

    collect = ObservableList(['test1', 'test2', 'test3'])
    print(f"{collect[1].get()=}")
    print(f"{collect=}")

    collect.append("test4")
    print(f"{collect=}")

    print(f"\n{op2.set('try')=}")
    print(f"{op2.get()=}\n")

    print(f"{collect[1].set('try2')=}")
    print(f"{collect[1].get()=}")
    print(f"{collect=}\n")

    print(f"{collect.update(['test1', 'modified', 'test3'])=}")
    print(f"{collect[1].get()=}")
    print(f"{collect=}\n")

    print(f"{collect.update(['test1', 'modified', 'test3', 'insert'])=}")
    print(f"{collect[3].get()=}")
    print(f"{collect=}\n")

    print(f"{collect.update(['test1', 'modified', 'test3'])=}")
    print(f"{collect=}\n")

    print(f"{collect.update(['test1', 'insert', 'modified', 'test3'])=}")
    print(f"{collect=}\n")

    print(f"{collect.update(['test1', 'modified', 'test3'])=}")
    print(f"{collect=}\n")

    print(f"{collect.update(['test1', 'modified'])=}")
    print(f"{collect=}\n")

    print(f"{collect.update([])=}")
    print(f"{collect=}\n")

    print(f"{collect.update(['new1', 'new2', 'new3', 'new4'])=}")
    print(f"{collect=}\n")

    print(f"{collect.update(['new1', 'modified', 'new3', ])=}")
    print(f"{collect=}\n")

    print(f"{collect.update(['test1', 'modified', 'test3', 'insert', 'insert'])=}")
    print(f"{collect=}\n")

    print(f"{collect.update(['test1', 'modified', 'test3'])=}")
    print(f"{collect=}\n")
