---
name: func-args
description: Guide for using the func_args Python library (>=1.0.2) — sentinel-based function argument handling with REQ/OPT markers and enhanced dataclasses. Use when writing API wrappers, parameter validation, or dataclass-based config objects.
---

# func_args Library Usage Guide

`func_args` is a lightweight, zero-dependency Python library (requires Python >=3.10) that provides sentinel values for enhanced function argument handling. Install with `pip install func_args`.

**All public API is imported from `func_args.api`:**

```python
from func_args.api import (
    REQ,                # sentinel: marks a parameter as required
    OPT,                # sentinel: marks a parameter as optional (excluded from kwargs)
    check_required,     # raises ParamError if any value is REQ
    remove_optional,    # returns new dict with OPT values removed
    prepare_kwargs,     # check_required + remove_optional in one pass
    BaseModel,          # mutable dataclass mixin with REQ/OPT support
    BaseFrozenModel,    # frozen dataclass mixin with REQ/OPT support
    ParamError,         # exception for missing required parameters
    T_KWARGS,           # type alias: dict[str, Any]
    T_OPT_KWARGS,       # type alias: T_KWARGS | None
)
```

## Core Concept

`REQ` and `OPT` are singleton sentinel values used as default parameter values:

- **`REQ`** — marks a parameter as required. If the caller doesn't provide it, validation raises `ParamError`.
- **`OPT`** — marks a parameter as optional. It is automatically stripped from the final kwargs dict, so unprovided optional params never reach the downstream API.

Use identity checks (`is`), never equality (`==`):

```python
if value is REQ: ...
if value is OPT: ...
```

## Use Case 1: Wrapping Third-Party APIs

The primary use case. Create a better interface around an existing function you cannot modify:

```python
from func_args.api import REQ, OPT, prepare_kwargs

# Third-party API you cannot change
def s3_put_object(Bucket, Key, Body, Metadata=None, Tags=None):
    ...

# Your enhanced wrapper
def put_object(
    Bucket: str = REQ,
    Key: str = REQ,
    Body: bytes = REQ,
    Metadata: dict | None = OPT,
    Tags: dict | None = OPT,
):
    # Custom logic for optional params
    if Metadata is OPT:
        Metadata = {"creator": "admin"}

    kwargs = dict(
        Bucket=Bucket, Key=Key, Body=Body,
        Metadata=Metadata, Tags=Tags,
    )
    # prepare_kwargs does two things in one pass:
    # 1. Raises ParamError if any value is still REQ
    # 2. Removes any value that is still OPT
    return s3_put_object(**prepare_kwargs(**kwargs))

# Usage:
put_object(Bucket="b", Key="k", Body=b"data")           # works
put_object(Bucket="b", Key="k", Body=b"data", Tags={})   # works, Tags included
put_object(Bucket="b", Key="k")                           # raises ParamError for Body
```

## Use Case 2: Individual Utilities

Use `check_required` and `remove_optional` separately when you need finer control:

```python
from func_args.api import REQ, OPT, check_required, remove_optional

def create_user(username=REQ, email=REQ, nickname=OPT, role="user"):
    check_required(username=username, email=email)
    return remove_optional(
        username=username, email=email,
        nickname=nickname, role=role,
    )

create_user(username="alice", email="a@b.com")
# -> {"username": "alice", "email": "a@b.com", "role": "user"}

create_user(username="bob", email="b@b.com", nickname="Bobby")
# -> {"username": "bob", "email": "b@b.com", "nickname": "Bobby", "role": "user"}
```

## Use Case 3: Enhanced Dataclasses

`BaseModel` and `BaseFrozenModel` are dataclass mixins that:

1. **Bypass field ordering restrictions** — OPT/REQ fields can appear in any order (standard dataclasses require non-default fields before default fields).
2. **Validate REQ fields on init** — Raises `ParamError` immediately if a REQ field is missing.
3. **Provide `to_dict()` and `to_kwargs()`** — Convert to dict with or without OPT values.

```python
import dataclasses
from func_args.api import BaseModel, REQ, OPT

@dataclasses.dataclass
class DeployConfig(BaseModel):
    # OPT fields can come BEFORE REQ fields — no ordering restriction
    region: str = dataclasses.field(default=OPT)
    env: str = dataclasses.field(default="prod")
    app_name: str = dataclasses.field(default=REQ)
    tags: list = dataclasses.field(default_factory=list)

config = DeployConfig(app_name="my-service")

config.to_dict()
# {"region": OPT, "env": "prod", "app_name": "my-service", "tags": []}

config.to_kwargs()
# {"env": "prod", "app_name": "my-service", "tags": []}

DeployConfig()  # raises ParamError
```

### Frozen Dataclass with Computed Fields

```python
import dataclasses
from func_args.api import BaseFrozenModel, REQ, OPT

@dataclasses.dataclass(frozen=True)
class Document(BaseFrozenModel):
    title: str = dataclasses.field(default=REQ)
    author: str = dataclasses.field(default=OPT)
    slug: str = dataclasses.field(init=False)

    def __post_init__(self):
        super().__post_init__()  # validates REQ fields first
        object.__setattr__(self, "slug", self.title.lower().replace(" ", "-"))

doc = Document(title="API Guide")
doc.to_kwargs()
# {"title": "API Guide", "slug": "api-guide"}  — "author" excluded (still OPT)
```

### Splitting kwargs with `_split_req_opt`

```python
kwargs = {"app_name": "svc", "region": "us-east-1", "env": "staging", "tags": ["v2"]}
req, opt = DeployConfig._split_req_opt(kwargs)
# req = {"app_name": "svc"}
# opt = {"region": "us-east-1", "env": "staging", "tags": ["v2"]}
```

## API Quick Reference

| Symbol | Description |
|---|---|
| `REQ` | Sentinel for required parameters |
| `OPT` | Sentinel for optional parameters (auto-removed) |
| `check_required(**kw) -> None` | Raises `ParamError` if any value `is REQ` |
| `remove_optional(**kw) -> dict` | Returns new dict with `OPT` values removed |
| `prepare_kwargs(**kw) -> dict` | `check_required` + `remove_optional` in one pass |
| `BaseModel` | Mutable dataclass mixin (use with `@dataclasses.dataclass`) |
| `BaseFrozenModel` | Frozen dataclass mixin (use with `@dataclasses.dataclass(frozen=True)`) |
| `ParamError` | Exception for missing required parameters |

## Key Rules

1. **Always use `is` for sentinel checks**, never `==`.
2. **All three functions take `**kwargs`**, not a dict: `prepare_kwargs(**my_dict)`, not `prepare_kwargs(my_dict)`.
3. **Dataclass fields use `dataclasses.field(default=REQ)`**, not bare `REQ` as default (bare defaults work but `field()` is the canonical pattern).
4. **Import from `func_args.api`** for the public API surface.
5. **`to_kwargs()` excludes OPT values**, `to_dict()` includes them.
