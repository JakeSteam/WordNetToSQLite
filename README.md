# WordNet to SQLite

This repo provides a Python script to convert WordNet's word data (`/wordnet-data`) into a SQLite database (`words.db`) with unique combinations of word & type, with structure:

```
words (word TEXT, type TEXT, definitions TEXT)
```

## Sample contents

Filtering `word` to `article`, alphabetical order:

| word          | type      | definitions                                                                                                                                                                                                                                                  |
| :------------ | :-------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| antiparticle  | noun      | a particle that has the same mass as another particle but has opposite values for its other properties                                                                                                                                                       |
| article       | noun      | one of a class of artifacts#nonfictional prose forming an independent part of a publication#(grammar) a determiner that may indicate the specificity of reference of a noun phrase#a separate section of a legal document (as a statute or contract or will) |
| article       | verb      | bind by a contract                                                                                                                                                                                                                                           |
| articled      | adjective | bound by contract                                                                                                                                                                                                                                            |
| particle      | noun      | a function word that can be used in English to form phrasal verbs#a body having finite mass and internal structure but negligible dimensions#(nontechnical usage) a tiny piece of anything                                                                   |
| quasiparticle | noun      | a quantum of energy (in a crystal lattice or other system) that has position and momentum and can in some respects be regarded as a particle                                                                                                                 |

## Notes on contents

Word definitions for the same `type` are combined (e.g. with the noun `article`, but not the verb) with a `#` between definitions.

- `word`:
  - Any words with uppercase letters (e.g. proper nouns) are removed.
  - Any words with numbers are removed.
  - Any words with other characters (apostrophes, spaces) are removed.
  - Roman numerals are excluded (e.g. `XVII`).
- `type`:
  - Always `adjective` / `adverb` / `noun` / `verb`.
- `definition`:
  - Definition of the word, may contain multiple if the word appears as a synonym for another word.
  - May contain bracketed usage information, e.g. `(dated)`.
  - May contain special characters like `'`, `$`, `!`, `<`, `[`, etc.

## Reproducing results

If you wish to recreate `words.db` from scratch, you can:

1. Download `WNdb-3.0.tar.gz` from [WordNet](https://wordnet.princeton.edu/download/current-version).
2. Extract it, and place the `data.x` files in `/wordnet-data/`.
3. Run `py wordnet-to-sqlite.py`.

Notes on WordNet's data files [are here](https://wordnet.princeton.edu/documentation/wndb5wn), this repo just does a "dumb" parse then filters out numerical data.
