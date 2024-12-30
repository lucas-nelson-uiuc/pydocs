import datetime
import re
from collections import Counter
from typing import Sequence

from loguru import logger


def parse(*args: tuple, **kwargs: dict) -> Sequence[dict]:
    """
    Parse contents from log file.

    Parameters
    ----------
    *args : tuple
        Positional arguments to pass to `loguru.logger.parse`.
    **kwargs : dict
        Keyword arguments to pass to `loguru.logger.parse`.

    Returns
    -------
    Sequence[dict]
        Collection of parsed lines from log.
    """
    return [line for line in logger.parse(*args, **kwargs)]


def summarize(contents: Sequence[dict]) -> dict:
    """
    Summarize contents of log file.

    Parameters
    ----------
    contents : Sequence[dict]
        Object returned from parsed log file.

    Returns
    -------
    dict
        Statistics describing parsed log file.
    """

    def summarize_runtime(
        start: datetime.datetime, end: datetime.datetime, length: int
    ) -> dict:
        """
        Get statistics for log's runtime.

        Parameters
        ----------
        start : datetime.datetime
            Timestamp of log's initial entry.
        end : datetime.datetime
            Timestamp of log's final entry.
        length : int
            Number of entries in log.

        Returns
        -------
        dict
            Statistics for log's runtime.
        """
        return {
            "total": (end - start).total_seconds(),
            "mean": ((end - start) / length).total_seconds(),
        }

    def summarize_dimensions(enter: str, exit: str) -> str:
        """
        Docstring here.

        Parameters
        ----------
        enter : str
            Entered.
        exit : str
            Exited.

        Returns
        -------
        str
            Something here.
        """

        def get_dimensions(message: str) -> tuple[int]:
            """
            Docstring here.

            Parameters
            ----------
            message : str
                Something.

            Returns
            -------
            tuple[int]
                Something.

            Raises
            ------
            ValueError
                If dimensions cannot be parsed from string.
            """
            pattern = r"\[(?P<rows>[\d\,]+)\srows\sx\s(?P<cols>[\d\,]+)\scols\]"
            dimensions = re.search(pattern, message).groups()
            if not (isinstance(dimensions, tuple) or (len(dimensions) == 2)):
                raise ValueError("Cannot find valid dimensions.")
            return (int(dim.replace(",", "")) for dim in dimensions)

        rows_enter, cols_enter = get_dimensions(enter)
        rows_exit, cols_exit = get_dimensions(exit)
        return {"rows": rows_exit - rows_enter, "cols": cols_exit - cols_enter}

    return {
        "runtime": summarize_runtime(
            start=contents[0].get("timestamp"),
            end=contents[-1].get("timestamp"),
            length=len(contents),
        ),
        "dimensions": summarize_dimensions(
            enter=[c.get("message") for c in contents if c.get("operation") == "enter"][
                0
            ],
            exit=[c.get("message") for c in contents if c.get("operation") == "exit"][
                0
            ],
        ),
        "levels": Counter([line.get("level") for line in contents]),
        "operations": Counter([line.get("operation") for line in contents]),
    }
