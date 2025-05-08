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
