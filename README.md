# Boolean-Retrieval-Model

Inverted index and Positional index for a set of collection to facilitate Boolean Model of IR. Inverted files and Positional files are the primary data structure to support the efficient determination of which documents contain specified terms and at which proximity.
Basic Assumption for Boolean Retrieval Model

1) An index term (word) is either present (1) or absent (0) in the document. A dictionary contains all index terms.
2) All index terms provide equal evidence with respect to information needs. (No frequency count necessary, but in next assignment it can be)
3) Queries are Boolean combinations of index terms (at max 3).
4) Boolean Operators (AND, OR and NOT) are allowed. For examples: X AND Y: represents doc that contains both X and Y X OR Y: represents doc that contains either X or Y NOT X: represents the doc that do not contain X
5) Queries of the type X AND Y / 3 represents doc that contains both X and Y and 3 words apart.
