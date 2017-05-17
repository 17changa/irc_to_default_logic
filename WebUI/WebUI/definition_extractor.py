# This Python file uses the following encoding: UTF-8
import re
from collections import OrderedDict
import os
from .crawler import Crawler

# List of all keywords that the definition parser looks for in determining a definition
DEFINITION_TYPES = [
    u"means", u"includes", u"does not include", u"has the meaning",
    u"shall include", u"shall not include"
]

# Regular expression pattern for finding key terms in the definitions
TERM_REGEX = re.compile(
    r"(?:(“[^”]+”)|(‘[^’]+’)) (?:{0})".format(u"|".join(DEFINITION_TYPES)),
    re.UNICODE | re.IGNORECASE)


# Declares DefExtractor class, originally definition_extractor.py
# This is because Flask makes it complicated to import classes from other python files,
# so I just put everything we need in this file
class DefExtractor:
    # Returns the regular expression pattern for finding key terms
    def get_term_regex(self, term):
        definition_types_pattern = r"({0})".format(u"|".join(DEFINITION_TYPES))
        return re.compile(r"(?:“{0}”|‘{0}’) {1}(.*)".format(
            term, definition_types_pattern), re.UNICODE | re.IGNORECASE)

    # Uses term regex to find and keep a list of defined terms
    def extract_defined_terms(self, level):
        # Puts a new line between each sentence
        text = u'\n'.join(level.get_sentences())
        # Makes array of defined terms
        defined_terms = []
        # Finds all terms that match regex for key terms
        matches = TERM_REGEX.findall(text)
        # Extracts the term based on quotation marks around it
        for group1, group2 in matches:
            term = None
            if group1 != '':
                assert group2 == ''
                assert group1.startswith(u"“") and group1.endswith(u"”")
                term = group1[1:-1]
            if group2 != '':
                assert group1 == ''
                assert group2.startswith(u"‘") and group2.endswith(u"’")
                term = group2[1:-1]
            # Makes sure term is not empty
            assert term is not None and len(term) > 0
            # Adds newly found term to array of defined terms
            defined_terms.append(term)
        # Returns the array of defined terms
        return defined_terms

    # Finds and stores all the definitions of key terms
    def extract_definitions(self, level):
        # Gets all unique defined terms from given level id
        defined_terms = self.extract_defined_terms(level)
        unique_terms = set(defined_terms)
        # Makes an ordered dictionary called definitions
        definitions = OrderedDict()
        # Parses all the sentences in the level and stores them in array sentences
        sentences = level.get_sentences()
        # Finds all the sentences that fit a definition regex pattern and stores them in definitions
        for sentence in sentences:
            for term in unique_terms:
                term_def_regex = self.get_term_regex(term)
                matches = term_def_regex.findall(sentence)
                if len(matches) == 0: continue
                assert len(matches) == 1
                def_type, rest = matches[0]
                assert def_type in DEFINITION_TYPES
                assert len(rest) > 0
                # Terms are sometimes defined multiple times in same section...
                # TODO: Figure out how to efficiently find definitions at levels below section
                while term in definitions:
                    term = u"{}#".format(term)
                # Each term in definitions has a sentence, type, and rest
                definitions[term] = {
                    "sentence": sentence,
                    "type": def_type,
                    "rest": rest
                }
        # Returns the unique terms and dictionary of definitions
        return unique_terms, definitions

    # Creates a new array that matches terms to definitions, originally also creates a
    # first order logic structure for each term
    def terms_definitions(self, level):
        terms_definitions = []
        defined_terms, definitions = self.extract_definitions(level)
        for term, definition in definitions.items():
            terms_definitions.append({
                "term": term,
                "definition": definition,
            })
        return terms_definitions

    # Main function of DefExtractor class that calls on helper methods to parse the lawcode
    # section and returns a dictionary of terms and definitions
    def main(self, lawcode, titlenum, levelid):
        # Creates a crawler to parse through the given xml file
        crawler = Crawler(lawcode, titlenum)
        level = crawler.get_level(levelid)
        # Extracts the terms and definitions based on the given level id
        definitions = self.terms_definitions(level)
        # If there are no definitions in the given section, raises an error
        if len(definitions) == 0:
            raise NoDefinitionsFound()
        # Else returns dictionary of terms and definitions
        else:
            return definitions


# No definitions found error is called on when there are no defined terms in a given level id
class NoDefinitionsFound(Exception):
    def __str__(self):
        return "No term definitions found."
