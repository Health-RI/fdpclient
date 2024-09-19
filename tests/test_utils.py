# SPDX-FileCopyrightText: 2024 Stichting Health-RI
#
# SPDX-License-Identifier: MIT


from rdflib import Graph
from rdflib.compare import to_isomorphic

from fdpclient.utils import (
    rewrite_graph_subject,
)


def test_subject_replacement():
    old_graph = Graph().parse(source="tests/references/valid_project.ttl")
    reference_graph = Graph().parse(
        source="tests/references/valid_project_subject_replaced.ttl"
    )

    rewrite_graph_subject(
        old_graph,
        "http://localhost/data/archive/projects/test_img2catalog",
        "http://example.com/newsubject",
    )

    # print(new_graph.serialize())
    assert to_isomorphic(reference_graph) == to_isomorphic(old_graph)
