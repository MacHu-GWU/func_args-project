# -*- coding: utf-8 -*-

from ._version import __version__
from ._version import __short_description__
from ._version import __license__
from ._version import __author__
from ._version import __author_email__
from ._version import __maintainer__
from ._version import __maintainer_email__
# ------------------------------------------------------------------------------
# For compatibility with older versions of func_args>=0.1.1,<1.0.0
from .arg import OPT as NOTHING
from .arg import remove_optional as resolve_kwargs
# ------------------------------------------------------------------------------
