import pytest

from docext.core.errors import ExtractionValidationError
from docext.extraction.json_repair import parse_json_output


@pytest.mark.parametrize(
    "text",
    [
        '{"a": 1}',
        '```json\n{"a": 1}\n```',
        'Here is the result:\n{"a": 1}\nThanks!',
    ],
)
def test_parse_json_output_tolerates_fences_and_prose(text: str) -> None:
    assert parse_json_output(text) == {"a": 1}


def test_parse_json_output_rejects_non_object() -> None:
    with pytest.raises(ExtractionValidationError):
        parse_json_output("[1, 2]")
