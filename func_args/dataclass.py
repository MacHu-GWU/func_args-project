# -*- coding: utf-8 -*-

"""
Enhanced dataclass functionality for parameter handling.

This module extends Python's standard dataclasses with additional capabilities
for handling required and optional parameters in a more controlled way.

Key features:

- Use sentinel values (REQ, OPT) to mark required and optional fields
- Validation of required parameters during initialization
- Methods to convert dataclass instances to dictionaries with proper handling of sentinels
- Freedom from dataclass limitations on field ordering (required fields first)
"""

import dataclasses

from .exc import ParamError
from .arg import REQ, OPT, T_KWARGS


class BaseModelMixin:
    """
    Base class for all parameter dataclasses with validation capabilities.

    This class provides enhanced functionality for parameter validation and conversion
    that all parameter classes can inherit. It handles required parameter validation
    during initialization and provides utility methods to convert parameters to
    dictionaries suitable for function calls.
    """

    def _validate(self) -> None:
        """
        Validate that all required parameters are provided.
        """
        for field in dataclasses.fields(self.__class__):
            if field.init:
                k = field.name
                if getattr(self, k) is REQ:
                    raise ParamError(f"Field {k!r} is required for {self.__class__}.")

    def __post_init__(self) -> None:
        self._validate()

    @classmethod
    def _split_req_opt(cls, kwargs: T_KWARGS) -> tuple[T_KWARGS, T_KWARGS]:
        """
        Split provided kwargs into required and optional parameters.
        """
        req_kwargs, opt_kwargs = dict(), dict()
        for field in dataclasses.fields(cls):
            if field.default is REQ:
                try:
                    req_kwargs[field.name] = kwargs[field.name]
                except KeyError:
                    raise ParamError(
                        f"{field.name!r} is a required parameter for {cls}!"
                    )
            else:
                try:
                    opt_kwargs[field.name] = kwargs[field.name]
                except KeyError:
                    pass
        opt_kwargs = {k: v for k, v in opt_kwargs.items() if v is not OPT}
        return req_kwargs, opt_kwargs

    def to_dict(self) -> T_KWARGS:
        """
        Convert the dataclass to a complete dictionary with all fields.
        """
        return dataclasses.asdict(self)

    def to_kwargs(self) -> T_KWARGS:
        """
        Convert the dataclass to a dictionary suitable for function calls.
        """
        return {k: v for k, v in dataclasses.asdict(self).items() if v is not OPT}


@dataclasses.dataclass
class BaseModel(BaseModelMixin):
    pass


@dataclasses.dataclass(frozen=True)
class BaseFrozenModel(BaseModelMixin):
    pass
