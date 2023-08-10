from typing import Union, Optional, Any
import io
import uuid
import pandas as pd
from pathlib import Path
import re

from ._util import _ProData


def read_pro(
    filename: Union[str, Path], header_regex: Optional[str] = None, **csv_kwargs: Any
) -> pd.DataFrame:
    """
    Reads a file as binary, uses get_bytes_skip_rows_regex_match to filter out
    unnecessary lines. Then reads the file into a pandas DataFrame, using explicit
    types for the columns based on the "VARIABLE_TYPES" line.
    """
    pdat = _ProData.from_bytes(Path(filename).read_bytes(), header_regex)

    do_kwarg_dtype = True
    if not "dtype" in csv_kwargs:
        do_kwarg_dtype = False
        if pdat.to_type is not None:
            csv_kwargs["dtype"] = pdat.to_type

    if "encoding" in csv_kwargs:
        df = pd.read_csv(io.BytesIO(pdat.data), **csv_kwargs)
    else:
        try:
            df = pd.read_csv(io.BytesIO(pdat.data), encoding="utf-8", **csv_kwargs)
        except UnicodeDecodeError:
            df = pd.read_csv(io.BytesIO(pdat.data), encoding="latin1", **csv_kwargs)

    if not do_kwarg_dtype:
        if pdat.to_dt_template:
            for col_name, template in pdat.to_dt_template.items():
                df[col_name] = pd.to_datetime(df[col_name], format=template)

    # If the first column contains only "*", drop it (this is part of the pro file format)
    if df.iloc[:, 0].unique() == ["*"]:
        df = df.iloc[:, 1:]

    # Ignore the type since read_csv can return a generator
    return df.copy()  # type: ignore


def to_pro(df: pd.DataFrame, filename: Union[str, Path], **csv_kwargs: Any) -> None:
    # random UUID for * replacement
    uuid_value = f"{uuid.uuid4()}"

    # Insert the UUID value at the 0th index of the DataFrame
    df = df.copy()
    df.insert(0, "!", uuid_value)

    # Convert the DataFrame to CSV format, with headers and body separate
    header_csv = df.head(0).to_csv(index=False)

    csv_kwargs.pop("quoting", None)
    csv_kwargs.pop("index", None)
    body_csv = df.to_csv(header=False, index=False, quoting=2)

    # Write the CSV content to the specified file
    with open(filename, "wb") as f:
        f.write(header_csv.encode("latin1"))
        f.write(re.sub(f'"{uuid_value}"', "*", body_csv).encode("latin1"))
