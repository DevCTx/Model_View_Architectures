import os
import sys

# Update sys.path to include the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
#if __name__ == "__main__" :
from Observer_patterns.Observables import ObservableList


class Bound_List(list):
    """ Sets a ttk.Treeview bound to a list of class properties (one way only) """

    def __init__(self, name, observable_list: ObservableList, on_size_modified=None, on_item_modified=None):
        super().__init__()
        self.name = name
        self.on_list_size_modified = on_size_modified
        self.on_list_item_modified = on_item_modified

        # calls _update_tk_list on list modification
        self._property_list = observable_list.bind_list(self._update_list)
        self._update_list(False)

    def _update_list(self, initialized=True):
        for _property in self._property_list:
            _property.unbind_property()  # ObservableProperty unbind
        super().clear()

        # Append items from the model
        for i, _property in enumerate(self._property_list):
            _property.bind_property(lambda index=i: self._update_item(index))
            super().append(_property.get())

        if initialized and self.on_list_size_modified is not None:
            self.on_list_size_modified()

    def _update_item(self, key):
        if 0 <= key < len(self):
            super().__setitem__(key, self._property_list[key].get() )

        if self.on_list_item_modified is not None:
            self.on_list_item_modified(key)

    def __setitem__(self, key, value):
        self._property_list[key].set(value)

    def update(self, value):
        self._property_list.update(value)

    def unbind_list(self):
        """ should be used on_closing window """
        for _property in self._property_list:
            _property.unbind_property()  # ObservableProperty unbind
        self._property_list.unbind_list()  # ObservableList unbind


if __name__ == "__main__":
    # FIRST FILE :

    # Create a list of values
    not_observed_list = [["First1","First2"], ("Tuple1","Tuple2"), "Third"]

    # Create a list of Properties to observe from the list of values
    observed_list = ObservableList([["First1","First2"], ("Tuple1","Tuple2"), "Third"])


    # SECOND FILE :

    # Create a function to call when the list_to_observe will be modified
    def on_list_size_modified():
        print(f"the size of observed_list has been modified")

    def on_list_item_modified(*args, **kwargs):
        print(f"the item [{args[0]}] of observed_list has been modified")

    # In another file, create a list bound on the observable list
    bound_list = Bound_List("bound_list", observed_list, on_list_size_modified, on_list_item_modified)

    # FIRST FILE :
    print(f"{not_observed_list = }")
    print(f"{observed_list = }")
    print(f"{bound_list = }")

    print("\nnot_observed_list[0] = 'Modified'")
    not_observed_list[0] = 'Modified'
    print(f"{not_observed_list = }")
    print(f"{observed_list = }")
    print(f"{bound_list = }")

    print("\nobserved_list[0].set('Changed')")
    observed_list[0].set('Changed')
    print(f"{observed_list = }")
    print(f"{bound_list = }")

    print("\nbound_list[1] = 'Revised'")
    bound_list[1] = 'Revised'
    print(f"{observed_list = }")
    print(f"{bound_list = }")

    print("\nobserved_list[1].set(('Tuple','from','observed_list'))")
    observed_list[1].set(('Tuple','from','observed_list'))
    print(f"{observed_list = }")
    print(f"{bound_list = }")

    print("\nbound_list[2] = ['List','from','bound_list']")
    bound_list[2] = ['List','from','bound_list']
    print(f"{observed_list = }")
    print(f"{bound_list = }")

    print("\nbound_list.update(['Revised','with','differents'])")
    bound_list.update(['Revised','with','differents'])
    print(f"{observed_list = }")
    print(f"{bound_list = }")

    print("\nobserved_list = ['Four','Five','Six']")
    observed_list.update(['Four','Five','Six'])
    print(f"{observed_list = }")
    print(f"{bound_list = }")

    print("\nbound_list.update(['Revised','less'])")
    bound_list.update(['Revised','less'])
    print(f"{observed_list = }")
    print(f"{bound_list = }")

    print("\nbound_list.update(['Revised','and','more'])")
    bound_list.update(['Revised','and','more'])
    print(f"{observed_list = }")
    print(f"{bound_list = }")

    print("\nbound_list.update(['Revised','less'])")
    observed_list.update(['Revised','less'])
    print(f"{observed_list = }")
    print(f"{bound_list = }")

    print("\nbound_list.update(['Revised','and','more'])")
    observed_list.update(['Revised','and','more'])
    print(f"{observed_list = }")
    print(f"{bound_list = }")
