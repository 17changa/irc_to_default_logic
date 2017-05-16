# -*- coding: utf-8 -*-
# Imports classes needed to create Flask application
from flask import Flask, request, url_for, render_template

# Creates the application with title name
app = Flask(__name__)

# When uncommented configures the app to run with debugging set to true
#app.config.update(dict(DEBUG=True))


# Creates the main page of the app using format from index.html
@app.route('/')
def main():
    return render_template('index.html')


# Imports necessary classes for definition parsing
from os.path import join
from lxml import etree
from nltk.tokenize import sent_tokenize, word_tokenize
import re
from collections import OrderedDict


# Creates the parsing function of the app that received information from the form and posts
# information from the parser
@app.route('/parse', methods=['GET', 'POST'])
def parse():
    # Sets appropriate level id and xml filepath based on the inputs from the web form
    lawcode = request.form.get("lawcode")
    xml_filepath = join(app.root_path, 'xml_files/{0}.xml'.format(lawcode))
    levelid = "s" + request.form.get("levelid")
    # Dictionary corresponding filnames to title numbers
    titlenum = {
        'usc01': '1',
        'usc02': '2',
        'usc03': '3',
        'usc04': '4',
        'usc05': '5',
        'usc05A': '5a',
        'usc06': '6',
        'usc07': '7',
        'usc08': '8',
        'usc09': '9',
        'usc10': '10',
        'usc11': '11',
        'usc11A': '11a',
        'usc12': '12',
        'usc13': '13',
        'usc14': '14',
        'usc15': '15',
        'usc16': '16',
        'usc17': '17',
        'usc18': '18',
        'usc18A': '18a',
        'usc19': '19',
        'usc20': '20',
        'usc21': '21',
        'usc22': '22',
        'usc23': '23',
        'usc24': '24',
        'usc25': '25',
        'usc26': '26',
        'usc27': '27',
        'usc28': '28',
        'usc28A': '28a',
        'usc29': '29',
        'usc30': '30',
        'usc31': '31',
        'usc32': '32',
        'usc33': '33',
        'usc35': '35',
        'usc36': '36',
        'usc37': '37',
        'usc38': '38',
        'usc39': '39',
        'usc40': '40',
        'usc41': '41',
        'usc42': '42',
        'usc43': '43',
        'usc44': '44',
        'usc45': '45',
        'usc46': '46',
        'usc47': '47',
        'usc48': '48',
        'usc49': '49',
        'usc50': '50',
        'usc50A': '50a',
        'usc51': '51',
        'usc52': '52',
        'usc54': '54',
    }
    try:
        # Calls the main method of the definition parser on the chosen xml file
        words = DefExtractor().main(xml_filepath, titlenum[lawcode], levelid)
        # Sends output of the main function to show_definitions.html and displays it accordingly
        return render_template('show_definitions.html', ans=words)
    # Handles errors from executing the code above
    except Exception as e:
        # Displays the error page that properly prints the given error
        return render_template('error.html', err=e)


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


# Defines the level id class that helps the Crawler determine the section/subsections
class LevelId:
    # Regex pattern for parsing level ids
    LEVEL_ID_PATTERN = re.compile(u"^s[^/]+(/[a-zA-Z0-9]+)*$", re.UNICODE)

    # Makes sure that the given level id adheres to regex patterns
    @staticmethod
    def _validate(val):
        # If level id is not in unicode, prints error
        assert isinstance(val, str), u"Non-unicode level id: {0}".format(val)
        # If level id does not fit regex pattern, prints error
        assert LevelId.LEVEL_ID_PATTERN.match(
            val), u"Invalid level id: {0}".format(val)

    # Instantiates a level id, changes val type to str and makes sure level id is properly formatted
    def __init__(self, val):
        val = str(val)
        LevelId._validate(val)
        self.val = val

    # Gets id of section
    def get_section_id(self):
        return self.val.split(u'/')[0]

    # Gets number of section
    def get_section_num(self):
        return self.get_section_id()[1:]

    # Sees how many levels are in section
    def get_depth(self):
        return len(self.val.split(u'/')) - 1

    # Gets the number of the deepest level
    def get_num(self):
        if self.get_depth() == 0:
            return self.get_section_num()
        return self.val.split(u'/')[-1]

    # Methods for converting to str and bytes
    def __str__(self):
        return self.val

    def __bytes__(self):
        return str(self).encode("UTF-8")


