from ppadb.client import Client
import time 
import threading
from flask import Flask, request
from flask_cors import CORS, cross_origin
from playsound import playsound

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

adb = Client(host='127.0.0.1',port=5037)
devices = adb.devices()

if len(devices) == 0:
    print("no devices found")
    quit()

device = devices[0]

class Command:
    Initialize = -1
    SelectRole = 0
    SelectWord = 1
    Restart = 2
    Yes = 3
    No = 4
    FoundWord = 5
    Error = 6
    OtherSound = 7

Instructions = """
Hello Sarah! I'm a bot specifically made for you! Here is how I operate:

1. You type a message in the chat
2. If I can interpret your message, I'll tap the screen on the word/role you tell me to
3. I'll sometimes reply back in the chat with a message about what I did. Especially if I 
can't read what you want me to do.

Here are a list of commands. If the command has the <N> symbol, this means you enter a number in this location. 

Commands:
'role:<N>'  - Select a role 1-4
'word:<N>'  - Select a word 1-5
'restart'   - Restart the game so you can try different words (not implemented yet)
'yes' or 'y'- Answer yes to someone's question, it will play a success sound (not implemented yet)
'no' or 'n' - Answer no to someone's question, it will play a failure sound (not implemented yet)
'found'     - They found the word! Plays the found a word sound (not implemented yet)

Good luck!
"""

rolePositions = [(310, 1000),(733, 1000), (310, 1400),(733, 1400)]
wordPositions = [(500, 420),(500, 620),(500, 820),(500, 1020),(500, 1220)]

def select_role(position):
    position = int(position)
    assert position > 0 and position <= len(rolePositions), "Must be a valid role position"

    position = position - 1
    x = rolePositions[position][0]
    y = rolePositions[position][1]
    device.shell(f'input tap {x} {y}')

def select_word(position):
    position = int(position)
    assert position > 0 and position <= len(wordPositions), "Must be a valid word position"

    position = position - 1
    x = wordPositions[position][0]
    y = wordPositions[position][1]
    device.shell(f'input tap {x} {y}')

def found_word_sound():
    playsound("./sounds/found.mp3")

def no_sound():
    playsound("./sounds/no.mp3")

def yes_sound():
    playsound("./sounds/yes.mp3")

def other_sound(name):
    try:
        playsound("./sounds/{}.mp3".format(name))
        return True
    except:
        print("The sound '{}' didn't work".format(name))
        return False

def input_from_console():
    role = int(input("What is your role?"))
    select_role(role+1)

    word = int(input("What is your word?"))
    select_word(word+1)


def accept_from(name):
    if (not isinstance(name, str)):
        return False

    return name.lower() in ["sarah burt", "sarah"]

def message_to_command(message):
    message = message.lower().strip()
    if ':' in message:
        sm = message.split(':')
        if (sm[0] == 'role'):
            return (Command.SelectRole, int(sm[1]))
        elif (sm[0] == 'word'):
            return (Command.SelectWord, int(sm[1]))
        else:
            return (Command.Error, "contains ':' but doesn't start with 'role' or 'word' followed by a number (eg. word:2)")

    if 'restart' == message:
        return (Command.Restart,)
    
    if 'yes' == message or 'y' == message:
        return (Command.Yes,)
        
    if 'no' == message or 'n' == message:
        return (Command.No,)

    if 'found' == message:
        return (Command.FoundWord,)

    if 'init' == message:
        return (Command.Initialize, Instructions)

    if 'power' == message:
        return (Command.OtherSound, "power")

    return (Command.Error, 'Invalid input. Fails to match any condition')

def build_response(text, addToChat=False):
    return {
        'text':text,
        'log': addToChat
    }

@app.route('/wereword', methods=['POST'])
@cross_origin()
def accept_command():
    content = request.json
    name = "sarah" #content['name']
    message = content['message']

    if (not accept_from(name)):
        return build_response("Not from Sarah", True)

    action = message_to_command(message)
    command = action[0]

    if (Command.Error == command):
        return build_response(action[1])

    if (Command.SelectRole == command):
        select_role(action[1])
        return build_response("Selected Role {}".format(action[1]), True)
    
    if (Command.SelectWord == command):
        select_word(action[1])
        return build_response("Selected Word {}".format(action[1]), True)

    if (Command.FoundWord == command):
        found_word_sound()
        return build_response("Played 'found word' sound")

    if (Command.Yes == command):
        yes_sound()
        return build_response("Played 'Yes' sound")
        
    if (Command.No == command):
        no_sound()
        return build_response("Played 'No' sound")
    
    if (Command.Error == command):
        return build_response(action[1], True)

    if (Command.Initialize == command):
        return build_response(action[1], True)

    if (Command.OtherSound == command):
        success = other_sound(action[1])
        if success:
            return build_response("Played the '{}' sound".format(action[1]), True)
        else:
            return build_response("Failed to play the '{}' sound".format(action[1]), True)

    return build_response("Something went wrong and I don't know what. This error should never happen", True)

if __name__ == "__main__":
    # input_from_console()
    app.run()
