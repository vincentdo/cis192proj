from flask import Flask, request
import logging
from json import dumps

app = Flask(__name__)

@app.route('/login', methods=['POST'])
def login():
    extracted = json.loads(request.form['data'])
    ta = form['pennkey']
    return blah

@app.route('/getStudent', methods=['GET', 'POST'])
def submit_page():
    if request.method == 'POST':
        msg = '{} was POST-ed'.format(request.form['submit'])
    else:
        msg = request.args.get('submit')
    return redirect((url_for('log', msg=msg, mode='debug')))

def processInput(command):
    # print(command)
    parts = command.split()
    cmd = parts[0]
    if (cmd == 'addTA'):
        addTA(parts[1], parts[2])
    elif (cmd == 'quit'):
        sys.exit(0)
    else:
        print('Invalid command')

def main():
    if len(sys.argv) == 2:
        if (sys.argv[1] == 'cmd'):
            while (True):
                command = input('Enter command: ')
                print(command)
                processInput(command)
    else:
        app.debug = True
        log_handler = logging.FileHandler('my_flask.log')
        log_handler.setLevel(logging.DEBUG)
        app.logger.addHandler(log_handler)
        app.run()

if __name__ == '__main__':
    main()
