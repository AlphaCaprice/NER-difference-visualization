import argparse
import configparser
from pathlib import Path

from spacy import displacy
from tqdm import tqdm

from machine_tagging.machine_tagging import find_entities
from model.model import FlairNER
from preprocessing.preprocessing import preprocess_file
from utils.file_handlers import (
    clear_file,
    csv_write_row,
    csv_write_rows,
    json_append,
    json_load,
    json_write,
)
from utils.metrics import collect_metrics, MetricRecord
from utils.utils import create_table_view, load_displacy_options

parser = argparse.ArgumentParser()
parser.add_argument(
    "language", help="two-letter abbreviation of language name (en, fr, zh)."
)
parser.add_argument("-m", "--model", dest="model", help="Name of model to use")
parser.add_argument("-d", "--dest", dest="dest", help="Where to save data")

group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("--file", dest="file", help="path to file for processing")
group.add_argument("--folder", dest="folder",
                   help="path to folder with valid files for processing")
group.add_argument("--link", dest="link", help="url to file in the Internet")
group.add_argument("--links", dest="links",
                   help="path to txt file that contains links to html files in "
                        "the Internet; links must be split by new line.")

if __name__ == "__main__":
    args = parser.parse_args()
    language = args.language
    if args.folder:
        data = list(Path(args.folder).glob("?*.*"))
    elif args.file:
        data = [args.file]
    elif args.link:
        data = [args.link]
    elif args.links:
        data = Path(args.links).read_text().split("\n")
    else:
        # this will never reach because  parser raise exception earlier
        raise KeyError("No data was specified")

    config = configparser.ConfigParser()
    config.read("settings.ini")

    colors_path = config["paths"]["colors"]
    entities_path = config["paths"][f"{language}_entities"]
    model_path = args.model or config["paths"][f"{language}_model"]

    # output paths
    output_dir_base = args.dest or config["paths"]["output"]

    # load model
    model = FlairNER(model=model_path, lang=language, max_length=None)

    Path(output_dir_base).mkdir(exist_ok=True)

    for file in tqdm(data, desc="Files"):
        filename = file.rsplit("/", 1)[-1] if not isinstance(file, Path) else file.stem

        output_dir = Path(output_dir_base, filename)
        if output_dir.exists():
            tqdm.write(f"Folder {output_dir} already exist. Skipped.")
            continue

        try:
            document_pages = preprocess_file(str(file))
        except NameError as e:
            tqdm.write(f"{e} Skipped.")
            continue

        output_dir.mkdir()

        csv_output = Path(output_dir, f"{filename}.csv")
        model_predictions_output = Path(output_dir, "model_predictions.json")
        machine_predictions_output = Path(output_dir, "rule_based_predictions.json")
        html_output = Path(output_dir, f"{filename}.html")

        displacy_options = load_displacy_options(colors_path)

        model_tagged = []
        machine_tagged = []
        table_rows = []

        entities = json_load(entities_path)

        for i, page in enumerate(tqdm(document_pages, desc="Pages", leave=False)):
            for paragraph in tqdm(page, desc="Paragraphs", leave=False):
                if not paragraph:
                    continue

                machine_record = find_entities(paragraph, entities)
                model_record = model.predict_paragraph(paragraph)

                machine_tagged.append(machine_record)
                model_tagged.append(model_record)

                if len(machine_record["ents"]) + len(model_record["ents"]) == 0:
                    continue
                metric_record = collect_metrics(machine_record, model_record)

                if metric_record.model_fn_amount + metric_record.model_fp_amount > 0:
                    displacy_text = displacy.render(
                        model_record, style="ent", manual=True, options=displacy_options
                    )
                    displacy_text = displacy_text.replace("\n", "")
                    table_rows.append(metric_record._replace(text=displacy_text))

        # write names of columns and data in csv file
        clear_file(csv_output)
        csv_write_row(
            csv_output, [field.replace("_", " ") for field in MetricRecord._fields]
        )
        csv_write_rows(csv_output, table_rows)

        # create empty json files
        json_write(model_predictions_output, [])
        json_write(machine_predictions_output, [])

        # write predictions from machine tagging and model
        json_append(model_predictions_output, model_tagged)
        json_append(machine_predictions_output, machine_tagged)

        create_table_view(csv_output, html_output)
