# -*- coding: utf-8 -*-

import pytest
import dataclasses
from datetime import datetime, date


from func_args.exc import ParamError
from func_args.dataclass import BaseModel, BaseFrozenModel, REQ, OPT


@dataclasses.dataclass
class Person(BaseModel):
    """Simple test class with required and optional fields."""

    # Required field
    name: str = dataclasses.field(default=REQ)
    # Optional field
    age: int = dataclasses.field(default=OPT)
    # Field with default value
    active: bool = dataclasses.field(default=True)
    # Field with default_factory
    tags: list = dataclasses.field(default_factory=list)


class TestBaseModel:
    """Tests for BaseModel functionality."""

    def test_init_with_required(self):
        """Should initialize when all required fields are provided."""
        person = Person(name="Alice")
        assert person.name == "Alice"
        assert person.age is OPT
        assert person.active is True
        assert person.tags == []

        # Providing non-required fields
        person = Person(name="Bob", age=30, active=False, tags=["employee"])
        assert person.name == "Bob"
        assert person.age == 30
        assert person.active is False
        assert person.tags == ["employee"]

    def test_init_missing_required(self):
        """Should raise ParamError when required fields are missing."""
        with pytest.raises(ParamError):
            Person()

    def test_to_dict(self):
        """to_dict() should return complete dictionary with sentinel values."""
        person = Person(name="Bob")
        result = person.to_dict()
        assert result == {"name": "Bob", "age": OPT, "active": True, "tags": []}

    def test_to_kwargs(self):
        """to_kwargs() should return dictionary with OPT values removed."""
        # Simple case
        person = Person(name="Charlie")
        result = person.to_kwargs()

        assert result == {"name": "Charlie", "active": True, "tags": []}

        # With optional values provided
        person = Person(name="Dave", age=30)
        result = person.to_kwargs()

        assert result == {"name": "Dave", "age": 30, "active": True, "tags": []}

        # Default mutables should be different instances
        person1 = Person(name="Alice")
        person2 = Person(name="Bob")
        person1.tags.append("tag1")

        assert "tag1" in person1.tags
        assert "tag1" not in person2.tags

    def test_split_req_opt(self):
        """_split_req_opt() should correctly separate required and optional kwargs."""
        # All required and some optional
        kwargs = {"name": "Dave", "age": 30, "active": False, "tags": ["admin"]}
        req, opt = Person._split_req_opt(kwargs)
        assert req == {"name": "Dave"}
        assert opt == {"age": 30, "active": False, "tags": ["admin"]}

        # Missing required fields
        kwargs = {"age": 30, "active": False}

        with pytest.raises(ParamError):
            Person._split_req_opt(kwargs)

    def test_split_req_opt_edge_case(self):
        @dataclasses.dataclass
        class MyClass(BaseModel):
            """
            Define OPT field first
            """

            field1: str = dataclasses.field(default=OPT)
            field2: int = dataclasses.field(default=REQ)

        with pytest.raises(ParamError):
            MyClass._split_req_opt({"in_valid_field": None})


@dataclasses.dataclass(frozen=True)
class Document(BaseFrozenModel):
    """Test class with frozen=True and init=False computed fields."""

    # Regular fields with different defaults
    title: str = dataclasses.field(default=REQ)
    author: str = dataclasses.field(default=OPT)
    created_date: date = dataclasses.field(default_factory=date.today)
    version: int = dataclasses.field(default=1)

    # init=False fields that are computed in __post_init__
    word_count: int = dataclasses.field(init=False)
    title_length: int = dataclasses.field(init=False)
    slug: str = dataclasses.field(init=False)
    last_modified: datetime = dataclasses.field(init=False)

    def __post_init__(self):
        """Initialize the computed fields after normal initialization."""
        super().__post_init__()  # Call parent's post_init first for validation

        # Using object.__setattr__ since the dataclass is frozen
        object.__setattr__(self, "word_count", len(self.title.split()))
        object.__setattr__(self, "title_length", len(self.title))
        object.__setattr__(self, "slug", self.title.lower().replace(" ", "-"))
        object.__setattr__(self, "last_modified", datetime.now())


class TestBaseFrozenModel:
    """Tests for frozen dataclasses with init=False computed fields."""

    def test_init_with_computed_fields(self):
        """Should correctly initialize and compute init=False fields."""
        doc = Document(title="Test Document")

        # Check regular fields
        assert doc.title == "Test Document"
        assert doc.author is OPT
        assert doc.version == 1
        assert isinstance(doc.created_date, date)

        # Check computed fields
        assert doc.word_count == 2  # "Test Document" has 2 words
        assert doc.title_length == 13  # Length of "Test Document"
        assert doc.slug == "test-document"
        assert isinstance(doc.last_modified, datetime)

    def test_frozen_with_init_false_to_dict(self):
        """to_dict() should include init=False computed fields."""
        doc = Document(title="Hello World", author="Jane Doe")

        result = doc.to_dict()

        # Should include all fields
        assert result["title"] == "Hello World"
        assert result["author"] == "Jane Doe"
        assert result["word_count"] == 2
        assert result["title_length"] == 11
        assert result["slug"] == "hello-world"
        assert isinstance(result["last_modified"], datetime)

    def test_frozen_with_init_false_to_kwargs(self):
        """to_kwargs() should include init=False fields but exclude OPT values."""
        doc = Document(title="API Documentation")

        result = doc.to_kwargs()

        # Should include all fields except those with OPT value
        assert "title" in result
        assert "author" not in result  # OPT should be excluded
        assert "word_count" in result
        assert "title_length" in result
        assert "slug" in result
        assert "last_modified" in result
        assert "version" in result
        assert "created_date" in result

        assert result["word_count"] == 2
        assert result["title_length"] == 17
        assert result["slug"] == "api-documentation"

    def test_frozen_immutability(self):
        """Should not allow changing fields after initialization."""
        doc = Document(title="Immutable Document")

        # Attempting to modify any field should raise an error
        with pytest.raises(dataclasses.FrozenInstanceError):
            doc.title = "New Title"

        with pytest.raises(dataclasses.FrozenInstanceError):
            doc.word_count = 100

        # But the computed values should be set correctly at initialization
        assert doc.word_count == 2
        assert doc.title_length == 18
        assert doc.slug == "immutable-document"


if __name__ == "__main__":
    from func_args.tests import run_cov_test

    run_cov_test(
        __file__,
        "func_args.dataclass",
        preview=False,
    )
