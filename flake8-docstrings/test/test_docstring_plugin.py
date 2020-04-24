import pytest
import ast
from pathlib import Path
from flake8_docstrings import DocstringsChecker


def _get_file_content(filename: str) -> str:
    with open(filename, 'r') as f:
        file_content = f.read()
    return file_content


def _run_inspection(filename: str):
    file = Path(__file__).absolute().parent / 'cases' / filename
    inspector = DocstringsChecker(
        filename=str(file),
        tree=ast.parse(_get_file_content(file))
    )
    return list(inspector.run())


@pytest.mark.parametrize(
    "filename, errors",
    [
        (
            'docstring_exist.py',
            [
                (
                    1, 0,
                    'D101/D102/D103 Missing docstring '
                    'in public class/method/function.',
                    DocstringsChecker
                ),
                (
                    2, 4,
                    'D101/D102/D103 Missing docstring '
                    'in public class/method/function.',
                    DocstringsChecker
                )
            ]
        ),
        (
            'quotes.py',
            [
                (
                    4, 4,
                    'D300 Use triple single quotes.',
                    DocstringsChecker
                ),
                (
                    4, 4,
                    'D209 Multi-line docstring closing quotes'
                    ' should be on a separate line.',
                    DocstringsChecker
                )
            ]
        ),
        (
            'first_line.py',
            [
                (
                    4, 4,
                    'D400 First line should end with a period.',
                    DocstringsChecker
                ),
                (
                    13, 4,
                    'D212 Docstring summary should start at '
                    'the first line with a capital letter.',
                    DocstringsChecker
                )
            ]
        ),
        (
            'blank_line.py',
            [
                (
                    4, 4,
                    'D205 1 blank (maybe you should remove whitespaces) line '
                    'required between summary line and description.',
                    DocstringsChecker
                )
            ]
        ),
        (
            'args.py',
            [
                (
                    4, 4,
                    'D405 Args: should be implemented, '
                    'during function have arguments.',
                    DocstringsChecker
                ),
                (
                    8, 10,
                    'D406 Argument wasn`t implemented in args list.',
                    DocstringsChecker
                )
            ]
        ),
        (
            'returns.py',
            [
                (
                    4, 4,
                    'D407 "Returns:" should be implemented, '
                    'during function returns something.',
                    DocstringsChecker
                ),
                (
                    26, 4,
                    'D407 "Returns:" should be implemented, '
                    'during function returns something.',
                    DocstringsChecker
                )
            ]
        ),
        (
            'operator.py',
            [
                (
                    13, 4,
                    'D410 Operator -> should be implemented',
                    DocstringsChecker
                )
            ]
        ),
        (
            'annotation.py',
            [
                (
                    4, 4,
                    'D411 Arguments must be annotated',
                    DocstringsChecker
                ),
                (
                    13, 10,
                    'D411 Arguments must be annotated',
                    DocstringsChecker
                )
            ]
        )
    ]
)
def test_run_inspections(filename, errors):
    assert _run_inspection(filename) == errors
