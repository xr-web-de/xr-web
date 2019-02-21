from os import path

if path.exists(path.join(path.dirname(__file__), "local.py")):
    from .local import *  # NOQA
else:
    from .base import *  # NOQA
