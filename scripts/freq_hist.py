# This Python file uses the following encoding: UTF-8
from irc_crawler import IRCCrawler
from definition_extractor import extract_defined_terms
import matplotlib.pyplot as plt
import numpy as np
import operator
import collections
import matplotlib.patches as mpatches
import os

def make_freq_hist(level):
    text = u'\n'.join(level.get_sentences())
    num_defined_terms = []
    defined_terms = extract_defined_terms(level)
    for x in defined_terms:
        p = text.count(x)  # find the terms in text
        num_defined_terms.append(p)  # add a number to a list called num_defined_terms
    dictionary = dict(zip(defined_terms, num_defined_terms))  # match the defined term to their frequencies
    sorteddict = sorted(dictionary.items(),
                        key=operator.itemgetter(1))  # turn into tuple, sort by value(1) rather than key(0)
    sorteddict.reverse()  # make order descending
    keys = []
    values = []
    for i in sorteddict:
        keys.append(i[0])  # list of keys/terms
        values.append(i[1])  # list of values/frequencies
    colors = []
    while len(colors) < len(keys):
        colors.append('b')
    section_count = collections.Counter(defined_terms)
    section_freq = section_count.values()  # the frequencies of terms in each section
    section_words = section_count.keys()  # the words pertaining to each frequency
    for index, num in enumerate(section_freq, start=0):
        if num > 1:
            kword = section_words[index]
            realindex = keys.index(kword)
            colors[realindex] = 'r'
    os.chdir('definition_stats')
    file_object = open('defined_terms.txt', 'r')
    irc = file_object.readlines()
    irc_count = collections.Counter(irc)
    irc_freq = irc_count.values()  # the frequencies themselves
    irc_words = irc_count.keys()  # the words pertaining to each frequency
    for index, word in enumerate(section_words, start=0):
        hi = word + '\n'
        hii = irc_words.index(hi.encode('ascii', 'ignore'))  # indexes of each defined word.
        h = section_words.index(word)
        if irc_freq[hii] > section_freq[h]:
            kword = section_words[index]
            realindex = keys.index(kword)
            colors[realindex] = 'g'
    plt.figure(figsize=(16, 9))
    pos = np.arange(len(values))  # create list with numbers from 1 - the length of the list of frequencies
    ax = plt.axes()
    ax.set_xticks(pos)  # set ticks to the list of numbers
    ax.set_xticklabels(keys, rotation=-30, fontsize=8, ha='left')
    ax.set_aspect(0.16)
    red_patch = mpatches.Patch(color='red', label='defined > 1 time within ' + str(args.level_id))
    green_patch = mpatches.Patch(color='green', label='defined > 1 time within IRC')
    width = 0.9  # bar width
    plt.bar(pos, values, width, color=colors)  # create the bars with # bars, each value, and bar width
    plt.legend(handles=[red_patch, green_patch])
    plt.title("Frequency of defined terms in IRC in " + str(args.level_id))
    plt.xlabel("Defined terms")
    plt.ylabel("Number of appearances in specified section")
    plt.show()


def main(args):
    crawler = IRCCrawler()
    level = crawler.get_level(args.level_id)
    make_freq_hist(level)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Extract definitions from parts of the Internal Revenue Code.")
    parser.add_argument("--level-id",
                        type=str,
                        default="s163/h",
                        help="Specifies the level (section, subsection, paragraph, etc.) to find. " + \
                             "Should have pattern s[section]/[subsection]/[paragraph]/[subparagraph]/[clause]/[subclause]/[item]. " + \
                             "For example, 's163/h/1' specifies section 163, subsection h, paragraph 1.")
    args = parser.parse_args()
    main(args)
