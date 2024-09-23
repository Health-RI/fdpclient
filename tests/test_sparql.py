# SPDX-FileCopyrightText: 2024 Stichting Health-RI
#
# SPDX-License-Identifier: MIT

from unittest.mock import MagicMock, patch

import pytest
from rdflib import Graph, URIRef
from rdflib.namespace import DCAT, RDF

from fdpclient.fdpclient import FDPClient
from fdpclient.sparqlclient import FDPSPARQLClient
from fdpclient.utils import add_or_update_dataset


@pytest.fixture
def empty_dataset_graph():
    g = Graph()
    g.add((URIRef("https://example.com/dataset"), RDF.type, DCAT.Dataset))

    return g


# These test cases are not the best. Better would be to emulate the actual endpoint
@patch("SPARQLWrapper.SPARQLWrapper.setQuery")
@patch("SPARQLWrapper.SPARQLWrapper.queryAndConvert")
def test_subject_query_success(queryAndConvert, setQuery):
    expected_decoded_json = {
        "head": {"vars": ["subject"]},
        "results": {
            "bindings": [
                {
                    "subject": {
                        "type": "uri",
                        "value": "http://example.com/dataset",
                    }
                }
            ]
        },
    }
    queryAndConvert.return_value = expected_decoded_json

    expected_query = """PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT *
WHERE {
    ?subject dcterms:identifier "https://example.com/dataset" .
    ?subject dcterms:isPartOf <https://example.com> .
}"""

    t = FDPSPARQLClient("https://example.com")

    assert t.find_subject("https://example.com/dataset", "https://example.com") == "http://example.com/dataset"
    setQuery.assert_called_with(expected_query)


@patch("SPARQLWrapper.SPARQLWrapper.queryAndConvert")
def test_subject_query_empty(queryAndConvert):
    expected_decoded_json = {
        "head": {"vars": ["subject"]},
        "results": {"bindings": []},
    }
    queryAndConvert.return_value = expected_decoded_json

    t = FDPSPARQLClient("https://example.com")

    assert t.find_subject("https://example.com/dataset", "https://example.com") is None


@patch("SPARQLWrapper.SPARQLWrapper.queryAndConvert")
def test_subject_query_multiple(queryAndConvert):
    expected_decoded_json = {
        "head": {"vars": ["subject"]},
        "results": {
            "bindings": [
                {
                    "subject": {
                        "type": "uri",
                        "value": "http://example.com/dataset1",
                    }
                },
                {
                    "subject": {
                        "type": "uri",
                        "value": "http://example.com/dataset2",
                    }
                },
            ]
        },
    }
    queryAndConvert.return_value = expected_decoded_json

    t = FDPSPARQLClient("https://example.com")
    with pytest.raises(expected_exception=ValueError, match="More than one result"):
        t.find_subject("https://example.com/dataset", "https://example.com")


@patch("SPARQLWrapper.SPARQLWrapper.queryAndConvert")
def test_subject_query_typeerror(queryAndConvert):
    expected_decoded_json = {
        "head": {"vars": ["subject"]},
        "results": {
            "bindings": [
                {
                    "subject": {
                        "type": "literal",
                        "value": "incorrect_result",
                    }
                }
            ]
        },
    }
    queryAndConvert.return_value = expected_decoded_json

    t = FDPSPARQLClient("https://example.com")
    with pytest.raises(TypeError):
        t.find_subject("https://example.com/dataset", "https://example.com")


# Not using the above FDP client here, easier to check if the related function calls in the client
# are made. We can assume those calls are correct as they are tested above
def test_dataset_updater_nomatch():
    sparqlclient = MagicMock(spec=FDPSPARQLClient)
    fdpclient = MagicMock(spec=FDPClient)
    metadata = Graph()
    dataset_identifier = "https://example.com/dataset"
    catalog_uri = "https://fdp.example.com/catalog/123"

    # No match found
    sparqlclient.find_subject.return_value = None

    add_or_update_dataset(metadata, fdpclient, dataset_identifier, catalog_uri, sparqlclient)

    sparqlclient.find_subject.assert_called_once_with(dataset_identifier, catalog_uri)
    fdpclient.create_and_publish.assert_called_once_with("dataset", metadata)
    fdpclient.update_serialized.assert_not_called()


def test_dataset_updater_match(empty_dataset_graph):
    sparqlclient = MagicMock(spec=FDPSPARQLClient)
    fdpclient = MagicMock(spec=FDPClient)
    metadata = empty_dataset_graph
    dataset_identifier = "https://example.com/dataset"
    catalog_uri = "https://fdp.example.com/catalog/123"

    subject_uri = "https://fdp.example.com/dataset/456"
    sparqlclient.find_subject.return_value = subject_uri

    add_or_update_dataset(metadata, fdpclient, dataset_identifier, catalog_uri, sparqlclient)

    sparqlclient.find_subject.assert_called_once_with(dataset_identifier, catalog_uri)
    fdpclient.create_and_publish.assert_not_called()
    fdpclient.update_serialized.assert_called_once_with(subject_uri, metadata)


def test_dataset_updater_invalid(empty_dataset_graph):
    sparqlclient = MagicMock(spec=FDPSPARQLClient)
    fdpclient = MagicMock(spec=FDPClient)
    metadata = empty_dataset_graph
    dataset_identifier = None
    catalog_uri = "https://fdp.example.com/catalog/123"

    add_or_update_dataset(metadata, fdpclient, dataset_identifier, catalog_uri, sparqlclient)

    fdpclient.create_and_publish.assert_called_once_with("dataset", metadata)
    sparqlclient.find_subject.assert_not_called()
    fdpclient.update_serialized.assert_not_called()
