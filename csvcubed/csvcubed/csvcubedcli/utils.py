import re
from functools import wraps
import os
from pathlib import Path

from typing import Union, Sequence, Any, List

#import vcr
from unidecode import unidecode


def pathify(label):
    """
      Convert a label into something that can be used in a URI path segment.
    """
    return re.sub(r'-$', '',
                  re.sub(r'-+', '-',
                         re.sub(r'[^\w/]', '-', unidecode(label).lower())))


def is_interactive():
    import __main__ as main
    return not hasattr(main, '__file__')


def ensure_list(o: Any) -> List:
    if isinstance(o, List):
        return o
    else:
        return [o]


# def recordable(f):
#     @wraps(f)
#     def wrapper(*args, **kwargs):
#         if 'RECORD_MODE' in os.environ:
#             with vcr.use_cassette(str(Path('fixtures') / 'recording.yml'), record_mode=os.environ['RECORD_MODE']):
#                 return f(*args, **kwargs)
#         else:
#             return f(*args, **kwargs)
#     return wrapper