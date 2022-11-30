# version 2.4
# Last updated: 29.11.2022
import numpy as np
import pandas as pd
import os
from random import randint, randrange
import codecs
import re
import random
from collections import Counter

from hebrew_alphabet_vectorization import *

# QUOTES_FILE_NAME = 'quotes_very_short.txt'
# QUOTES_FILE_NAME = 'quotes_short.txt'
QUOTES_FILE_NAME = 'quotes.txt'

MAXIMAL_ALLOWED_NUMBER_OF_QUOTES_IN_ONE_GAME = 25

QUOTE_PATTERN = '(.*)\((.*)\)$'
QUOTE_WITH_TRANSLATION_PATTERN = '(.*\n)(.*)\((.*)\)$'

COMPILED_QUOTE_PATTERN = re.compile(QUOTE_PATTERN)
COMPILED_QUOTE_WITH_TRANSLATION_PATTERN = re.compile(QUOTE_WITH_TRANSLATION_PATTERN)


def print_lines(line, window_length=80):
    end_of_window_length = round(3/4 * window_length)
    if len(line) <= window_length:
        print(line)
    else:
        space_index = line.rfind(' ',window_length-end_of_window_length, window_length)
        comma_index = line.rfind(',', window_length - end_of_window_length, window_length)
        period_index = line.rfind('. ', window_length - end_of_window_length, window_length)
        chosen_index = max([space_index, comma_index, period_index])

        if chosen_index == -1:
            chosen_index = window_length

        print(line[0:chosen_index])
        print_lines(line[chosen_index:], window_length)


class Quote(object):
    def __init__(self, quote, quotee=None, source=None):
        self.quote = quote
        self.quotee = quotee
        self.source = source

        self.vec = vectorize_text(quote)
        self.was_used = False

    def print_quote(self):
        # print('\n')
        print_lines(self.quote)
        print('מי אמר/ה:')
        print_lines(self.quotee)
        if self.source is not None:
            print('מהיכן לקוח:')
            print_lines(self.source)
        # print('\n')

    def use_quote(self):
        self.print_quote()
        self.was_used = True


class Quotes(object):
    def __init__(self, quotes_file_name):
        self.quotes_file_name = quotes_file_name
        self.quotes = []
        self.quotees_counter = Counter()
        self.last_quote = None

        self.load_quotes()
        constant_weights = np.ones(len(self.quotes))
        self.weights = np.expand_dims(constant_weights, axis=1)
        self.fill_quotees_counter()
        self.print_quotees_counter()

    def load_quotes(self):
        splitting_delimiter = os.linesep*2  # '\n\n'

        f = codecs.open(self.quotes_file_name, "r", "utf-8")
        all_quotes_text = f.read()
        f.close()

        all_quotes = all_quotes_text.split(splitting_delimiter)
        line_index = 0
        for full_quote in all_quotes:
            self.quotes.append(self.extract_quote(full_quote))

    def extract_quote(self, full_quote):
        if COMPILED_QUOTE_PATTERN.match(full_quote):
            quote, quotee_and_source = COMPILED_QUOTE_PATTERN.match(full_quote).groups()
        elif re.match(QUOTE_WITH_TRANSLATION_PATTERN, full_quote):
            m = re.match(QUOTE_WITH_TRANSLATION_PATTERN, full_quote)
            quote_in_source_language = m.group(1)
            quote = m.group(2)
            quotee_and_source = m.group(3)
        else:
            quote = full_quote
            quotee_and_source = 'Anonymous'

        quotee, source = self.extract_quotee_and_source(quotee_and_source)

        return Quote(quote=quote, quotee=quotee, source=source)

    @staticmethod
    def extract_quotee_and_source(quotee_and_source):
        source = None  # init value
        m = re.search(',', quotee_and_source)
        if m:
            quotee = quotee_and_source[:m.start()]
            source = quotee_and_source[m.start()+2:]
        else:
            quotee = quotee_and_source

        return quotee, source

    def print_all_quotes(self):
        for quote_index, quote in self.quotes.items():
            quote.use_quote()

    def print_random_quote(self):
        tries_left = 10
        if len(self.quotes) > 0 and tries_left > 0:
            selected_quote_as_list = random.choices(self.quotes, weights=self.weights, cum_weights=None, k=1)
            selected_quote = selected_quote_as_list[0]
            if not selected_quote.was_used:
                selected_quote.use_quote()
                index_of_selected_quote = self.quotes.index(selected_quote)
                self.last_quote = self.quotes.pop(index_of_selected_quote)
                weights_without_selected_quote = np.delete(self.weights, index_of_selected_quote)
                self.weights = weights_without_selected_quote
                # An un-used quote was found in the allowed number of turns
                return True
            else:
                tries_left -= 1

        # An un-used quote was not found
        return False

    def update_weights(self, user_text_vec):
        # self.weights = [vector_dist(user_text_vec, quote.vec) for quote in self.quotes]
        new_weights = [inner_product(user_text_vec, quote.vec) for quote in self.quotes]
        self.weights = np.expand_dims(new_weights, axis=1)

    def fill_quotees_counter(self):
        for q in self.quotes:
            self.quotees_counter.update([q.quotee])

    def print_quotees_counter(self):
        quotee_rating = 1
        for quotee_name, counts in self.quotees_counter.most_common():
            print("{}) ".format(quotee_rating) + quotee_name + " ({}) ".format(counts))
            quotee_rating += 1


