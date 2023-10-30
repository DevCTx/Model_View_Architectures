# https://en.wikipedia.org/wiki/Observer_pattern#Python
import atexit


class Observable:
    def __init__(self):
        self._observers = []

    def add_observer(self, observer : callable):
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer : callable):
        if observer in self._observers:
            self._observers.remove(observer)

    def notify_observers(self, *args, **kwargs):
        for observer in self._observers:
            observer(*args, **kwargs)


class ObserverObject:
    def __init__(self, name, observable):
        self.name = name
        self.observable = observable
        self.observable.add_observer(self.notify)
        print(self.name, "Add self.notify to observer list of", self.observable.__class__.__name__)
        atexit.register(self.on_closing)

    def on_closing(self):
        self.observable.remove_observer(self.notify)
        print(self.name, "Remove self.notify from observer list of", self.observable.__class__.__name__)

    def notify(self, *args, **kwargs):
        print(self.name, "Got", args, kwargs, "From", self.observable.__class__.__name__)


if __name__ == "__main__":
    subject = Observable()
    object_observer1 = ObserverObject("object_observer1", subject)
    object_observer2 = ObserverObject("object_observer2", subject)
    subject.notify_observers("notification", kw="test")

#### Output :
# object_observer1 Add self.notify to observer list of Observable
# object_observer2 Add self.notify to observer list of Observable
# object_observer1 Got ('notification',) {'kw': 'test'} From Observable
# object_observer2 Got ('notification',) {'kw': 'test'} From Observable
# object_observer2 Remove self.notify from observer list of Observable
# object_observer1 Remove self.notify from observer list of Observable
