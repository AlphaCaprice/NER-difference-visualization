import csv
import json

from typing import Iterable, Union, List, Dict


def csv_write_row(filename: str, row: Iterable, mode="a+") -> None:
    """Writes one row in CSV file.

    Args:
        mode: in which mode to write
        filename: path to file
        row: data to write

    """
    with open(filename, mode, newline="") as file:
        writer = csv.writer(file, delimiter=',', quotechar='"',
                            quoting=csv.QUOTE_MINIMAL)
        writer.writerow(row)


def csv_write_rows(filename: str, rows: Iterable[Iterable], mode="a+") -> None:
    """Writes multiple rows in CSV file.

    Args:
        mode: in which mode to write
        filename: path to file
        rows: data to write

    """
    with open(filename, mode, newline="") as file:
        writer = csv.writer(file, delimiter=',', quotechar='"',
                            quoting=csv.QUOTE_MINIMAL)
        writer.writerows(rows)


def json_load(filename: str) -> Union[List, Dict]:
    """Load json data from file"""
    with open(filename, "r") as file:
        data = json.load(file)
    return data


def json_write(filename: str, data) -> None:
    """Write json data to file"""
    with open(filename, "w") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def json_append(filename: str, new_data: list) -> None:
    """Write json data to file"""
    with open(filename, "r+") as file:
        existed_data = json.load(file)
        existed_data.extend(new_data)
        file.seek(0)
        json.dump(existed_data, file, indent=4, ensure_ascii=False)


def clear_file(filename: str) -> None:
    """Clear file information"""
    open(filename, "w").close()
