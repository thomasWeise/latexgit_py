"""Some utility methods for string processing."""
import datetime
import re
import string
from typing import (
    Callable,
    Iterable,
    Pattern,
)
from urllib.parse import urlparse

from latexgit.utils.types import type_error


def str_to_lines(text: str) -> list[str]:
    r"""
    Convert a string to an iterable of lines.

    :param text: the original text string
    :return: the lines

    >>> str_to_lines("\n123\n  456\n789 \n 10\n\n")
    ['', '123', '  456', '789 ', ' 10', '', '']
    """
    if not isinstance(text, str):
        raise type_error(text, "text", str)
    return text.split("\n")


def lines_to_str(lines: Iterable[str],
                 trailing_newline: bool = True) -> str:
    r"""
    Convert an iterable of strings to a single string.

    :param lines: the lines
    :param trailing_newline: should the re be a newline at the end?
    :return: the single string

    >>> lines_to_str(["a", "b", "", "c", ""], trailing_newline=True)
    'a\nb\n\nc\n'
    >>> lines_to_str(["a", "b", "", "c"], trailing_newline=True)
    'a\nb\n\nc\n'
    >>> lines_to_str(["a", "b", "", "c"], trailing_newline=False)
    'a\nb\n\nc'
    >>> lines_to_str(["a", "b", "", "c", ""], trailing_newline=False)
    'a\nb\n\nc'
    """
    if not isinstance(lines, Iterable):
        raise type_error(lines, "lines", Iterable)

    res = "\n".join(lines).rstrip()
    if trailing_newline:
        return res + "\n"
    return res


def enforce_non_empty_str(text: str) -> str:
    """
    Enforce that a text is a non-empty string.

    :param text: the text
    :returns: the text
    :raises TypeError: if `text` is not a `str`
    :raises ValueError: if `text` is empty
    """
    if not isinstance(text, str):
        raise type_error(text, "text", str)
    if len(text) <= 0:
        raise ValueError(f"Non-empty str expected, but got {text!r}.")
    return text


def enforce_non_empty_str_without_ws(text: str) -> str:
    """
    Enforce that a text is a non-empty string without white space.

    :param text: the text
    :returns: the text
    :raises TypeError: if `text` is not a `str`
    :raises ValueError: if `text` is empty or contains any white space
        characters
    """
    text = enforce_non_empty_str(text)
    if any(c in text for c in string.whitespace):
        raise ValueError(
            f"No white space allowed in string, but got {text!r}.")
    return text


def datetime_to_date_str(date: datetime.datetime) -> str:
    """
    Convert a datetime object to a date string.

    :param date: the date
    :return: the date string
    """
    if not isinstance(date, datetime.datetime):
        raise type_error(date, "date", datetime.datetime)
    return date.strftime("%Y\u2011%m\u2011%d")


def datetime_to_datetime_str(date: datetime.datetime) -> str:
    """
    Convert a datetime object to a date-time string.

    :param date: the date
    :return: the date-time string
    """
    if not isinstance(date, datetime.datetime):
        raise type_error(date, "date", datetime.datetime)
    return date.strftime("%Y\u2011%m\u2011%d\u00a0%H:%M\u00a0%Z")


def enforce_url(url: str) -> str:
    """
    Enforce that a string is a valid url.

    :param url: the url
    :return: the url
    """
    enforce_non_empty_str_without_ws(url)
    if ".." in url:
        raise ValueError(f"Invalid url {url!r}, contains '..'.")
    res = urlparse(url)
    if res.scheme != "ssh":
        if res.scheme not in ("http", "https"):
            raise ValueError(f"Invalid scheme {res.scheme!r} in url {url!r}.")
        if "@" in url:
            raise ValueError(
                f"Non-ssh URL must not contain '@', but {url!r} does")
    enforce_non_empty_str_without_ws(res.netloc)
    enforce_non_empty_str_without_ws(res.path)
    return res.geturl()


def get_prefix_str(str_list: tuple[str, ...] | list[str]) -> str:
    r"""
    Compute the common prefix string.

    :param str_list: the list of strings
    :return: the common prefix

    >>> get_prefix_str(["abc", "acd"])
    'a'
    >>> get_prefix_str(["xyz", "gsdf"])
    ''
    >>> get_prefix_str([])
    ''
    >>> get_prefix_str(["abx"])
    'abx'
    >>> get_prefix_str(("\\relative.path", "\\relative.figure",
    ...     "\\relative.code"))
    '\\relative.'
    """
    if len(str_list) <= 0:
        return ""
    prefix_str = ""
    len_smallest_str = min([len(str_mem) for str_mem in str_list])
    str_list_0 = str_list[0]
    for i in range(len_smallest_str):
        f = str_list_0[i]
        if len([0 for ind in range(1, len(str_list))
                if f != str_list[ind][i]]) > 0:
            break
        prefix_str += f
    return prefix_str


def regex_sub(search: str | Pattern,
              replace: Callable | str,
              inside: str) -> str:
    r"""
    Replace all occurrences of 'search' in 'inside' with 'replace'.

    :param search: the regular expression to search
    :param replace: the regular expression to replace it with
    :param inside: the string in which to search/replace
    :return: the new string after the recursive replacement

    >>> regex_sub('[ \t]+\n', '\n', ' bla \nxyz\tabc\t\n')
    ' bla\nxyz\tabc\n'
    >>> regex_sub('[0-9]A', 'X', '23A7AA')
    '2XXA'
    """
    while True:
        text = re.sub(
            search, replace, inside,
            flags=0 if isinstance(search, Pattern) else re.MULTILINE)
        if text is inside:
            return inside
        inside = text


def replace_all(find: str, replace: str, src: str) -> str:
    """
    Perform a recursive replacement of strings.

    After applying this function, there will not be any occurence of `find`
    left in `src`. All of them will have been replaced by `replace`. If that
    produces new instances of `find`, these will be replaced as well.
    If `replace` contains `find`, this will lead to an endless loop!

    :param find: the string to find
    :param replace: the string with which it will be replaced
    :param src: the string in which we search
    :return: the string `src`, with all occurrences of find replaced by replace

    >>> replace_all("a", "b", "abc")
    'bbc'
    >>> replace_all("aa", "a", "aaaaa")
    'a'
    >>> replace_all("aba", "a", "abaababa")
    'aa'
    """
    new_len = len(src)
    while True:
        src = src.replace(find, replace)
        old_len = new_len
        new_len = len(src)
        if new_len >= old_len:
            return src
