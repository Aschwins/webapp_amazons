## Run command
## FLASK_APP=src/amazons/app.py FLASK_ENV=development flask run
import os
import logging
import numpy as np
from threading import Lock
from flask import Flask, jsonify, request
from flask import render_template, session, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_socketio import SocketIO, emit, join_room, leave_room, \
     close_room, rooms, disconnect

from flaskthreads import AppContextThread

# Configure Logger
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.ERROR)

app = Flask(__name__)
app.config["SECRET_KEY"] = "OCML3BRawWEUeaxcuKHLpw"
Bootstrap(app)

async_mode = None

socketio = SocketIO(app, async_mode=async_mode)

clients_in_waiting = []
game_number = 0

thread = None
thread_lock = Lock()


def pair_clients_in_waiting(clients):
    new_waiting_room = clients
    p1, p2 = np.random.choice(new_waiting_room, 2, replace=False)
    new_waiting_room.remove(p1)
    new_waiting_room.remove(p2)
    return new_waiting_room, tuple([p1, p2])


def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    global clients_in_waiting

    while True:
        socketio.sleep(5)
        count += 1
        # Check if there are enough players

        logger.info(f"COUNT {count}")

        if len(clients_in_waiting) > 1:
            with thread_lock:
                clients_in_waiting, paired = pair_clients_in_waiting(clients_in_waiting)
                socketio.emit('update_waiting_room',
                              {'clients_in_waiting': clients_in_waiting}, broadcast=True,
                              namespace='/test')
                create_game(paired[0], paired[1], count)



def create_game(sid1, sid2, game):
    """
    Function that pairs two players from the waiting room to a amazons game.
    """
    join_room(str(game), sid1, '/test')
    join_room(str(game), sid2, '/test')
    emit('server_response', {'data': f"Created game #{str(game)}, between {sid1} and {sid2}"}, broadcast=True)

    emit('redirect', {'url': url_for('game')}, str(game))
    emit('server_response', {'data': f"{sid1} and {sid2} joined room {game}"}, str(game))


@app.route("/", methods=["GET"])
def index():
    return render_template('index.html')


@app.route("/game")
def game():
    return render_template('game.html')


@socketio.on('connect', namespace='/test')
def connect():
    emit('server_response', {'data': f'Connected {request.sid}'}, broadcast=True)

    # Start a Thread to check wether waiting room has enough clients.
    global thread
    if thread is None:
        thread = AppContextThread(target=background_thread)
        thread.start()
        thread.join()


@socketio.on('disconnect', namespace='/test')
def disconnect():
    emit('server_response', {'data': f'Disconnected {request.sid}'}, broadcast=True)
    logger.info(f"Client disconnected: {request.sid}")


@socketio.on('join', namespace='/test')
def join(message):
    emit('server_response', {'data': f"Client {request.sid} joined waiting."}, broadcast=True)
    clients_in_waiting.append(request.sid)
    logger.debug(f"CLIENTS IN WAITING: {clients_in_waiting}")
    emit('update_waiting_room', {'clients_in_waiting': clients_in_waiting}, broadcast=True)


if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', debug=True)