# Raises exception when the level does not have a proper id
class LevelHasNoIdException(Exception):
    def __str__(self):
        return "Section has no valid id."


# Raises exception when the given level id does not exist
class LevelDoesNotExistException(Exception):
    def __str__(self):
        return "Section does not exist."


# Keeps track of all the tags in the xml file
TAGS = [
    "section", "subsection", "paragraph", "subparagraph", "clause",
    "subclause", "item", "subitem", "subsubitem"
]


# Defines each level that has a valid level id
class Level:
    # Validates a level based on its given sublevels
    @staticmethod
    def _validate(id, tag, num, heading, chapeau, content, sublevels,
                  continuation):
        # Ensures that the level id of that level is valid
        assert isinstance(id, LevelId)
        # Makes sure the tag is a valid type based on the array of possible tags above
        assert tag in TAGS, u"Unknown tag: {0}".format(tag)
        # Makes sure the num tag is the same as the level id number
        assert num == id.get_num()
        # Makes sure each tag is either none or a str
        for s in [heading, chapeau, continuation, content]:
            assert s is None or isinstance(
                s, str), "Non-unicode text: {0}".format(s)
        # Makes sure sublevels are in the form of an ordered dictionary
        assert isinstance(sublevels, OrderedDict)

    # Instantiates level based on its tags
    def __init__(self, id, tag, num, heading, chapeau, content, sublevels,
                 continuation):
        Level._validate(id, tag, num, heading, chapeau, content, sublevels,
                        continuation)
        self.id = id
        self.tag = tag
        self.num = num
        self.heading = heading
        self.chapeau = chapeau
        self.content = content
        self.sublevels = sublevels
        self.continuation = continuation
        # Lazy evaluation
        self._sentence_fragments = None
        self._sentences = None

    # Uses the nltk sentence tokenizer to join sentence fragments into sentences
    def get_sentences(self, sentence_tokenizer=sent_tokenize):
        if self._sentences is None:
            sent_fragments = self.get_sentence_fragments()
            level_str = u" ".join(sent_fragments)
            self._sentences = sentence_tokenizer(level_str)
        return self._sentences

    # Finds sentence fragments in each sublevel
    def get_sentence_fragments(self):
        if self._sentence_fragments is None:
            sent_fragments = []
            if self.chapeau is not None:
                sent_fragments.append(self.chapeau)
            if self.content is not None:
                sent_fragments.append(self.content)
            for c in self.sublevels.values():
                sublevel, continuation = c[0], c[1]
                sent_fragments.extend(sublevel.get_sentence_fragments())
                if continuation is not None:
                    sent_fragments.append(continuation)
            if self.continuation is not None:
                sent_fragments.append(self.continuation)
            self._sentence_fragments = sent_fragments
        return self._sentence_fragments

    # Converts level to str or bytes
    def __str__(self):
        return u'\n'.join(self.get_sentences())

    def __bytes__(self):
        return str(self).encode("UTF-8")


