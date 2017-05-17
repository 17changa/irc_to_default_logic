# This Python file uses the following encoding: UTF-8
from os.path import join
from lxml import etree
from collections import OrderedDict
import re
from nltk.tokenize import sent_tokenize


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
