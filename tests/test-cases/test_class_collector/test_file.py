"""This file is used for testing in  test_pref_check.py"""
from dataclasses import dataclass


class Myclass:
    my_string = "stuff"
    my_int = 5


class SecondClass:
    def __init__(self, name, age, location) -> None:
        self.name = name
        self.age = age
        self.location = location


@dataclass
class ThirdClass:
    def __init__(self, name, age, hobbies) -> None:
        self.name = name
        self.age = age
        self.hobbies = hobbies
