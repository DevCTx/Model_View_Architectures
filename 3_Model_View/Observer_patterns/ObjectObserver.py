# https://en.wikipedia.org/wiki/Observer_pattern#Python


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


class ObjectObserver:
    def __init__(self, observable):
        observable.register_observer(self)

    def notify(self, observable, *args, **kwargs):
        print(self, "Got", args, kwargs, "From", observable)


if __name__ == "__main__":
    subject = Observable()
    object_observer1 = ObjectObserver(subject)
    object_observer2 = ObjectObserver(subject)
    subject.notify_observers("notification", kw="test")

### Output :
# <__main__.ObjectObserver object at 0x00000165AC0B9490> Got ('notification',) {'kw': 'test'} From <__main__.Observable object at 0x00000165AC0B9410>
# <__main__.ObjectObserver object at 0x00000165AC0B9610> Got ('notification',) {'kw': 'test'} From <__main__.Observable object at 0x00000165AC0B9410>

