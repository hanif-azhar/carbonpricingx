from __future__ import annotations

from io import BytesIO
from typing import Dict

import pandas as pd


def build_excel_report(sheets: Dict[str, pd.DataFrame]) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for sheet_name, df in sheets.items():
            safe_name = str(sheet_name)[:31]
            if isinstance(df, pd.DataFrame):
                df.to_excel(writer, sheet_name=safe_name, index=False)
    return output.getvalue()
