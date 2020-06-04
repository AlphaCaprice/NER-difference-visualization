from functools import lru_cache

import pandas as pd

from utils.file_handlers import json_load
from utils.html_template import HTML, SCRIPT, STYLE


@lru_cache(maxsize=64)
def load_displacy_options(colors_path: str) -> dict:
    """Set entities colors for displacy.render function

    Args:
        colors_path: path to json

    Returns:
        displacy options
    """
    colors_info = json_load(colors_path)

    # Create correct arguments for displacy
    colors = {str(k["label"]): k["color"] for k in colors_info}
    labels = list(colors.keys())
    return {"ents": labels, "colors": colors}


def create_table_view(csv_path: str, html_path: str) -> None:
    """Create table view of csv file using pandas to_html method.
    After creating, html table is wrapped in custom html template for pretty view.

    Args:
        csv_path: csv input file
        html_path: html output file

    """
    csv_ = pd.read_csv(csv_path)

    html_table = csv_.to_html(
        classes=["table-bordered"],
        justify="center",
        table_id="custom_table",
        escape=False,
    )

    with open(html_path, "w") as file:
        html = HTML.format(table=html_table, script=SCRIPT, style=STYLE)
        file.write(html)
