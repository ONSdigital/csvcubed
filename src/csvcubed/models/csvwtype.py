from enum import Enum, auto


class CSVWType(Enum):
    """
    The type of metadata file.
    """

    QbDataSet = auto()
    """ The metadata file is of type data cube dataset. """

    CodeList = auto()
    """ The metadata file is of type code list/concept scheme. """

    Other = auto()
    """ The metadata file is not of types data cube and code list. This type of metadata files is not supported."""
