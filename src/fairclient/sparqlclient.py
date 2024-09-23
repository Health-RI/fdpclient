# SPDX-FileCopyrightText: 2024 Stichting Health-RI
#
# SPDX-License-Identifier: MIT

import logging

from SPARQLWrapper import JSON, SPARQLWrapper

logger = logging.getLogger(__name__)


class FDPSPARQLClient:
    """Simple SPARQL client to query a SPARQL endpoint of (reference) FAIR Data Point."""

    def __init__(self, endpoint: str):
        self.endpoint = endpoint

        self.sparql = SPARQLWrapper(endpoint)
        self.sparql.setReturnFormat(JSON)

    def find_subject(self, identifier, catalog):
        query = f"""PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT *
WHERE {{
    ?subject dcterms:identifier "{identifier}" .
    ?subject dcterms:isPartOf <{catalog}> .
}}"""
        self.sparql.setQuery(query)
        results = self.sparql.queryAndConvert()["results"]["bindings"]

        if len(results) == 0:
            # No result found
            return None
        if len(results) > 1:
            msg = "More than one result for SPARQL query"
            raise ValueError(msg)

        if results[0]["subject"]["type"].casefold() != "uri":
            msg = "Incorrect result type for subject in FDP"
            raise TypeError(msg)

        return results[0]["subject"]["value"]
