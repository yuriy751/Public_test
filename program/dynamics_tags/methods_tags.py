from dataclasses import dataclass


@dataclass
class MethodTags:
    def create_new_tag(self, name, value):
        if not hasattr(self, name):
            setattr(self, name, value)

    def delete_tag(self, name):
        if hasattr(self, name):
            delattr(self, name)