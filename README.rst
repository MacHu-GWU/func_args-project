
.. image:: https://readthedocs.org/projects/func-args/badge/?version=latest
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

.. image:: https://img.shields.io/badge/Link-API-blue.svg
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
.. image:: https://func-args.readthedocs.io/en/latest/_static/func_args-logo.png
    :target: https://func-args.readthedocs.io/en/latest/


Overview
------------------------------------------------------------------------------
``func_args`` is a lightweight, zero-dependency Python library that provides sentinel values (``REQ`` and ``OPT``) for enhanced function argument handling. It solves common problems when creating wrapper functions around third-party APIs.

**Key features:**

- ``REQ`` sentinel — marks parameters as required, with early validation
- ``OPT`` sentinel — marks parameters as optional, automatically excluded from kwargs
- ``prepare_kwargs()`` — validates required and removes optional in one pass
- ``BaseModel`` / ``BaseFrozenModel`` — dataclass mixins that bypass the "default after non-default" ordering limitation


.. _install:

Install
------------------------------------------------------------------------------

.. code-block:: console

    $ pip install func-args


Usage
------------------------------------------------------------------------------


1. Wrapping Third-Party APIs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The most common use case: creating a better interface around an existing API.

.. code-block:: python

    from func_args.api import REQ, OPT, prepare_kwargs

    # Suppose this is a third-party API you cannot modify:
    def put_object(Bucket, Key, Body, Metadata=None, Tags=None):
        """AWS S3 put_object simplified."""
        ...

    # Your enhanced wrapper:
    def better_put_object(
        Bucket: str = REQ,
        Key: str = REQ,
        Body: bytes = REQ,
        Metadata: dict | None = OPT,
        Tags: dict | None = OPT,
    ):
        # You can add custom logic for optional params
        if Metadata is OPT:
            Metadata = {"creator": "admin"}

        kwargs = dict(
            Bucket=Bucket,
            Key=Key,
            Body=Body,
            Metadata=Metadata,
            Tags=Tags,
        )
        # prepare_kwargs will:
        # 1. Raise ParamError if any value is still REQ (caller forgot it)
        # 2. Remove any value that is still OPT (caller didn't provide it)
        # 3. Return a clean dict ready for the real API call
        return put_object(**prepare_kwargs(**kwargs))

    # Works - Tags is OPT so it gets removed automatically
    better_put_object(Bucket="my-bucket", Key="file.txt", Body=b"hello")

    # Raises ParamError: "Missing required argument: 'Body'"
    better_put_object(Bucket="my-bucket", Key="file.txt")


2. Individual Utilities
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
You can also use ``check_required`` and ``remove_optional`` separately:

.. code-block:: python

    from func_args.api import REQ, OPT, check_required, remove_optional

    def create_user(username=REQ, email=REQ, nickname=OPT, role="user"):
        # Step 1: validate required params
        check_required(username=username, email=email)

        # Step 2: build kwargs and remove OPT values
        kwargs = remove_optional(
            username=username,
            email=email,
            nickname=nickname,
            role=role,
        )
        return kwargs

    create_user(username="alice", email="alice@example.com")
    # -> {"username": "alice", "email": "alice@example.com", "role": "user"}

    create_user(username="bob", email="bob@example.com", nickname="Bobby")
    # -> {"username": "bob", "email": "bob@example.com", "nickname": "Bobby", "role": "user"}


3. Enhanced Dataclasses
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
``BaseModel`` and ``BaseFrozenModel`` let you define dataclasses with ``REQ``/``OPT``
defaults in **any order** — no more "fields without defaults must come before fields
with defaults" restriction.

.. code-block:: python

    import dataclasses
    from func_args.api import BaseModel, BaseFrozenModel, REQ, OPT

    @dataclasses.dataclass
    class DeployConfig(BaseModel):
        """
        Note: OPT fields can appear BEFORE REQ fields.
        Standard dataclasses would reject this ordering.
        """
        region: str = dataclasses.field(default=OPT)      # optional, listed first
        env: str = dataclasses.field(default="prod")       # has default
        app_name: str = dataclasses.field(default=REQ)     # required, listed last
        tags: list = dataclasses.field(default_factory=list)

    # REQ fields must be provided, OPT fields are truly optional
    config = DeployConfig(app_name="my-service")
    assert config.app_name == "my-service"
    assert config.region is OPT
    assert config.env == "prod"

    # to_dict() returns all fields including sentinel values
    config.to_dict()
    # {"region": OPT, "env": "prod", "app_name": "my-service", "tags": []}

    # to_kwargs() returns only provided values (OPT filtered out)
    config.to_kwargs()
    # {"env": "prod", "app_name": "my-service", "tags": []}

    # Missing required field raises ParamError immediately
    DeployConfig()  # raises ParamError: "Field 'app_name' is required ..."


4. Frozen Dataclass with Computed Fields
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: python

    @dataclasses.dataclass(frozen=True)
    class Document(BaseFrozenModel):
        title: str = dataclasses.field(default=REQ)
        author: str = dataclasses.field(default=OPT)
        version: int = dataclasses.field(default=1)

        # Computed fields (init=False) work seamlessly
        slug: str = dataclasses.field(init=False)

        def __post_init__(self):
            super().__post_init__()  # validates REQ fields first
            object.__setattr__(self, "slug", self.title.lower().replace(" ", "-"))

    doc = Document(title="API Guide")
    assert doc.slug == "api-guide"
    assert doc.to_kwargs() == {"title": "API Guide", "version": 1, "slug": "api-guide"}
    # "author" excluded because it's still OPT


API Reference
------------------------------------------------------------------------------

+---------------------------+-----------------------------------------------------------+
| Symbol                    | Description                                               |
+===========================+===========================================================+
| ``REQ``                   | Sentinel marking a required parameter                     |
+---------------------------+-----------------------------------------------------------+
| ``OPT``                   | Sentinel marking an optional parameter                    |
+---------------------------+-----------------------------------------------------------+
| ``check_required(**kw)``  | Raises ``ParamError`` if any value is ``REQ``             |
+---------------------------+-----------------------------------------------------------+
| ``remove_optional(**kw)`` | Returns new dict with ``OPT`` values removed              |
+---------------------------+-----------------------------------------------------------+
| ``prepare_kwargs(**kw)``  | Combines check_required + remove_optional in one pass     |
+---------------------------+-----------------------------------------------------------+
| ``BaseModel``             | Mutable dataclass mixin with REQ/OPT support              |
+---------------------------+-----------------------------------------------------------+
| ``BaseFrozenModel``       | Frozen (immutable) dataclass mixin with REQ/OPT support   |
+---------------------------+-----------------------------------------------------------+
| ``ParamError``            | Exception raised for missing required parameters          |
+---------------------------+-----------------------------------------------------------+


AI Agent Skill
------------------------------------------------------------------------------
This project ships a self-contained `Agent skill <https://code.claude.com/docs/skills>`_ at ``.claude/skills/func-args/SKILL.md``. Copy this file into your project's ``.claude/skills/`` directory and your AI coding agent will know how to use ``func_args`` correctly — including API usage patterns, dataclass examples, and common pitfalls.
