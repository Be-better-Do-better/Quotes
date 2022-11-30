from utils import *
import re
from collections import Counter
import numpy as np

HEBREW_ALPHABET = load_hebrew_alphabet()
ENDING_LETTERS_PAIRS = load_hebrew_ending_letters_pairs()
HEBREW_EHEVI_LETTERS = load_ehevi_letters()

HEBREW_LETTERS_TO_CONSIDER = [letter for letter in HEBREW_ALPHABET if letter not in HEBREW_EHEVI_LETTERS]


def collect_all_hebrew_letters_combinations():
    all_combinations = []

    # add unigrams (single letters)
    # for l in HEBREW_ALPHABET:
    #    all_combinations.append(l)

    # add bigrams (double letters)
    for l1 in HEBREW_ALPHABET:
        for l2 in HEBREW_ALPHABET:
            all_combinations.append((l1, l2))

    # add trigrams (triple letters)
    for l1 in HEBREW_ALPHABET:
        for l2 in HEBREW_ALPHABET:
            for l3 in HEBREW_ALPHABET:
                all_combinations.append((l1, l2, l3))

    return all_combinations


ALL_HEBREW_LETTERS_COMBINATIONS = collect_all_hebrew_letters_combinations()


class Word(object):
    def __init__(self, raw_word):
        self._raw = raw_word
        self._clean_word = self.clean_word()
        self._ngram_counter = Counter()

        self.collect_ngram_frequencies()

    def clean_word(self):
        cleaned_word_as_list = []
        for letter_to_evaluate in self._raw:
            # remove all EHEVI letters and non letters :
            if letter_to_evaluate in HEBREW_LETTERS_TO_CONSIDER:
                cleaned_word_as_list.append(letter_to_evaluate)

            elif letter_to_evaluate in ENDING_LETTERS_PAIRS:
                cleaned_word_as_list.append(ENDING_LETTERS_PAIRS[letter_to_evaluate])
        return ''.join(cleaned_word_as_list)

    def collect_ngram_frequencies(self):

        unigrams = [letter for letter in self._clean_word]
        self._ngram_counter.update(unigrams)

        bigrams = []
        if len(self._clean_word) > 1:
            bigrams = [(self._clean_word[i], self._clean_word[i+1]) for i in range(len(self._clean_word)-1)]

        self._ngram_counter.update(bigrams)

        trigrams = []
        if len(self._clean_word) > 2:
            trigrams = [(self._clean_word[i], self._clean_word[i + 1], self._clean_word[i + 2]) for i in
                        range(len(self._clean_word)-2)]
        self._ngram_counter.update(trigrams)

    def get_ngram_counter(self):
        return self._ngram_counter


def vectorize_text(input_text):
    split_text = re.split('; |, |\*|\n|-', input_text)
    ngrams_counter = Counter()

    for word in split_text:
        word_data = Word(word)
        ngrams_counter += word_data.get_ngram_counter()

    output_vec = np.zeros(len(ALL_HEBREW_LETTERS_COMBINATIONS))

    for ngram, frequency in ngrams_counter.items():
        # print("The N-Gram " + str(ngram) + " has a frequency: {}".format(frequency))
        if ngram in ALL_HEBREW_LETTERS_COMBINATIONS:
            output_vec[ALL_HEBREW_LETTERS_COMBINATIONS.index(ngram)] = frequency

    return output_vec


def norm(v):
    return np.sqrt(np.matmul(v, v))


def vector_dist(v1, v2):
    if norm(v1) > 0 and norm(v2) > 0:
        return np.matmul(v1, v2) / (norm(v1) * norm(v2))
    else:
        return 0.


def inner_product(v1, v2):
    return np.matmul(v1, v2)


def test_vectorize_text():
    # input_text1 = 'בלא-בלא-בלאו!'
    input_text1 = ''
    print(input_text1)
    v1 = vectorize_text(input_text1)

    input_text2 = 'ללכת לעזאזל, אוף!'
    print(input_text2)
    v2 = vectorize_text(input_text2)

    res = vector_dist(v1, v2)
    print(res)



def main():
    all_hebrew_letters_combinations = collect_all_hebrew_letters_combinations()


if __name__ == '__main__':
    test_vectorize_text()
    # main()

