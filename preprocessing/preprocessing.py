from typing import List

from preprocessing.load_functions import choose_load_function


ALLOWED_EXTENSIONS = {"txt", "pdf", "docx", "doc", "html", "xml", "htm", "xht"}


def preprocess_file(file_path: str) -> List[List]:
    ext = file_path.rsplit(".", 1)[1]
    if ext not in ALLOWED_EXTENSIONS:
        raise NameError

    # Preprocessed text
    load_function = choose_load_function(ext)
    list_of_pages = load_function(file_path)

    return list_of_pages