class Game(object):
    def __init__(self, quotes_file_name):
        self.quotes_file_name = quotes_file_name
        self.quotes = Quotes(self.quotes_file_name)
        self.favourite_quotes = []
        self.last_quote = None

        self.user_text = ''
        self.user_text_vectorized = vectorize_text(self.user_text)

        self.finish_game = False
        self.user_response = None

        self.turns_left = MAXIMAL_ALLOWED_NUMBER_OF_QUOTES_IN_ONE_GAME  # Maximal number of quotes in a single game

    def opening_announcement(self):
        print("\n\n\n")
        print("פתגמים ואמרות הם בעלי ערך רב")
        print("כמה פתגמים שימושיים יתרמו לחיים מאושרים יותר מספרים עבי כרס, בלתי מושגים. (סנקה)")
        print('ברוכים הבאים!')
        print("בחר מתוך {} הציטוטים הנפלאים!".format(len(self.quotes.quotes)))

    @staticmethod
    def closing_announcement():
        print('להתראות!')

    def run(self):
        self.opening_announcement()
        self.get_new_user_text()

        while not self.finish_game:
            self.run_single_turn()

        self.closing_announcement()


    def run_single_turn(self):
        self.print_rules_of_game()
        self.user_response = input('>')
        self.decide_what_to_do()
        print('\n')

    def decide_what_to_do(self):
        if self.turns_left <= 0:
            self.finish_game = True
            self.end_of_turns_announcement()

        elif len(self.user_response) == 0:
            success = self.quotes.print_random_quote()
            if success:
                self.turns_left -= 1
        elif self.user_response.lower() == 'h':
            self.print_help()
        elif self.user_response.lower() == 'u':
            self.get_new_user_text()
        elif self.user_response.lower() == 'd':
            self.display_user_text()
        elif self.user_response.lower() == '+':
            self.like_last_quote()
        elif self.user_response.lower() == 'x':  # HACKING POINT
            print(self.user_text_vectorized)
            print(self.quotes.weights)
            print("Turns left = {}".format(self.turns_left))

        else:
            self.finish_game = True

    def get_new_user_text(self):
        self.user_text = input('הכניסו טקסט מעניין:')
        self.update_user_profile()
    
    def update_user_profile(self):
        user_profile_as_text = self.user_text
        for q in self.favourite_quotes:
            user_profile_as_text += ' ' + q.quote

        self.user_text_vectorized = vectorize_text(user_profile_as_text)
        self.quotes.update_weights(self.user_text_vectorized)

    def like_last_quote(self):
        self.favourite_quotes.append(self.quotes.last_quote)
        self.update_user_profile()

    def display_user_text(self):
        print('הטקסט שכתב המשתמש הוא:')
        print(self.user_text)

    def end_of_turns_announcement(self):
        print('הגעת למספר הציטוטים המירבי המותר.')

    def print_help(self):
        print('Enter - קבל עוד ציטוט')
        print('h - תפריט')
        print('u - הכנס טקסט להשוואה')
        print('d - הצג טקסט משתמש')
        print('+ - אהבתי את הציטוט האחרון')
        print('יציאה - כל מקש אחר')

    def print_rules_of_game(self):
        print('Enter - קבל עוד ציטוט')
        print('h - תפריט')
        print('יציאה - כל מקש אחר')

def play_game():
    quotes_file_name = os.path.join(os.getcwd(), QUOTES_FILE_NAME)
    game = Game(quotes_file_name)
    game.run()

if __name__ == '__main__':
    # test_Quotes()
    play_game()