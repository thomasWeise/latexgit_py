"""Test the interaction with the file system and temp files."""

from typing import Final

from pycommons.io.path import Path, write_lines
from pycommons.io.temp import temp_dir, temp_file

from latexgit.aux import (
    REQUEST_FILE,
    RESPONSE_PATH,
    run,
)


def test_aux() -> None:
    """Test the aux processor."""
    mrepo: Final[str] = \
        "https://github.com/thomasWeise/programmingWithPythonCode"
    with (temp_dir() as td,
          temp_file(td, suffix=".aux") as tf):
        txt = [
            r"\relax",
            f"{REQUEST_FILE} {{{mrepo}}}{{05_functions/def_factorial.py}}{{"
            f"python3 -m latexgit.formatters.python --args format}}",
            r"\gdef \@abspage@last{1}"]
        with tf.open_for_write() as wd:
            write_lines(txt, wd)

        run(tf)
        got_1 = list(tf.open_for_read())

        assert len(got_1) == (len(txt) + 2)
        res_cmd: str = f"\\xdef{RESPONSE_PATH}"
        res_files: list[str] = [s for s in got_1 if s.startswith(res_cmd)]
        assert len(res_files) == 1
        res_file: str = res_files[0]
        res_cmd = f"{res_cmd}a{{"
        i1: int = res_file.index(res_cmd) + len(res_cmd)
        res_path: Path = td.resolve_inside(
            res_file[i1:res_file.index("}", i1)])

        processed_file = res_path.read_all_str()
        assert "\n\n\n" in processed_file
