import pytest
from pathlib import Path
import pyshacl
from rdflib import Graph

def validate_rdf(data_file: Path) -> tuple[bool, str]:
    """Validate an RDF file against the SHACL shapes."""
    # Load the data graph
    data_graph = Graph()
    data_graph.parse(data_file)

    # Load the SHACL shapes graph
    shapes_file = Path(__file__).parent.parent / "shacl" / "ldto-core.ttl"
    shapes_graph = Graph()
    shapes_graph.parse(shapes_file)

    # Perform the validation
    validation_result = pyshacl.validate(
        data_graph,
        shacl_graph=shapes_graph,
        inference='rdfs',
        abort_on_first=False,
        meta_shacl=False,
        debug=False
    )
    
    conforms, _, results_text = validation_result
    return conforms, results_text

def test_valid_examples():
    """Test that all examples validate correctly."""
    examples_dir = Path(__file__).parent.parent / "examples"
    for example_file in examples_dir.glob("*.ttl"):
        conforms, results = validate_rdf(example_file)
        assert conforms, f"Validation failed for {example_file.name}:\n{results}"

def test_invalid_files():
    """Test that all files in the invalid directory fail validation."""
    invalid_dir = Path(__file__).parent / "invalid"
    for invalid_file in invalid_dir.glob("*.ttl"):
        conforms, results = validate_rdf(invalid_file)
        assert not conforms, f"Expected validation to fail for {invalid_file.name}, but it passed"
