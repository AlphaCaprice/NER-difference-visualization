import requests
from typing import List

import tika
from bs4 import BeautifulSoup
from docx import Document
from tika import parser

# tika's java server for parsing PDF files
tika.initVM()


def choose_load_function(ext: str) -> callable:
    ext_to_fun = {
        "txt": load_txt,
        "pdf": load_pdf,
        "docx": load_docx,
        "doc": load_docx,
        "html": load_html,
        "xml": load_html,
        "htm": load_html,
        "xht": load_html,
    }
    return ext_to_fun[ext]


def paginate(list_of_paragraphs: list, max_page_length=5000) -> List[List]:
    """Split list of paragraphs into pages.

    Args:
        list_of_paragraphs: List of paragraphs.
        max_page_length: Approximate length of pages. Maximum number of characters for
            one page.

    Returns:
        List of pages.
    """
    pages = []
    one_page = []
    page_len = 0
    for par in list_of_paragraphs:
        if not par or par == "\t":
            continue
        if page_len >= max_page_length:
            pages.append(one_page)
            one_page = []
            page_len = 0
        one_page.append(par)
        page_len += len(par)
    else:
        pages.append(one_page)
    return pages


def load_txt(file_path: str) -> List[List]:
    """Split text to pages.

    Args:
        file_path: path to file

    Returns:
        list of pages.
    """
    with open(file_path, "r") as f:
        content = f.read()
    return paginate(content.split("\n"))


def load_docx(file_path: str) -> List[List]:
    """Load a docx file and split document to pages.

    Args:
        file_path: path to docx file.

    Returns:
        list of pages.
    """
    doc = Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return paginate(full_text)


def load_pdf(file_path: str) -> List[List]:
    """Load a PDF file and split document to pages.

    Args:
        file_path: path to file

    Returns:
        list of pages.
    """
    # tika's parser requires only str-like paths
    parser_ = parser.from_file
    parsed: BeautifulSoup = BeautifulSoup(parser_(file_path,
                                                  xmlContent=True)["content"],
                                          features="lxml")

    list_of_pages = []
    for div in parsed.find_all("div", {"class": "page"}):
        list_of_paragraphs = []
        for p in div.find_all("p"):
            par = p.text.replace("-\n", "").replace("\n", "")
            if par:
                list_of_paragraphs.append(par)
        if list_of_paragraphs:
            list_of_pages.append(list_of_paragraphs)
    return list_of_pages


def load_html(file_path: str) -> List[List]:
    """Split html content to pages.

    Args:
        file_path: path to file

    Returns:
        list of pages
    """
    if file_path.startswith(("http", "https")):
        file = requests.get(file_path)
        raw_html = file.content
    else:
        with open(file_path, "r") as file:
            raw_html = file.read()
    soup = BeautifulSoup(raw_html, features="lxml")
    # replace non-breaking space
    soup = soup.body.get_text(strip=False).replace("\xa0", " ")
    lines = [line.strip() for line in soup.splitlines() if line.strip()]
    return paginate(lines)