# Defines crawler class that parses through the xml file
class Crawler:
    # Instantiates the crawler class using given xml filepath
    def __init__(self,
                 xml_filepath,
                 titlenum,
                 default_namespace="USLM",
                 debug=False):
        self.tree = etree.parse(xml_filepath)
        self.root = self.tree.getroot()
        self.default_namespace = default_namespace
        self.nsmap = self.root.nsmap
        self.nsmap[default_namespace] = self.nsmap.pop(None)
        self.debug = debug
        self.titlenum = titlenum

    # Returns default namespace prefix
    def _namespace_prefix(self):
        return "{{{0}}}".format(self.nsmap[self.default_namespace])

    # Converts nodes into str, substitutes ; for . in certain circumstances to improve
    # sentence tokenizing (remove the re.sub if it's decreasing accuracy)
    def _stringify_node(self, node):
        return re.sub(
            u"[^ ]*\u201c",
            ". \u201c",
            etree.tostring(node, method="text",
                           encoding="UTF-8").strip().decode("UTF-8"),
            flags=re.UNICODE)

    # Gets the node based on its level id and xml filepath
    def _get_level_node(self, level_id):
        # Makes sure given level id is a valid LevelId object
        assert isinstance(level_id, LevelId)
        # Filepath of level given titlenum and level id
        xpath_expression = "//{0}:*[@identifier='/us/usc/t{1}/{2}']".format(
            self.default_namespace, self.titlenum, level_id)
        nodes = self.root.xpath(xpath_expression, namespaces=self.nsmap)
        # Makes sure this is a unique node
        assert len(nodes) <= 1
        # If there are no nodes with the given id, raise exception
        if len(nodes) == 0:
            raise LevelDoesNotExistException()
        # Returns the node
        return nodes[0]

    # Parses through the level using its nodes
    def _parse_level(self, node):
        # If the node has no identifier, raise exception
        if node.get("identifier") is None:
            # Happens for some quoted sections that appear in the "notes"
            raise LevelHasNoIdException()
        # Sets the identifier prefix pattern based on the titlenum
        identifier_prefix = u"/us/usc/t{0}/".format(self.titlenum)
        # Makes sure node's identifier starts with the valid prefix
        assert node.get("identifier").startswith(identifier_prefix)
        # Sets the id to the LevelId based on its identifier
        id = LevelId(
            node.get("identifier").replace(identifier_prefix, '', 1).replace(
                "...", " to ", 1))
        # Makes sure tag starts with valid namespace prefix
        ns_prefix = self._namespace_prefix()
        assert node.tag.startswith(ns_prefix)
        tag = node.tag.replace(ns_prefix, '', 1)
        num = None
        level = {
            "heading": None,
            "chapeau": None,
            "content": None,
            "continuation": None
        }
        sublevels = OrderedDict()
        # Gets value of tags/sublevels if they exist, otherwise stringifies the node
        for c in node:
            c_tag = c.tag.replace(ns_prefix, '', 1)
            if c_tag == "num":
                assert num is None, u"Repeated num in level {}".format(id)
                num = c.get("value")
            if c_tag in level:
                if c_tag == "continuation":
                    continuation = self._stringify_node(c)
                    if len(sublevels) == 0:
                        assert level["continuation"] is None
                        level["continuation"] = continuation
                    else:
                        # Continuations can be "sandwiched" between sublevels
                        # See 10.4 in http://xml.house.gov/schemas/uslm/1.0/USLM-User-Guide.pdf
                        prev_sublevel_num = next(reversed(sublevels))
                        prev_sublevel_and_continuation = sublevels[
                            prev_sublevel_num]
                        if prev_sublevel_and_continuation[1] is None:
                            prev_sublevel_and_continuation[1] = continuation
                        else:
                            #assert level["continuation"] is None
                            level["continuation"] = continuation
                else:
                    level[c_tag] = self._stringify_node(c)
            elif c_tag in TAGS:
                sublevel = self._parse_level(c)
                sublevel_num = sublevel.num
                # Apparently, there exist some levels with the same name
                while sublevel_num in sublevels:
                    sublevel_num += "?"
                # First element is sublevel, second element is continuation
                sublevels[sublevel_num] = [sublevel, None]
            # If something is weird with the tag, skips that element
            elif self.debug:
                print(u"Warning: Skipping element with tag {0}".format(c.tag))
        # Returns the level object with the given level id and sublevel tags
        return Level(id, tag, num, level["heading"], level["chapeau"],
                     level["content"], sublevels, level["continuation"])

    # Gets the level based on its level id and nodes, then parses all its sublevels
    def get_level(self, level_id):
        level_id = LevelId(level_id)
        level_node = self._get_level_node(level_id)
        level = self._parse_level(level_node)
        return level
