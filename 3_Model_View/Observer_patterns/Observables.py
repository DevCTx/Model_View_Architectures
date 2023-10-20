# https://en.wikipedia.org/wiki/Observer_pattern#Python


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
    def __init__(self, observable):
        observable.add_observer(self.notify)

    def notify(self, observable, *args, **kwargs):
        print(self, "Got", args, kwargs, "From", observable)


if __name__ == "__main__":
    subject = Observable()
    object_observer1 = ObserverObject(subject)
    object_observer2 = ObserverObject(subject)
    subject.notify_observers("notification", kw="test")


