.. _release_history:

Release and Version History
==============================================================================


Backlog (TODO)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

**Minor Improvements**

**Bugfixes**

**Miscellaneous**

- Deprecate ``NOTHING``, ``resolve_kwargs`` in ``2.X``


1.0.2 (2026-04-28)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Minor Improvements**

- Modernize type hints for Python 3.10+: use ``dict[str, Any]``, ``tuple[...]``, and ``X | None`` instead of ``typing.Dict``, ``typing.Tuple``, ``typing.Optional``.
- Add return type annotations to ``check_required``, ``_validate``, and ``__post_init__``.
- Improve ``to_kwargs()`` and ``_split_req_opt()`` efficiency by using inline dict comprehension instead of routing through ``remove_optional(**...)``.
- Use idiomatic ``value is not OPT`` instead of ``(value is OPT) is False`` in ``remove_optional()``.

**Bugfixes**

- Fix incorrect sentinel name ``NA`` in module docstring (should be ``OPT``).
- Fix docstring examples showing ``prepare_kwargs(dict)`` instead of correct ``prepare_kwargs(**dict)`` syntax.
- Fix doctest showing ``ValueError`` instead of ``ParamError`` in ``prepare_kwargs`` docstring.
- Remove incorrect ``# pragma: no cover`` annotations on code paths that are actually covered by tests.

**Miscellaneous**

- Migrate project tooling from Poetry/Makefile to uv/mise.
- Update README with comprehensive usage examples and API reference table.


1.0.1 (2025-05-06)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Bugfixes**

- Add the old ``NOTHING`` API in ``>=0.1.1,<1.0.0`` back as an alias of ``OPT``.
- Add the old ``resolve_kwargs`` API in ``>=0.1.1,<1.0.0`` back as an alias of ``remove_optional``.
- YANK 1.0.0.


1.0.0 (2025-05-05)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**💥Breaking Changes**

- Public API are moved away from ``func_args`` to ``func_args.api`` name space.
- All public API in ``func_args<1.0.0`` is removed.
- ``NOTHING`` is replaced by ``func_args.api.OPT``.
- ``resolve_kwargs`` is replaced by ``func_args.api.remove_optional``.

**Features and Improvements**

- Add the following Public APIs.
    - ``func_args.api.T_KWARGS``
    - ``func_args.api.T_OPT_KWARGS``
    - ``func_args.api.ParamError``
    - ``func_args.api.REQ``
    - ``func_args.api.OPT``
    - ``func_args.api.check_required``
    - ``func_args.api.remove_optional``
    - ``func_args.api.prepare_kwargs``
    - ``func_args.api.BaseModel``
    - ``func_args.api.BaseFrozenModel``
- Upgrade the underlying ``sentinel`` package to ``1.0.0``.


0.1.1 (2023-02-16)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- First release
- add sentinel ``NOTHING``.
- add ``resolve_kwargs``.
