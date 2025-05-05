# -*- coding: utf-8 -*-

import pytest

from func_args.arg import REQ, OPT, check_required, remove_optional, prepare_kwargs


class TestSentinels:
    """Tests for sentinel objects."""

    def test_sentinel_identity(self):
        """Verify that sentinel objects maintain identity."""
        assert REQ is REQ
        assert OPT is OPT
        assert REQ is not OPT
        assert REQ != OPT
        assert REQ != None
        assert OPT != None

    def test_sentinel_through_function(self):
        """Verify sentinel identity is preserved through function calls."""

        def get_req():
            return REQ

        def get_opt():
            return OPT

        assert get_req() is REQ
        assert get_opt() is OPT


class TestCheckRequired:
    """Tests for check_required function."""

    def test_no_required_args(self):
        """Should not raise error when no REQ values are present."""
        # No REQ values
        check_required(**{"a": 1, "b": "test", "c": None})
        # Empty dict
        check_required()

    def test_with_required_args(self):
        """Should raise ValueError when REQ values are present."""
        with pytest.raises(ValueError, match="Missing required argument: 'b'"):
            check_required(**{"a": 1, "b": REQ})

        with pytest.raises(ValueError, match="Missing required argument: 'missing'"):
            check_required(**{"present": "value", "missing": REQ})


class TestRemoveOptional:
    """Tests for remove_optional function."""

    def test_no_optional_args(self):
        """Should return identical dict when no OPT values are present."""
        # No OPT values
        result = remove_optional(**{"a": 1, "b": "test", "c": None})
        assert result == {"a": 1, "b": "test", "c": None}
        # Empty dict
        assert remove_optional() == {}

    def test_with_optional_args(self):
        """Should remove keys with OPT values."""
        result = remove_optional(**{"a": 1, "b": OPT, "c": OPT, "d": None})
        assert result == {"a": 1, "d": None}
        # All OPT values
        assert remove_optional(**{"a": OPT, "b": OPT}) == {}


class TestPrepareKwargs:
    """Tests for prepare_kwargs function."""

    def test_normal_args(self):
        """Should return dict with normal values unchanged."""
        kwargs = {"a": 1, "b": "test", "c": None, "d": False}
        result = prepare_kwargs(**kwargs)
        assert result == kwargs
        assert result is not kwargs  # Should be a new dict

    def test_optional_args(self):
        """Should remove OPT values."""
        result = prepare_kwargs(**{"a": 1, "b": OPT, "c": "test"})
        assert result == {"a": 1, "c": "test"}

    def test_required_args(self):
        """Should raise ValueError for REQ values."""
        with pytest.raises(ValueError, match="Missing required argument: 'b'"):
            prepare_kwargs(**{"a": 1, "b": REQ, "c": "test"})

    def test_mixed_args(self):
        """Should handle mix of normal, OPT and REQ values."""
        # Should remove OPT but fail on REQ
        with pytest.raises(ValueError, match="Missing required argument: 'c'"):
            prepare_kwargs(**{"a": 1, "b": OPT, "c": REQ, "d": None})

        # Should handle OPT correctly when no REQ present
        result = prepare_kwargs(**{"a": 1, "b": OPT, "d": None})
        assert result == {"a": 1, "d": None}


class TestComplexUsage:
    """Tests for real-world usage patterns."""

    def test_api_wrapper_example(self):
        """Test the module in an API wrapper scenario."""

        # Mock external API
        def original_api(bucket, key, body, metadata=None, tags=None):
            return {
                "bucket": bucket,
                "key": key,
                "body": body,
                "metadata": metadata,
                "tags": tags,
            }

        # Our wrapper with REQ and OPT
        def enhanced_api(
            bucket=REQ,
            key=REQ,
            body=REQ,
            metadata=OPT,
            tags=OPT,
            extra_option=None,
        ):
            kwargs = {
                "bucket": bucket,
                "key": key,
                "body": body,
                "metadata": metadata,
                "tags": tags,
            }
            processed = prepare_kwargs(**kwargs)
            # Add our additional parameter that wasn't in original API
            if extra_option:
                processed["metadata"] = processed.get("metadata", {})
                if isinstance(processed["metadata"], dict):
                    processed["metadata"]["extra"] = extra_option

            return original_api(**processed)

        # Test with all required args
        result = enhanced_api(bucket="my-bucket", key="file.txt", body=b"content")
        assert result == {
            "bucket": "my-bucket",
            "key": "file.txt",
            "body": b"content",
            "metadata": None,
            "tags": None,
        }

        # Test with extra option
        result = enhanced_api(
            bucket="my-bucket", key="file.txt", body=b"content", extra_option="special"
        )
        assert result == {
            "bucket": "my-bucket",
            "key": "file.txt",
            "body": b"content",
            "metadata": {"extra": "special"},
            "tags": None,
        }

        # Test with missing required arg
        with pytest.raises(ValueError, match="Missing required argument: 'body'"):
            enhanced_api(bucket="my-bucket", key="file.txt")


if __name__ == "__main__":
    from func_args.tests import run_cov_test

    run_cov_test(
        __file__,
        "func_args.arg",
        preview=False,
    )
