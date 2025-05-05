# -*- coding: utf-8 -*-

"""
This module provides tools for handling function arguments with special sentinel
values to indicate required parameters (REQ) or optional parameters (OPT).
It's particularly useful for creating wrappers around existing APIs.

Key concepts:

- REQ: Sentinel value marking parameters that must be provided
- OPT: Sentinel value marking parameters that can be omitted from the final kwargs

Example::

    # In this example, we create a wrapper around an AWS S3 put_object API
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/put_object.html
    def put_object(
        Bucket: str,
        Key: str,
        Body: bytes,
        Metadata: T.Optional[dict[str, str]] = ...,
        Tags: T.Optional[dict[str, str]] = ...,
    ):
        ...

    # Our enhanced wrapper with REQ and OPT
    def better_put_object(
        Bucket: str = REQ,
        Key: str = REQ,
        Body: bytes = REQ,
        Metadata: T.Optional[dict[str, str]] = OPT,
        Tags: T.Optional[dict[str, str]] = OPT,
    ):
        # custom parameter handling
        if Metadata is NA:
            Metadata = {"creator": "admin"}
        if Tags is NA:
            Tags = {"creator": "admin"}

        # Prepare kwargs with validation
        kwargs = dict(
            Bucket=Bucket,
            Key=Key,
            Body=Body,
            Metadata=Metadata,
            Tags=Tags,
        )
        cleaned_kwargs = prepare_kwargs(kwargs)
        return put_object(**cleaned_kwargs)

"""

from .vendor import sentinel
from .type_hint import T_KWARGS
from .exc import ParamError

REQ = sentinel.create(name="REQ")
OPT = sentinel.create(name="OPT")


def check_required(**kwargs):
    """
    Check and validate required arguments in kwargs.

    Raises ValueError if any required arguments (marked with REQ) are found.

    The function signature ``def check_required(**kwargs: T_KWARGS):``
    instead of ``def check_required(kwargs: T_KWARGS):`` is a deliberate
    design choice that improves usability.

    With `**kwargs` (Better)::

        # Direct, intuitive usage
        check_required(name="Alice", id=123, email="alice@example.com")

    With dictionary parameter (More cumbersome)::

        # Requires explicit dictionary construction
        check_required({"name": "Alice", "id": 123, "email": "alice@example.com"})
        # OR
        check_required(dict(name="Alice", id=123, email="alice@example.com"))
    """
    for key, value in kwargs.items():
        if value is REQ:
            raise ParamError(f"Missing required argument: {key!r}")


def remove_optional(**kwargs) -> T_KWARGS:
    """
    Remove optional parameters from kwargs.

    Filters out any keyword arguments that have the value OPT,
    returning a new dictionary with only the non-OPT values.
    """
    return {key: value for key, value in kwargs.items() if (value is OPT) is False}


def prepare_kwargs(**kwargs) -> T_KWARGS:
    """
    Process kwargs by checking required args and removing optional ones.

    This function combines the functionality of check_required() and remove_optional()
    in a single pass for efficiency.

    Examples:

    >>> prepare_kwargs({'name': 'test', 'id': 123})
    {'name': 'test', 'id': 123}

    >>> prepare_kwargs({'name': 'test', 'extra': OPT})
    {'name': 'test'}

    >>> prepare_kwargs({'name': 'test', 'id': REQ})
    Traceback (most recent call last):
        ...
    ValueError: Missing required argument: 'id'
    """
    new_kwargs = {}
    for key, value in kwargs.items():
        if value is REQ:
            raise ParamError(f"Missing required argument: {key!r}")
        elif value is OPT:
            pass
        else:
            new_kwargs[key] = value
    return new_kwargs
