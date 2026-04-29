from dataclasses import dataclass


@dataclass
class MethodVarsState:
    def create_new_var(self, name, value):
        if not hasattr(self, name):
            setattr(self, name, value)

    def delete_var(self, name):
        if hasattr(self, name):
            delattr(self, name)