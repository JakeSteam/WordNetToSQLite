import os
import re
import json
import logging

wordnet_path = 'wordnet-data'
wordlist_path = 'profanity/wordlist.json'
log_file_path = 'profanity/log.txt'
output_file_path = 'words.json'
writeToText = True  # Set this flag to True to write to a JSON file, False to write to the database

# Open the log file in write mode to clear its contents
with open(log_file_path, 'w'):
    pass
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(message)s')

# Load custom word list
with open(wordlist_path, 'r', encoding='utf-8') as f:
    profane_words = set(json.load(f))

# Combine all profane words into a single regular expression
combined_profanity_regex = re.compile(r'\b(?:' + '|'.join(re.escape(word) for word in profane_words) + r')\b', re.IGNORECASE)

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
        if word in profane_words:
            logging.info(f"Removed word: {word}")
            return True
        return False

    # There are false positives, so keep word but remove definition
    def clean_definition(definition):
        match = combined_profanity_regex.search(definition)
        if match:
            logging.info(f"Removed definition for '{match.group()}': {definition}")
            return ""
        return definition

    def parse_file(file_path, word_type, word_dict):
        print(f"Parsing {word_type}s")
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
                        if word not in word_dict:
                            word_dict[word] = []
                        types_added = {entry['t'] for entry in word_dict[word]}
                        if word_type not in types_added:
                            word_dict[word].append({'t': word_type, 'd': definition})

    word_dict = {}
    parse_file(os.path.join(wordnet_path, 'data.noun'), 'n', word_dict)
    parse_file(os.path.join(wordnet_path, 'data.verb'), 'v', word_dict)
    parse_file(os.path.join(wordnet_path, 'data.adj'), 'a', word_dict)
    parse_file(os.path.join(wordnet_path, 'data.adv'), 'r', word_dict)

    print(f"Number of words: {len(word_dict)}")

    if writeToText:
        # Write all collected data to the output file in minified JSON format
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(word_dict, f, ensure_ascii=False, separators=(',', ':'))
    else:
        # Insert all collected data into the database using batch insertion
        data_to_insert = [(word, entry['t'], entry['d']) for word, entries in word_dict.items() for entry in entries]
        cursor.executemany('INSERT INTO words (word, type, definitions) VALUES (?, ?, ?)', data_to_insert)
        cursor.execute('CREATE INDEX idx_word ON words (word)')

# Parse WordNet files and insert data into SQLite database or write to JSON file
parse_wordnet()

if not writeToText:
    conn.commit()
    conn.close()