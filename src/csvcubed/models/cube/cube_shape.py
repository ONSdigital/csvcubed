from enum import Enum, auto


class CubeShape(Enum):
    """
    The shape of the cube.
    """

    Standard = auto()
    """ The cube is in the standard shape. """

    Pivoted = auto()
    """ The cube is in the pivoted shape. """
