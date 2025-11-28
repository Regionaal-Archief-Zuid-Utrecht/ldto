import sys
from pathlib import Path

import pytest

# Ensure project root (containing the 'scripts' module) is on sys.path
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.validate import validate_rdf, ALLOWED_EXTENSIONS


TESTS_ROOT = Path(__file__).parent


def iter_test_cases():
    """Yield pytest parameters for all test files.

    Directory layout:
        tests/<shapes_type>/<valid|invalid>/*

    - <shapes_type>  -> name of the SHACL profile (e.g. core, plus, razu)
    - valid/invalid  -> whether the data file is expected to conform
    """
    for shapes_dir in TESTS_ROOT.iterdir():
        if not shapes_dir.is_dir():
            continue

        shapes_type = shapes_dir.name

        for expectation in ("valid", "invalid"):
            data_dir = shapes_dir / expectation
            if not data_dir.is_dir():
                continue

            expected_conforms = expectation == "valid"

            for data_file in data_dir.iterdir():
                if not data_file.is_file():
                    continue
                if not any(str(data_file).endswith(ext) for ext in ALLOWED_EXTENSIONS):
                    continue

                test_id = f"{shapes_type}-{expectation}-{data_file.name}"
                yield pytest.param(data_file, shapes_type, expected_conforms, id=test_id)


@pytest.mark.parametrize("data_file,shapes_type,expected_conforms", list(iter_test_cases()))
def test_files_against_ldto_profiles(data_file: Path, shapes_type: str, expected_conforms: bool):
    """Validate all test files using scripts/validate.py according to directory naming.

    - tests/<shapes_type>/valid/*   -> must conform (validate.py exit code 0)
    - tests/<shapes_type>/invalid/* -> must NOT conform (validate.py exit code != 0)
    """
    status = validate_rdf(str(data_file), shapes_type)

    if expected_conforms:
        assert status == 0, (
            f"Expected validation to succeed for {data_file} with profile '{shapes_type}', "
            f"but validate.py returned status {status}."
        )
    else:
        assert status != 0, (
            f"Expected validation to fail for {data_file} with profile '{shapes_type}', "
            f"but validate.py returned status {status}."
        )


EXAMPLES_DIR = PROJECT_ROOT / "examples"


def test_examples_conform_to_razu_profile():
    """All example files must conform to the 'razu' profile."""
    assert EXAMPLES_DIR.is_dir(), f"Examples directory not found: {EXAMPLES_DIR}"

    for example_file in EXAMPLES_DIR.iterdir():
        if not example_file.is_file():
            continue
        if not any(str(example_file).endswith(ext) for ext in ALLOWED_EXTENSIONS):
            continue

        status = validate_rdf(str(example_file), "razu")
        assert status == 0, (
            f"Expected example {example_file} to conform to 'razu' profile, "
            f"but validate.py returned status {status}."
        )