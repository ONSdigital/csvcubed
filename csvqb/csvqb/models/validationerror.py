"""
ValidationError
---------------
"""


class ValidationError:
    def __init__(self, message: str):
        self.message: str = message

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.message})"
