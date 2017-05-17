# Web UI for Law Code Definition Parser
This is a web user interface that implements the [irc_to_default_logic](https://github.com/mpertierra/irc_to_default_logic) natural language processing algorithms. Specifically, it uses functions from [irc_crawler.py](https://github.com/mpertierra/irc_to_default_logic/blob/master/scripts/irc_crawler.py) and [definition_extractor.py](https://github.com/mpertierra/irc_to_default_logic/blob/master/scripts/definition_extractor.py) (modified for compatibility with Python3.6 and Flask) to generate key terms and definitions from given sections of the United States Law Code.

## Setup
This UI requires Flask to be installed on the target computer. This can be done through
```
pip install Flask
```

## Running the Flask Application
Navigate to the ```WebUI``` folder in your system using the commands below, replacing ```[filepath]``` with the actual location of your ```WebUI``` folder

```
cd [filepath]/WebUI
```
Next, tell Flask where to find the application by using
```
export FLASK_APP=WebUI/WebUI.py
```
Finally, run the application
```
flask run
```

>_To make the web server available to other computers on your network, run the following code instead_
>```
>flask run --host=0.0.0.0
>```
>_This should only be used if the debugger is disabled or you trust the users on your network._

## Using the UI
When the application is ran, the terminal will output a message in the form of
```
* Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```
Navigate to that link in your browser. Now you should see the web interface displayed on the screen.

There are currently two user-defined inputs:
* A dropdown menu of available US Law Codes
* A text-input area for the level id of the section you want to parse

The default level id value is 1, but please make sure you enter a valid level id for the chosen law code, otherwise the program will return an error. The level id should be in the format
```
[section]/[subsection]/[paragraph]/[subparagraph]/[clause]/[subclause]/[item]/[subitem]/[subsubitem]
```
For example, ```163/h/1``` specifies section 163, subsection h, paragraph 1.

Press the ```Submit``` button, and you will be redirected to either an error message or a list of terms and definitions that the parser found.

Press the ```Return``` link at the bottom of screen to go back to the main page at any time.


## Debugging
*Note: Currently this WebUI only runs on Python 3+ and you will get a type error if Python 3 is not set up on your system*

In addition, there are a couple errors the page could display if the inputs are not valid:
```
Error: No term definitions found
```
Means the program could not find any definable terms in the given section. Definitions can only be found in sections with the heading "Definitions". Check a pdf or xml file of the given law code to see if your section has valid definitions.

```
Error: Invalid level id
```
Means that the level id you entered is not properly formatted. Please see the "Using the UI" section for instructions on how to properly format the level id.

```
Error: Section has no valid id
```
This error is raised when the tags in the given section are not properly formatted. Check the xml files to see if the identifiers adhere to normal patterns.

```
Error: Section does not exist
```
Means that there is no section in the chosen law code that can be identified with the given level id. Check that your level id is properly formatted, and that there actually exists such a section in the law code xml file.

>Lastly, if all else fails, try to debug the code manually through the built-in Flask debugger.
>
>To enable the Flask debugger, run the following commands in terminal
>```
>export FLASK_DEBUG=1
>```
>Warning: The Flask debugger allows the user to enter executable code, so only turn this on when necessary.

>If changes to the code (especially the CSS file) do not show up on the webpage, try re-exporting the app, restarting flask, and/or hard-refreshing the webpage (CTRL-F5 on Windows)
