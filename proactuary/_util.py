import io
import re
from typing import Dict, List, Optional, Tuple
import pandas as pd
from dataclasses import dataclass
import re
import random
import shutil
import os


def excel_to_datetime_template(excel_template: str) -> str:
    """
    Converts an Excel date-time format string to a Python strftime format
    string.

    This function provides a basic implementation of Excel's datetime
    formatting conventions, handling common time and date components like
    year ("yyyy", "yy"), month ("mm", "m"), day ("dddd", "ddd", "dd", "d"),
    hours ("hh", "d"), minutes ("mm", "m"), seconds ("ss", "s"), and AM/PM
    markers ("AM/PM").

    Note that the interpretation of "mm"/"m" and "h"/"hh" depends on the
    context; it's similar to the Excel implementation, but not identical:
    - "mm"/"m" are interpreted as minutes if it appears directly after an
    hour format or directly before or after a seconds format; otherwise,
    it's interpreted as months.
    - "hh"/"h" are interpreted in 12-hour format if it's in the same string
    with "AM/PM"; otherwise, it's interpreted in 24-hour format.

    Not all Excel date-time formats are supported, for example, three digit
    years ("yyy").

    Args:
        excel_template (str): An Excel date-time format string.

    Returns:
        str: A Python strftime format string corresponding to the input, with
             certain exceptions.
    """

    normal_subs = {
        "yyyy": "%Y",
        "yy": "%y",
        "mmmm": "%B",
        "mmm": "%b",
        "dddd": "%A",
        "ddd": "%a",
        "dd": "%d",
        "d": "%-d",
        "hh": "%H",
        "h": "%-H",
        "ss": "%S",
        "s": "%-S",
        "am/pm": "%p",
    }

    # Temporary placeholder mappings
    xl_to_ph = {
        k: "{" + "".join(random.choices("0123456789", k=50)) + "}"
        for k in normal_subs.keys()
    }
    ph_to_dt = {k: v for k, v in zip(xl_to_ph.values(), normal_subs.values())}

    # Replace normal templates with placeholders
    for key, placeholder in xl_to_ph.items():
        excel_template = re.sub(key, placeholder, excel_template, flags=re.IGNORECASE)

    m_month_ph = "{" + "".join(random.choices("0123456789abcdef", k=30)) + "}"
    mm_month_ph = "{" + "".join(random.choices("0123456789abcdef", k=30)) + "}"
    m_minute_ph = "{" + "".join(random.choices("0123456789abcdef", k=30)) + "}"
    mm_minute_ph = "{" + "".join(random.choices("0123456789abcdef", k=30)) + "}"
    h_pm_ph = "{" + "".join(random.choices("0123456789abcdef", k=30)) + "}"
    hh_pm_ph = "{" + "".join(random.choices("0123456789abcdef", k=30)) + "}"

    ph_to_dt.update(
        {
            mm_month_ph: "%m",
            m_month_ph: "%-m",
            mm_minute_ph: "%M",
            m_minute_ph: "%-M",
            h_pm_ph: "%-I",
            hh_pm_ph: "%I",
        }
    )

    # Split excel_template into a list of parts, where each part is either a placeholder or a string using regex
    replacement_re = re.compile(f"({'|'.join(map(re.escape, ph_to_dt.keys()))})")
    parts = re.split(replacement_re, excel_template)

    # Right before seconds or right after seconds
    for i, part in enumerate(parts):
        if part == xl_to_ph["ss"] or part == xl_to_ph["s"]:
            if i > 0 and "m" in parts[i - 1]:
                parts[i - 1] = re.sub(
                    "mm", mm_minute_ph, parts[i - 1], flags=re.IGNORECASE
                )
                parts[i - 1] = re.sub(
                    "m", m_minute_ph, parts[i - 1], flags=re.IGNORECASE
                )
            if i < len(parts) - 1 and "m" in parts[i + 1]:
                parts[i + 1] = re.sub(
                    "mm", mm_minute_ph, parts[i + 1], flags=re.IGNORECASE
                )
                parts[i + 1] = re.sub(
                    "m", m_minute_ph, parts[i + 1], flags=re.IGNORECASE
                )

    # Right after hours
    for i, part in enumerate(parts):
        if part == xl_to_ph["h"] or part == xl_to_ph["hh"]:
            if i < len(parts) - 1 and "m" in parts[i + 1]:
                parts[i + 1] = re.sub(
                    "mm", mm_minute_ph, parts[i + 1], flags=re.IGNORECASE
                )
                parts[i + 1] = re.sub(
                    "m", m_minute_ph, parts[i + 1], flags=re.IGNORECASE
                )

    # If AM/PM shows up, then we need to replace h/hh with I/II
    if xl_to_ph["am/pm"] in parts:
        parts = [
            i
            if i not in (xl_to_ph["h"], xl_to_ph["hh"])
            else h_pm_ph
            if i == xl_to_ph["h"]
            else hh_pm_ph
            for i in parts
        ]

    excel_template = "".join(parts)
    excel_template = re.sub("mm", mm_month_ph, excel_template, flags=re.IGNORECASE)
    excel_template = re.sub("m", m_month_ph, excel_template, flags=re.IGNORECASE)

    for placeholder, dt_key in ph_to_dt.items():
        excel_template = excel_template.replace(placeholder, dt_key)

    return excel_template


