import sqlite3
import os
import re
from better_profanity import profanity

profanity.load_censor_words(whitelist_words=['horny'])
wordnet_path = 'wordnet-data'
db_path = 'words.db'

# Delete the existing database file if it exists
if os.path.exists(db_path):
    os.remove(db_path)

# Connect to SQLite database (or create it)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create table
cursor.execute('''
CREATE TABLE IF NOT EXISTS words (
    word TEXT,
    type TEXT,
    definitions TEXT
)
''')

def parse_wordnet():
    def is_valid_word(word, definition):
        return (
            word.islower() and
            word.isalpha() and
            len(word) > 1 and
            not is_roman_numeral(word, definition) and
            not is_profanity(word) 
        )

    def clean_word(word):
        return re.sub(r'\(.*?\)', '', word).strip()

    def is_roman_numeral(word, definition):
        return re.match(r'^[ivxlcdm]+$', word) is not None and (definition.startswith('being') or definition.startswith('denoting a quantity'))

    def is_profanity(word):
        if profanity.contains_profanity(word):
            print(f"Removed word: {word}")
            return True
        return False

    # There are many false positives, so keep word but remove definition
    def clean_definition(definition):
        if profanity.contains_profanity(definition):
            print(f"Removed definition: {definition}")
            return ""
        return definition

    def parse_file(file_path, word_type, word_dict):
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith(' ') or not line.strip():
                    continue
                parts = line.split('|')
                definition = clean_definition(parts[1].strip().split(';')[0])
                word_info = parts[0].split()
                words = [clean_word(word_info[i]) for i in range(4, len(word_info), 2)]
                for word in words:
                    if is_valid_word(word, definition):
                        key = (word, word_type)
                        if key in word_dict:
                            word_dict[key] += "#" + definition
                        else:
                            word_dict[key] = definition

    word_dict = {}
    parse_file(os.path.join(wordnet_path, 'data.noun'), 'noun', word_dict)
    parse_file(os.path.join(wordnet_path, 'data.verb'), 'verb', word_dict)
    parse_file(os.path.join(wordnet_path, 'data.adj'), 'adjective', word_dict)
    parse_file(os.path.join(wordnet_path, 'data.adv'), 'adverb', word_dict)

    print(f"Number of words: {len(word_dict)}")

    # Insert all collected data into the database
    for (word, word_type), definitions in word_dict.items():
        cursor.execute('INSERT INTO words (word, type, definitions) VALUES (?, ?, ?)', (word, word_type, definitions))

# Parse WordNet files and insert data into SQLite database
parse_wordnet()

# Commit and close the database connection
conn.commit()
conn.close()