# SPDX-FileCopyrightText: 2024 Stichting Health-RI
#
# SPDX-License-Identifier: MIT

from unittest.mock import MagicMock

import pytest
import requests
from rdflib import Graph, URIRef
from rdflib.compare import to_isomorphic
from rdflib.namespace import DCAT, RDF

from fdpclient.fdpclient import FDPClient
from fdpclient.utils import remove_node_from_graph


@pytest.fixture
def fdp_client_mock(requests_mock):
    requests_mock.post("https://fdp.example.com/tokens", json={"token": "1234abcd"})
    requests_mock.put(
        "https://fdp.example.com/dataset/12345678/meta/state",
    )
    requests_mock.put(
        "https://fdp.example.com/dataset/12345678",
    )
    with open(file="tests/references/fdp_dataset.ttl", mode="rb") as fdp_dataset_file:
        requests_mock.post(
            "https://fdp.example.com/dataset",
            status_code=201,
            headers={"Location": "https://fdp.example.com/dataset/12345678"},
            body=fdp_dataset_file,
        )
        requests_mock.get(
            "https://fdp.example.com/dataset/12345678",
            status_code=200,
            headers={"Content-Type": "text/turtle"},
            body=fdp_dataset_file,
        )

    requests_mock.post(
        "https://fdp.example.com/catalog",
        status_code=201,
        headers={"Location": "https://fdp.example.com/catalog/87654321"},
    )
    requests_mock.post(
        "https://fdp.example.com/distribution",
        status_code=201,
        headers={"Location": "https://fdp.example.com/distribution/abcdefgh"},
    )

    requests_mock.delete(
        "https://fdp.example.com/dataset/12345678",
        status_code=204,
    )
    return FDPClient("https://fdp.example.com", "user@example.com", "pass")


@pytest.fixture
def empty_dataset_graph():
    g = Graph()
    g.add((URIRef("https://example.com/dataset"), RDF.type, DCAT.Dataset))

    return g


def test_fdp_clienterror(requests_mock, empty_dataset_graph):
    requests_mock.post("https://fdp.example.com/tokens", json={"token": "1234abcd"})
    requests_mock.post("https://fdp.example.com/dataset", status_code=418, reason="I'm a teapot")
    fdp_client = FDPClient("https://fdp.example.com", "user@example.com", "pass")

    with pytest.raises(requests.HTTPError):
        fdp_client.post_serialized("dataset", empty_dataset_graph)


def test_fdp_login(requests_mock):
    requests_mock.post("https://fdp.example.com/tokens", json={"token": "1234abcd"})
    fdp_client = FDPClient("https://fdp.example.com", "user@example.com", "pass")

    assert requests_mock.call_count == 1
    assert requests_mock.last_request.json() == {
        "email": "user@example.com",
        "password": "pass",
    }
    assert fdp_client.get_headers() == {
        "Authorization": "Bearer 1234abcd",
        "Content-Type": "text/turtle",
    }


def test_fdp_login_trailing_slash(requests_mock):
    requests_mock.post("https://fdp.example.com/tokens", json={"token": "1234abcd"})
    fdp_client = FDPClient("https://fdp.example.com/", "user@example.com", "pass")

    assert requests_mock.call_count == 1
    assert requests_mock.last_request.json() == {
        "email": "user@example.com",
        "password": "pass",
    }
    assert fdp_client.get_headers() == {
        "Authorization": "Bearer 1234abcd",
        "Content-Type": "text/turtle",
    }


def test_fdp_login_error(requests_mock):
    requests_mock.post("http://fdp.example.com/tokens", status_code=403)

    with pytest.raises(requests.HTTPError):
        FDPClient("http://fdp.example.com", "wrong_email", "wrong_password")


def test_fdp_publish(requests_mock, fdp_client_mock: FDPClient):
    fdp_client_mock.publish_record("https://fdp.example.com/dataset/12345678")

    assert requests_mock.call_count == 2
    assert requests_mock.last_request.url == "https://fdp.example.com/dataset/12345678/meta/state"
    assert requests_mock.last_request.json() == {"current": "PUBLISHED"}


