from enum import Enum


class JsonSchemaVersion(Enum):
    v1_0 = "V1_0"

def do_something(version: JsonSchemaVersion) -> None:
    print(version)
    print(version.name)
    print(version.value)

do_something(JsonSchemaVersion.v1_0)