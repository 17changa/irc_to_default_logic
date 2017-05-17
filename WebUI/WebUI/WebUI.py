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


from os.path import join
from .definition_extractor import DefExtractor


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
