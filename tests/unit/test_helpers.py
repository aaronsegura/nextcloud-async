import pytest
from httpx import Headers

from nextcloud_async.exceptions import NextcloudForbiddenError
from nextcloud_async.helpers import (
    bool2int,
    bool2str,
    filter_headers,
    password_confirmation_required,
    phone_number_to_e164,
    recursive_urlencode,
)


class TestBool2Int:
    def test_invalid_input(self):
        with pytest.raises(TypeError):
            bool2int("string")  # type: ignore

    def test_valid_inputs(self):
        assert bool2int(True) == 1
        assert bool2int(False) == 0


class TestBool2Str:
    def test_invalid_input(self):
        with pytest.raises(TypeError):
            bool2str("string")  # type: ignore

    def test_valid_inputs(self):
        assert bool2str(True) == "true"
        assert bool2str(False) == "false"


class TestPhoneNumberToE164:
    def test_invalid_input_type(self):
        with pytest.raises(TypeError):
            phone_number_to_e164(float(1.0))  # type: ignore

    def test_invalid_input(self):
        with pytest.raises(ValueError):
            phone_number_to_e164("82738jv9jadfj")

    def test_valid_int_input(self):
        result = phone_number_to_e164(80087355)
        assert result == "5.5.3.7.8.0.0.8.e164.arpa"

    def test_valid_string_input(self):
        result = phone_number_to_e164("80087355")
        assert result == "5.5.3.7.8.0.0.8.e164.arpa"


def test_filter_headers():
    httpx_headers = Headers({"HeaderKey": "HeaderValue"})
    result = filter_headers(["HeaderKey"], httpx_headers)
    assert result == {"HeaderKey": "HeaderValue"}


def test_recursive_urlencode_nested_dict():
    a = {"configData": {"key1": "val1", "key2": "val2"}, "key3": "val3"}
    r = recursive_urlencode(a)
    assert r == "configData[key1]=val1&configData[key2]=val2&key3=val3"