def _get_header_info_from_bytes(
    preample: List[bytes], header: List[str]
) -> Tuple[Dict[str, str], Dict[str, str]]:
    """
    Given a list of bytes representing the preample of a file and a list of strings representing the header of a file,
    returns two dictionaries. The first dictionary maps the header names to their respective types. The second dictionary
    maps the header names to their respective datetime templates, if they are of type datetime.

    Args:
    - preample: A list of bytes representing the preample of a file.
    - header: A list of strings representing the header of a file.

    Returns:
    - A tuple of two dictionaries. The first dictionary maps the header names to their respective types. The second
    dictionary maps the header names to their respective datetime templates, if they are of type datetime.
    """
    df_types = None
    for line in preample:
        if line.startswith(b"VARIABLE_TYPES"):
            df_types = list(pd.read_csv(io.BytesIO(line), nrows=1).columns)[1:]
            df_types = [re.sub(r"\.\d+", "", i) for i in df_types]
            break

    # Build the dict mapping header names to types
    to_type = {}
    to_dt_template = {}
    if df_types is not None:
        for col, var_type in zip(header, df_types):
            if var_type.startswith("S"):
                to_type[col] = "str"
            elif var_type.startswith("N"):
                to_type[col] = "float"
            elif var_type.startswith("I"):
                to_type[col] = "int"
            elif var_type.startswith("D"):
                # Read as string and then later convert to datetime
                to_type[col] = "str"
                to_dt_template[col] = excel_to_datetime_template(var_type[1:])

    return to_type, to_dt_template


@dataclass
class _ProData:
    header: List[str]
    to_type: Optional[Dict[str, str]]
    to_dt_template: Optional[Dict[str, str]]
    data: bytes

    @classmethod
    def from_bytes(cls, file_bytes: bytes, regex: Optional[str] = None) -> "_ProData":
        """
        Takes a bytes object and a regex. Tries to decode the bytes using utf-8 or
        latin1. Applies the regex to the decoded text line by line. Returns the
        bytes without the lines that don't match the regex. If the regex is None,
        returns the original bytes.
        """
        encoding_to_try = ["utf-8", "latin1"]

        byte_preample_lines = []
        byte_lines = file_bytes.split(b"\n")

        if regex is not None:
            regex_compiled = re.compile(regex)
            for i, line in enumerate(byte_lines):
                decoded_line = None
                err = None

                for encoding in encoding_to_try:
                    try:
                        decoded_line = line.decode(encoding)
                        break
                    except UnicodeDecodeError as e:
                        if err is None:
                            err = e
                        continue

                if decoded_line is None:
                    if err is not None:
                        raise err
                    else:
                        raise ValueError(
                            f"Could not decode line {i} with any of the encodings {encoding_to_try}"
                        )
                elif regex_compiled.findall(decoded_line):
                    byte_preample_lines = byte_lines[:i]
                    byte_lines = byte_lines[i:]
                    break

        header = list(pd.read_csv(io.BytesIO(byte_lines[0]), nrows=1).columns)

        to_type, to_dt_template = _get_header_info_from_bytes(
            byte_preample_lines, header
        )

        # remove end lines if ##END## is in the line:
        for i, line in enumerate(byte_lines):
            if (
                line.replace(b"\r", b"") == b""
                and i < len(byte_lines) - 1
                and byte_lines[i + 1].replace(b"\r", b"").endswith(b"##END##")
            ):
                byte_lines = byte_lines[: i + 1]
                break

        return cls(header, to_type, to_dt_template, b"\n".join(byte_lines))
