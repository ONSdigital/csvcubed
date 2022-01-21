"""
Writer Base
-----------
"""
from abc import ABC, abstractmethod
from pathlib import Path


class WriterBase(ABC):
    @abstractmethod
    def write(self, output_directory: Path):
        """
        Write the output to disk in the :obj:`output_directory`
        """
        ...
