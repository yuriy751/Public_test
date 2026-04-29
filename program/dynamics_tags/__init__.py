from dataclasses import dataclass, field
from .methods_tags import MethodTags


@dataclass
class DynamicsTag:
    methods: MethodTags = field(default_factory=MethodTags)

DYNAMIS_TAGS = DynamicsTag()