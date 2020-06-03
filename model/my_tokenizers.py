from flair.data import Token, segtok_tokenizer
from nltk import RegexpTokenizer
from segtok.segmenter import split_single
from segtok.tokenizer import split_contractions


def fr_tokenizer(text):
    tokens = []

    # Should we split data with ` char?
    tokenizer = RegexpTokenizer(r"""\w'|\w’|\w`|\w\w+'\w+|[^\w\s]|\w+""")
    words = []
    sentences = split_single(text)
    for sentence in sentences:
        contractions = split_contractions(tokenizer.tokenize(sentence))
        words.extend(contractions)

    # determine offsets for whitespace_after field
    index = text.index
    current_offset = 0
    previous_word_offset = -1
    previous_token = None
    for word in words:
        try:
            word_offset = index(word, current_offset)
            start_position = word_offset
        except ValueError:
            word_offset = previous_word_offset + 1
            start_position = (current_offset +
                              1 if current_offset > 0 else current_offset)

        if word:
            token = Token(text=word,
                          start_position=start_position,
                          whitespace_after=True)
            tokens.append(token)

        if (previous_token is not None) and word_offset - 1 == previous_word_offset:
            previous_token.whitespace_after = False

        current_offset = word_offset + len(word)
        previous_word_offset = current_offset - 1
        previous_token = token

    return tokens


tokenizers = {
    "en": segtok_tokenizer,
    "fr": fr_tokenizer,
    "zh": fr_tokenizer,
    "es": segtok_tokenizer
}
