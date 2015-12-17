from flask import Flask, request
import logging
from json import dumps

app = Flask(__name__)

# TODO: Integrate REST API at some point

def main():
    app.debug = True
    log_handler = logging.FileHandler('my_flask.log')
    log_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(log_handler)
    app.run()

if __name__ == '__main__':
    main()
