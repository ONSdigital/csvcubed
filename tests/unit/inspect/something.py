from unittest.mock import patch

import pytest


class Class:
    def method(self):
        pass


def test_the_thing():
    with patch("__main__.Class.method", lambda: "foo") as MockClass:
        assert Class().method() == "foo"
        print("Done")


if __name__ == "__main__":
    pytest.main()