@pytest.mark.parametrize("metadata_type", ["dataset", "catalog", "distribution"])
def test_fdp_post_serialised(
    requests_mock,
    fdp_client_mock: FDPClient,
    metadata_type,
):
    requests_mock.post(f"https://fdp.example.com/{metadata_type}", text="")

    metadata = MagicMock(spec=Graph)
    metadata.serialize.return_value = ""
    # Ensure it's valid? Enforce lowercase?
    fdp_client_mock.post_serialized(metadata_type, metadata)

    assert requests_mock.last_request.url == f"https://fdp.example.com/{metadata_type}"
    assert requests_mock.last_request.headers["Content-Type"] == "text/turtle"
    assert requests_mock.last_request.headers["Authorization"] == "Bearer 1234abcd"
    assert requests_mock.last_request.method == "POST"
    metadata.serialize.assert_called_once_with(format="turtle")


def test_fdp_update_serialised(requests_mock, fdp_client_mock: FDPClient):
    requests_mock.put("http://fdp.example.com/dataset/test", text="")

    metadata = MagicMock(spec=Graph)
    metadata.serialize.return_value = ""
    # Ensure it's valid? Enforce lowercase?
    fdp_client_mock.update_serialized("http://fdp.example.com/dataset/test", metadata)

    assert requests_mock.last_request.url == "http://fdp.example.com/dataset/test"
    assert requests_mock.last_request.headers["Content-Type"] == "text/turtle"
    assert requests_mock.last_request.headers["Authorization"] == "Bearer 1234abcd"
    assert requests_mock.last_request.method == "PUT"
    metadata.serialize.assert_called_once_with(format="turtle")


def test_fdp_delete_dataset(requests_mock, fdp_client_mock: FDPClient):
    # Ensure it's valid? Enforce lowercase?
    response = fdp_client_mock.delete_record("dataset/12345678")

    assert requests_mock.last_request.url == "https://fdp.example.com/dataset/12345678"
    assert requests_mock.last_request.method == "DELETE"
    assert response.status_code == 204


def test_fdp_get_dataset(requests_mock, fdp_client_mock: FDPClient):
    # Ensure it's valid? Enforce lowercase?
    response = fdp_client_mock.get_data("dataset/12345678")

    assert requests_mock.last_request.url == "https://fdp.example.com/dataset/12345678"
    assert requests_mock.last_request.method == "GET"
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "text/turtle"


# @pytest.mark.repeat(1)
# @patch("img2catalog.fdpclient.FDPClient.post_serialized")
# @patch("img2catalog.fdpclient.FDPClient.publish_record")
# publish_record, post_serialized, requests_mock
def test_fdp_create_and_publish(requests_mock, fdp_client_mock):
    empty_graph = Graph()

    assert fdp_client_mock.create_and_publish("dataset", empty_graph) == URIRef(
        "https://fdp.example.com/dataset/12345678"
    )
    # Test if dataset is pushed correctly
    assert requests_mock.request_history[-2].url == "https://fdp.example.com/dataset"
    assert requests_mock.request_history[-2].headers["Content-Type"] == "text/turtle"
    assert requests_mock.request_history[-2].method == "POST"

    # Test if dataset is actually published
    assert requests_mock.last_request.url == "https://fdp.example.com/dataset/12345678/meta/state"
    assert requests_mock.last_request.headers["Content-Type"] == "application/json"
    assert requests_mock.last_request.method == "PUT"
    assert requests_mock.last_request.json() == {"current": "PUBLISHED"}


def test_fdp_node_removal():
    reference_graph = Graph().parse("tests/references/empty_xnat.ttl")

    graph_to_modify = Graph().parse("tests/references/minimal_catalog_dataset.ttl")
    remove_node_from_graph(URIRef("https://example.com/dataset"), graph_to_modify)

    assert to_isomorphic(reference_graph) == to_isomorphic(graph_to_modify)
