from dataclasses import dataclass
import re


@dataclass
class RIsState:
    def create_new_n(self, name, value):
        if not hasattr(self, name):
            setattr(self, name, value)

    def delete_n(self, name):
        if hasattr(self, name):
            delattr(self, name)

    def get_sorted_layers(self):

        layer_items = []

        for key, value in self.__dict__.items():

            match = re.match(r"n_(\d+)$", key)
            if match:
                layer_number = int(match.group(1))
                layer_items.append((layer_number, value))

        layer_items.sort(key=lambda x: x[0])

        return [value for _, value in layer_items]