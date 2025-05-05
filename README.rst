
.. .. image:: https://readthedocs.org/projects/func-args/badge/?version=latest
    :target: https://func-args.readthedocs.io/en/latest/
    :alt: Documentation Status

.. image:: https://github.com/MacHu-GWU/func_args-project/actions/workflows/main.yml/badge.svg
    :target: https://github.com/MacHu-GWU/func_args-project/actions?query=workflow:CI

.. image:: https://codecov.io/gh/MacHu-GWU/func_args-project/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/MacHu-GWU/func_args-project

.. image:: https://img.shields.io/pypi/v/func-args.svg
    :target: https://pypi.python.org/pypi/func-args

.. image:: https://img.shields.io/pypi/l/func-args.svg
    :target: https://pypi.python.org/pypi/func-args

.. image:: https://img.shields.io/pypi/pyversions/func-args.svg
    :target: https://pypi.python.org/pypi/func-args

.. image:: https://img.shields.io/badge/✍️_Release_History!--None.svg?style=social&logo=github
    :target: https://github.com/MacHu-GWU/func_args-project/blob/main/release-history.rst

.. image:: https://img.shields.io/badge/⭐_Star_me_on_GitHub!--None.svg?style=social&logo=github
    :target: https://github.com/MacHu-GWU/func_args-project

------

.. .. image:: https://img.shields.io/badge/Link-API-blue.svg
    :target: https://func-args.readthedocs.io/en/latest/py-modindex.html

.. image:: https://img.shields.io/badge/Link-Install-blue.svg
    :target: `install`_

.. image:: https://img.shields.io/badge/Link-GitHub-blue.svg
    :target: https://github.com/MacHu-GWU/func_args-project

.. image:: https://img.shields.io/badge/Link-Submit_Issue-blue.svg
    :target: https://github.com/MacHu-GWU/func_args-project/issues

.. image:: https://img.shields.io/badge/Link-Request_Feature-blue.svg
    :target: https://github.com/MacHu-GWU/func_args-project/issues

.. image:: https://img.shields.io/badge/Link-Download-blue.svg
    :target: https://pypi.org/pypi/func-args#files


Welcome to ``func_args`` Documentation
==============================================================================


Overview
------------------------------------------------------------------------------
``func_args`` is a lightweight Python library for creating wrapper functions with enhanced argument handling. It solves common problems when working with third-party APIs that have suboptimal interface designs.

The library provides sentinel values (``REQ`` and ``OPT``) that can be used as function parameter defaults to:

- Mark parameters as required
- Mark parameters as optional and easily exclude them from kwargs

Additionally, ``func_args`` includes `dataclasses <https://docs.python.org/3/library/dataclasses.html>`_ enhancements for parameter validation and conversion.


Design Philosophy
------------------------------------------------------------------------------
``func_args`` follows these core principles:

1. **Explicit over implicit** - Parameters are clearly marked as required or optional
2. **Fail fast** - Required parameters are validated early
3. **Minimal overhead** - Simple API with minimal processing cost
4. **Flexible integration** - Works with any Python function without modifying the original
5. **Type hint support** - Full support for Python type annotations
6. **Consistent error handling** - Clear error messages for missing required parameters

The library solves several common problems:

- Creating wrapper functions around third-party APIs with poor parameter interfaces
- Building flexible functions with many optional parameters
- Enforcing required parameters without complex conditional logic
- Removing optional parameters from kwargs dictionaries to avoid passing unused parameters


Usage Examples
------------------------------------------------------------------------------


Basic Sentinels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In this example, we create a wrapper around an AWS S3 `put_object <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/put_object.html>`_ API:

.. code-block:: python

    def put_object(
        Bucket: str,
        Key: str,
        Body: bytes,
        Metadata: T.Optional[dict[str, str]] = ...,
        Tags: T.Optional[dict[str, str]] = ...,
    ):
        ...

.. code-block:: python

    from func_args.api import REQ, OPT, prepare_kwargs

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

        # This will:
        # 1. Raise ParamError if any REQ values remain
        # 2. Remove any OPT values
        # 3. Return a clean dict with only provided values
        cleaned_kwargs = prepare_kwargs(kwargs)

        # Call the original API with only the necessary parameters
        return put_object(**cleaned_kwargs)


Required Parameter Validation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: python

    from func_args.arg import REQ, check_required

    # Function with required parameters
    def create_user(username=REQ, email=REQ, role="user"):
        # Validate required parameters
        check_required(username=username, email=email)

        # If we got here, all required parameters were provided
        return {"username": username, "email": email, "role": role}

    # This works
    user = create_user(username="alice", email="alice@example.com")

    # This raises ParamError: "Missing required argument: 'email'"
    try:
        user = create_user(username="bob")
    except ParamError as e:
        print(e)


Optional Parameter Removal
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: python

    from func_args.arg import OPT, remove_optional

    # Function with many optional parameters
    def search_items(query, limit=10, offset=0, sort_by=OPT, filter_by=OPT, include_deleted=False):
        # Build base query parameters
        params = {
            "query": query,
            "limit": limit,
            "offset": offset,
            "sort_by": sort_by,
            "filter_by": filter_by,
            "include_deleted": include_deleted,
        }

        # Remove optional parameters that weren't provided
        clean_params = remove_optional(**params)

        # Now we can safely pass to the API without sending None values or defaults
        return api_search(**clean_params)


Enhanced Dataclasses
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: python

    import dataclasses
    from func_args.dataclass import BaseModel, REQ, OPT

    @dataclasses.dataclass
    class UserParameters(BaseModel):
        """Parameter class for user operations with validation."""

        # Required fields
        username: str = dataclasses.field(default=REQ)
        email: str = dataclasses.field(default=REQ)

        # Optional fields
        display_name: str = dataclasses.field(default=OPT)
        role: str = dataclasses.field(default="user")
        tags: list = dataclasses.field(default_factory=list)

        def validate_email(self):
            """Additional validation logic."""
            if not "@" in self.email:
                raise ValueError("Invalid email format")

        def __post_init__(self):
            # Call the base class validation
            super().__post_init__()
            # Perform additional validation
            self.validate_email()

    # Usage
    params = UserParameters(username="alice", email="alice@example.com")

    # Convert to dict with all fields (including OPT sentinel values)
    full_dict = params.to_dict()
    # {"username": "alice", "email": "alice@example.com", "display_name": OPT, "role": "user", "tags": []}

    # Convert to dict with only provided values (excluding OPT sentinels)
    kwargs = params.to_kwargs()
    # {"username": "alice", "email": "alice@example.com", "role": "user", "tags": []}


.. _install:

Install
------------------------------------------------------------------------------

``func_args`` is released on PyPI, so all you need is to:

.. code-block:: console

    $ pip install func-args

To upgrade to latest version:

.. code-block:: console

    $ pip install --upgrade func-args
