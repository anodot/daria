import pytest

from . import cacti


@pytest.mark.parametrize(
    "title, graph, host, er",
    [(
        "|query_descr|-|host_desc|",
        {
            "variables": {"descr": " graph. name "}
        },
        {"desc": " host name. "},
        {"query_descr": "graph__name", "host_desc": "host_name_"},
    )]
)
def test_extract_title_dimensions(title: str, graph: dict, host: dict, er: dict):
    assert cacti._extract_title_dimensions(title, graph, host) == er
