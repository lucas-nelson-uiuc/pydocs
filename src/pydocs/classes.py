import pathlib
import re
from typing import Callable
from typing import Sequence

from attrs import define
from attrs import field
from pydocs.parser import parse
from pydocs.parser import summarize


@define
class Log:
    source: str | pathlib.Path
    pattern: str | re.Pattern = field(default=r".*")
    cast: Callable | dict | None = field(default=None)

    @pattern.validator
    def is_compiled_pattern(self, attribute, value):
        try:
            re.compile(value)
        except Exception as e:
            raise e

    def _parse(self) -> Sequence[dict]:
        return parse(file=self.source, pattern=self.pattern, cast=self.cast)

    def _summarize(self) -> dict:
        contents = self._parse()
        return summarize(contents)

    def _validate(self, *validators: Callable) -> None:
        contents = self._parse()
        for validator in validators:
            assert validator(contents)


@define
class TidyLog(Log):
    """Base logging class tidy objects."""

    pattern: str = r"(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+\|\s+(?P<level>[A-Z]+)\s+\|\s+#>\s(?P<content>(?P<operation>[a-z]+):\s(?P<message>.*))"
    cast: Callable = ...
