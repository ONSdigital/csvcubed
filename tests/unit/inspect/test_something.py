from unittest.mock import patch

import pytest


class Class:
    def method(self):
        pass


def test_the_thing():
    with patch("__main__.Class") as MockClass:
        instance = MockClass.return_value
        instance.method.return_value = "foo"
        assert Class() is instance
        assert Class().method() == "foo"
        print("Done")


if __name__ == "__main__":
    pytest.main()
