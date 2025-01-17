import pytest
from pathlib import Path
import pyshacl
from rdflib import Graph

def validate_rdf(data_file: Path, shapes_file: Path = None) -> tuple[bool, str]:
    """Validate an RDF file against SHACL shapes.
    
    Args:
        data_file: Path to the RDF file to validate
        shapes_file: Path to the SHACL shapes file. If None, uses ldto-core.ttl
    """
    # Load the data graph
    data_graph = Graph()
    data_graph.parse(data_file)

    # Load the SHACL shapes graph
    if shapes_file is None:
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

def test_shacl_shapes():
    """Test that all SHACL shapes validate against meta-SHACL."""
    shapes_dir = Path(__file__).parent.parent / "shacl"
    meta_shacl = Path(__file__).parent / "shacl" / "shacl-shacl.ttl"
    
    for shape_file in shapes_dir.glob("*.ttl"):
        conforms, results = validate_rdf(shape_file, meta_shacl)
        assert conforms, f"SHACL validation failed for {shape_file.name}:\n{results}"
