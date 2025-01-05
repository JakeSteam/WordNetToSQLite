# WordNet to SQLite

This repo provides a Python script to convert WordNet's word data (`/wordnet-data`) into a SQLite database (`words.db`) with 71,361 unique combinations of word & type, with structure:

```
words (word TEXT, type TEXT, definitions TEXT)
```

The intended purpose is for a word game, so non-words, proper nouns, and profanity have been removed where possible.

## Alternate formats

This repo also supports:

- Text file output (`words.txt`, format `word|type|definition`) by enabling `writeToText` in `wordnet-to-sqlite.py`.
- Structured JSON output (`words.json`, format `Map<String, List<Map<String, String>>>`) by using `wordnet-to-json.py`. Note that word types are shortened to first letter (`av` for adverb).

## Sample contents

Filtering `word` to `article`, alphabetical order:

| word          | type      | definitions                                                                                                                                  |
| :------------ | :-------- | :------------------------------------------------------------------------------------------------------------------------------------------- |
| antiparticle  | noun      | a particle that has the same mass as another particle but has opposite values for its other properties                                       |
| article       | noun      | one of a class of artifacts                                                                                                                  |
| article       | verb      | bind by a contract                                                                                                                           |
| articled      | adjective | bound by contract                                                                                                                            |
| particle      | noun      | a function word that can be used in English to form phrasal verbs                                                                            |
| quasiparticle | noun      | a quantum of energy (in a crystal lattice or other system) that has position and momentum and can in some respects be regarded as a particle |

## Notes on contents

Word definitions for the same `type` are combined (e.g. with the noun `article`, but not the verb) with a `#` between definitions.

- `word`:
  - Any words with uppercase letters (e.g. proper nouns) are removed.
  - Any 1 character words are removed.
  - Any words with numbers are removed.
  - Any words with other characters (apostrophes, spaces) are removed.
  - Most profane words (626) are removed.
  - Roman numerals are removed (e.g. `XVII`).
- `type`:
  - Always `adjective` / `adverb` / `noun` / `verb`.
- `definition`:
  - Definition of the word, only uses first definition.
  - Most profane definitions (1124) are replaced with empty space.
  - May contain bracketed usage information, e.g. `(dated)`.
  - May contain special characters like `'`, `$`, `!`, `<`, `[`, etc.

Profanity removal (99% of the processing time) is performed using `profanity/wordlist.json` (see `profanity/log.txt` for removals).

## Reproducing results

If you wish to recreate `words.db` from scratch, you can:

1. Download `WNdb-3.0.tar.gz` from [WordNet](https://wordnet.princeton.edu/download/current-version) (or any other WordNet databases, I used [this fork](https://github.com/globalwordnet/english-wordnet)).
2. Extract it, and place the `data.x` files in `/wordnet-data/`.
3. Run `py wordnet-to-sqlite.py`.

The raw data looks like this ("unknown" is the only valid noun to extract):

```
08632096 15 n 03 unknown 0 unknown_region 0 terra_incognita 0 001 @ 08630985 n 0000 | an unknown and unexplored region; "they came like angels out the unknown"
```

This script takes ~60 seconds on an average laptop. Efficiency is not a priority, as the output database only needs generating once.

Notes on WordNet's data files [are here](https://wordnet.princeton.edu/documentation/wndb5wn), this repo just does a "dumb" parse then filters out numerical data.
