import os
import re
import json
import logging
import wordnet_to_protobuf_pb2  # Import the generated protobuf classes

wordnet_path = 'wordnet-data'
wordlist_path = 'profanity/wordlist.json'
log_file_path = 'profanity/log.txt'
output_file_path = 'words.pb'  # Change the output file extension to .pb for protobuf

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
        logging.info(f"Parsing {word_type}s")
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
                        types_added = {entry['type'] for entry in word_dict[word]}
                        if word_type not in types_added:
                            word_dict[word].append({'type': word_type, 'definition': definition})

    word_dict = {}
    parse_file(os.path.join(wordnet_path, 'data.noun'), 'n', word_dict)
    parse_file(os.path.join(wordnet_path, 'data.verb'), 'v', word_dict)
    parse_file(os.path.join(wordnet_path, 'data.adj'), 'a', word_dict)
    parse_file(os.path.join(wordnet_path, 'data.adv'), 'r', word_dict)

    logging.info(f"Number of words: {len(word_dict)}")

    # Create a WordNet message
    wordnet = wordnet_to_protobuf_pb2.WordNet()

    # Populate the WordNet message with data
    for word, entries in word_dict.items():
        word_entry = wordnet.entries.add()
        word_entry.word = word
        for entry in entries:
            definition = word_entry.definitions.add()
            definition.type = entry['type']
            definition.definition = entry['definition']

    # Write the serialized data to the output file in protobuf format
    with open(output_file_path, 'wb') as f:
        f.write(wordnet.SerializeToString())

# Parse WordNet files and write data to protobuf file
parse_wordnet()