import codecs
HEBREW_LETTERS_FILE = 'hebrew_alphabet.txt'
HEBREW_ENDING_LETTERS_FILE = 'hebrew_alphabet_ending_letters.txt'
HEBREW_EHEVI_LETTERS_FILE = 'hebrew_ehevi_letters.txt'


def load_hebrew_alphabet():
    basic_herbrew_alphabet = []
    f = codecs.open(HEBREW_LETTERS_FILE, "r", "utf-8")
    for letter in f.readlines():
        basic_herbrew_alphabet.append(letter.strip())
    f.close()
    return basic_herbrew_alphabet


def load_hebrew_ending_letters_pairs():
    ending_letters_pairs = {}
    f = codecs.open(HEBREW_ENDING_LETTERS_FILE, "r", "utf-8")
    for ending_letters_pair in f.readlines():
        split_pair = ending_letters_pair.split()
        ending_letter = split_pair[0]
        common_letter = split_pair[1]
        ending_letters_pairs[ending_letter] = common_letter
    f.close()
    return ending_letters_pairs

def load_ehevi_letters():
    hebrew_ehevi_letters = []
    f = codecs.open(HEBREW_EHEVI_LETTERS_FILE, "r", "utf-8")
    for letter in f.readlines():
        hebrew_ehevi_letters.append(letter.strip())
    f.close()
    return hebrew_ehevi_letters