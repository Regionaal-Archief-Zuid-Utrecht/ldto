import pytest
from pathlib import Path
import pyshacl
from rdflib import Graph

def validate_rdf(data_file: Path, shapes_file: Path) -> tuple[bool, str]:
    """Validate an RDF file against SHACL shapes. """
    data_graph = Graph()
    data_graph.parse(data_file)

    shapes_graph = Graph()
    shapes_graph.parse(shapes_file)

    validation_result = pyshacl.validate(
        data_graph,
        shacl_graph=shapes_graph,
        inference='rdfs',
        abort_on_first=False,
        meta_shacl=True if shapes_file.name == "shacl-shacl.ttl" else False,
        debug=False
    )
    
    conforms, _, results_text = validation_result
    return conforms, results_text

def _test_invalid_files(test_dir: str, shapes_type: str = 'core'):
    """Helper function to test invalid files in a directory."""
    invalid_dir = Path(__file__).parent / test_dir / "invalid"
    shapes_file = Path(__file__).parent.parent / "shacl" / f"ldto-{shapes_type}.ttl"
    
    for invalid_file in invalid_dir.glob("*.ttl"):
        conforms, results = validate_rdf(invalid_file, shapes_file)
        assert not conforms, f"Expected validation to fail for {invalid_file.name}, but it passed"

def test_invalid_core_files():
    """Test that all files in the core/invalid directory fail validation."""
    _test_invalid_files("core")

def test_invalid_extension_files():
    """Test that all files in the extensions/invalid directory fail validation."""
    _test_invalid_files("extensions", "extensions")

def test_valid_examples():
    """Test that all examples validate correctly against both core and extensions SHACL."""
    examples_dir = Path(__file__).parent.parent / "examples"
    for example_file in examples_dir.glob("*.ttl"):
        for shapes_type in ['core', 'extensions']:
            shapes_file = Path(__file__).parent.parent / "shacl" / f"ldto-{shapes_type}.ttl"
            conforms, results = validate_rdf(example_file, shapes_file)
            assert conforms, f"{shapes_type.title()} SHACL validation failed for {example_file.name}:\n{results}"

def test_shacl_shapes():
    """Test that all SHACL shapes validate against meta-SHACL."""
    meta_shacl = Path(__file__).parent / "shacl" / "shacl-shacl.ttl"
    shapes_dir = Path(__file__).parent.parent / "shacl"
    
    for shape_file in ['ldto-core.ttl', 'ldto-extensions.ttl']:
        shape_path = shapes_dir / shape_file
        conforms, results_text = validate_rdf(shape_path, meta_shacl)
        assert conforms, f"Meta-SHACL validation failed for {shape_file}:\n{results_text}"
