# This Python file uses the following encoding: UTF-8
# from irc_crawler import IRCCrawler
from .crawler import Crawler, Level
from .definition_extractor import DefExtractor
import matplotlib.pyplot as plt
import numpy as np
import operator
import collections
import matplotlib.patches as mpatches
import os


def make_freq_hist(crawl, level, title, levelid):
    APP_STATIC = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'static')
    path = os.path.join(APP_STATIC, 'histograms/hist_t{0}{1}'.format(
        title, levelid))
    extractor = DefExtractor()
    text = u'\n'.join(level.get_sentences())
    num_defined_terms = []
    defined_terms = extractor.extract_defined_terms(level)
    for x in defined_terms:
        p = text.count(x)  # find the terms in text
        num_defined_terms.append(
            p)  # add a number to a list called num_defined_terms
    dictionary = dict(
        zip(defined_terms,
            num_defined_terms))  # match the defined term to their frequencies
    sorteddict = sorted(
        dictionary.items(), key=operator.itemgetter(
            1))  # turn into tuple, sort by value(1) rather than key(0)
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
    section_freq = list(
        section_count.values())  # the frequencies of terms in each section
    section_words = list(
        section_count.keys())  # the words pertaining to each frequency

    # os.chdir('definition_stats')
    # file_object = open('defined_terms.txt', 'r')
    # irc = file_object.readlines()
    keyterms = []
    for section in crawl.iterate_over_sections():
        keyterms.extend(extractor.extract_defined_terms(section))
    # irc_count = collections.Counter(irc)
    term_count = collections.Counter(keyterms)
    # irc_freq = irc_count.values()  # the frequencies themselves
    term_freq = list(term_count.values())
    # irc_words = irc_count.keys()  # the words pertaining to each frequency
    term_words = list(term_count.keys())
    for index, word in enumerate(section_words, start=0):
        # target = word + '\n'
        target_index = list(term_words).index(
            word)  # indexes of each defined word.
        section_index = list(section_words).index(word)
        if term_freq[target_index] > section_freq[section_index]:
            kword = section_words[index]
            realindex = keys.index(kword)
            colors[realindex] = 'g'

    for index, num in enumerate(section_freq, start=0):
        if num > 1:
            kword = section_words[index]
            realindex = keys.index(kword)
            colors[realindex] = 'r'

    plt.figure(figsize=(16, 9))
    pos = np.arange(
        len(values)
    )  # create list with numbers from 1 - the length of the list of frequencies
    ax = plt.axes()
    ax.set_xticks(pos)  # set ticks to the list of numbers
    ax.set_xticklabels(keys, rotation=-30, fontsize=8, ha='left')
    ax.set_aspect(0.16)
    red_patch = mpatches.Patch(
        color='red', label='defined > 1 time within ' + str(levelid))
    green_patch = mpatches.Patch(
        color='green', label='defined > 1 time within Title ' + str(title))
    width = 0.9  # bar width
    plt.bar(
        pos, values, width,
        color=colors)  # create the bars with # bars, each value, and bar width
    plt.legend(handles=[red_patch, green_patch])
    plt.title("Frequency of defined terms in Title " + str(title) + " " +
              str(levelid))
    plt.xlabel("Defined terms")
    plt.ylabel("Number of appearances in specified section")
    plt.savefig(path, bbox_inches='tight')
    plt.close()
