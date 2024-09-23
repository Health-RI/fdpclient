# SPDX-FileCopyrightText: 2024 Stichting Health-RI
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from rdflib import DCAT, RDF, Graph, URIRef
from rdflib.term import Node

if TYPE_CHECKING:
    from fdpclient.fdpclient import FDPClient
    from fdpclient.sparqlclient import FDPSPARQLClient

logger = logging.getLogger(__name__)


def rewrite_graph_subject(
    g: Graph,
    oldsubject: str | URIRef | Node | None,
    newsubject: str | URIRef | Node | None,
):
    """Modifies a graph such that all elements of the oldsubject are replaced by newsubject

    Needed by the FDP update functionality to work around some ill-defined behavior

    Parameters
    ----------
    g : Graph
        Reference graph in which the subject will be replaced, in-place
    oldsubject : str, URIRef
        The old subject which is to be replaced
    newsubject : str, URIRef
        New subject which will replace the old subject
    """
    for s, p, o in g.triples((URIRef(oldsubject), None, None)):
        g.add((URIRef(newsubject), p, o))
        g.remove((s, p, o))


def add_or_update_dataset(
    metadata: Graph,
    fdpclient: FDPClient,
    dataset_identifier: str | None = None,
    catalog_uri: str | None = None,
    sparql: FDPSPARQLClient = None,
):
    """Either posts or updates a dataset on a FAIR Data Point

    For updating, you will need to provide a dataset identfier, URI of the parent catalog and an
    instance of an FDP-SPARQL client. If any of these are missing, datasets will always be created
    instead of being updated.

    Parameters
    ----------
    metadata : Graph
        The metadata to be published
    fdpclient : FDPClient
        Instance of FDPClient where the dataset will be pushed to
    dataset_identifier : str, optional
        DCAT Identifier of the dataset to match for updating the dataset, by default None
    catalog_uri : str, optional
        URI of the parent catalog to post data to, by default None
    sparql : FDPSPARQLClient, optional
        Instance of FDPSPARQLClient which will be queried for the dataset IRI, by default None
    """
    if sparql and dataset_identifier and catalog_uri:
        if fdp_subject_uri := sparql.find_subject(dataset_identifier, catalog_uri):
            logger.debug("Matched subject to %s", fdp_subject_uri)
            old_subject = metadata.value(
                predicate=RDF.type, object=DCAT.Dataset, any=False
            )
            rewrite_graph_subject(metadata, old_subject, fdp_subject_uri)
            return fdpclient.update_serialized(fdp_subject_uri, metadata)

        logger.debug("No match found")
    else:
        logger.debug(
            "Not all information for potential updating is given, create and publishing."
        )

    return fdpclient.create_and_publish("dataset", metadata)


def remove_node_from_graph(node, graph: Graph):
    """Completely removes a node and all references to it from a graph

    Parameters
    ----------
    node : ...
        Node to be removed
    graph : Graph
        Graph to remove it from
    """
    # Remove all triples with the node as a subject and an object
    graph.remove((node, None, None))
    graph.remove((None, None, node))
