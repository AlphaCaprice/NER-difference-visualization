import argparse
import configparser
import os
from spacy import displacy
from tqdm import tqdm

from machine_tagging.machine_tagging import find_entities
from model.model import FlairNER
from preprocessing.preprocessing import preprocess_file
from utils.file_handlers import (clear_file, csv_write_row, csv_write_rows,
                                 json_append, json_write)
from utils.metrics import MetricRecord, collect_metrics
from utils.utils import load_displacy_options, create_table_view

parser = argparse.ArgumentParser()
parser.add_argument("language",
                    help="Two-letter abbreviation of language name (en, fr, zh).")
parser.add_argument("file", help="Path to file for processing")
parser.add_argument("-m", "--model", dest="model", help="Name of model to use")
parser.add_argument("-d", "--destination", dest="dest", help="Where to save data")


if __name__ == '__main__':
    args = parser.parse_args()
    language = args.language
    file_path = args.file

    config = configparser.ConfigParser()
    config.read("settings.ini")

    colors_path = config["paths"]["colors"]
    model_path = args.model or config["paths"][f"{language}_model"]

    # output paths
    output_dir = args.dest or config["paths"]["output"]

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    csv_output = os.path.join(output_dir, "stat.csv")
    model_predictions_output = os.path.join(output_dir, "model_predictions.json")
    machine_predictions_output = os.path.join(output_dir, "machine_predictions.json")
    html_output = os.path.join(output_dir, "stat.html")

    displacy_options = load_displacy_options(colors_path)

    model = FlairNER(model=model_path, lang=language, max_length=None)

    model_tagged = []
    machine_tagged = []
    table_rows = []

    document_pages = preprocess_file(file_path)

    for i, page in enumerate(tqdm(document_pages, desc="Pages")):
        for paragraph in tqdm(page, desc="Paragraphs", leave=False):
            if not paragraph:
                continue

            machine_record = find_entities(paragraph)
            model_record = model.predict_paragraph(paragraph)

            machine_tagged.append(machine_record)
            model_tagged.append(model_record)

            if len(machine_record["ents"]) + len(model_record["ents"]) == 0:
                continue
            metric_record = collect_metrics(machine_record, model_record)

            if metric_record.model_fn_amount + metric_record.model_fp_amount > 0:
                displacy_text = displacy.render(model_record, style="ent", manual=True,
                                                options=displacy_options)
                displacy_text = displacy_text.replace("\n", "")
                table_rows.append(metric_record._replace(text=displacy_text))

    # write names of columns and data in csv file
    clear_file(csv_output)
    csv_write_row(csv_output,
                  [field.replace("_", " ") for field in MetricRecord._fields])
    csv_write_rows(csv_output, table_rows)

    # create empty json files
    json_write(model_predictions_output, [])
    json_write(machine_predictions_output, [])

    # write predictions from machine tagging and model
    json_append(model_predictions_output, model_tagged)
    json_append(machine_predictions_output, machine_tagged)

    create_table_view(csv_output, html_output)
