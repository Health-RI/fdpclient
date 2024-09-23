# SPDX-FileCopyrightText: 2024 Stichting Health-RI
#
# SPDX-License-Identifier: MIT

import pytest
import requests

from fdpclient.basicclient import BasicAPIClient


@pytest.fixture
def basic_mock(requests_mock):
    requests_mock.get("http://example.com/get", text="get")
    requests_mock.post("http://example.com/post", text="post")
    requests_mock.put("http://example.com/put", text="update")
    requests_mock.patch("http://example.com/patch", text="patch")
    requests_mock.delete("http://example.com/delete", text="delete")
    requests_mock.head("http://example.com/head", headers={"content-type": "application/json+ld"})

    requests_mock.get("http://example.com/404", status_code=404)

    return BasicAPIClient("http://example.com", {})


def test_basics(basic_mock):
    assert basic_mock.get("/get").text == "get"
    assert basic_mock.update("put").text == "update"
    assert basic_mock.patch("patch").text == "patch"
    assert basic_mock.post("/post").text == "post"
    assert basic_mock.delete("delete").text == "delete"


def test_404(basic_mock):
    with pytest.raises(requests.HTTPError):
        basic_mock.get("404")


def test_unknown_method(basic_mock):
    with pytest.raises(expected_exception=ValueError, match="Unsupported method"):
        basic_mock._call_method("head", "head")  # noqa: SLF001
