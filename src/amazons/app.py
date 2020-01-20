## Run command
## FLASK_APP=src/amazons/app.py FLASK_ENV=development flask run
import os
import logging
import numpy as np
import time
from threading import Lock
import threading
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

socketio = SocketIO(app, async_mode='threading')

clients_in_waiting = []
game_number = 0
rooms = {}

thread = None


def pair_clients_in_waiting(clients):
    new_waiting_room = clients
    p1, p2 = np.random.choice(new_waiting_room, 2, replace=False)
    new_waiting_room.remove(p1)
    new_waiting_room.remove(p2)
    return new_waiting_room, tuple([p1, p2])

def create_game(sid1, sid2, game):
    """
    Function that pairs two players from the waiting room to a amazons game.
    """
    join_room(str(game), sid1, '/test')
    join_room(str(game), sid2, '/test')
    emit('server_response', {'data': f"Created game #{str(game)}, between {sid1} and {sid2}"}, broadcast=True)

    emit('redirect', {'url': url_for('game')}, str(game))
    emit('server_response', {'data': f"{sid1} and {sid2} joined room {game}"}, str(game))


def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    global clients_in_waiting

    while True:
        global clients_in_waiting
        time.sleep(5)
        logger.info("5 seconds has past")
        socketio.emit('server_response', {'data': f'Clients in waiting: {clients_in_waiting}'}, broadcast=True, namespace='/test')

        count += 1
        # Check if there are enough players
        if len(clients_in_waiting) > 1:
            clients_in_waiting, paired = pair_clients_in_waiting(clients_in_waiting)
            logger.info(paired)
            socketio.emit('update_waiting_room',
                          {'clients_in_waiting': clients_in_waiting}, broadcast=True,
                          namespace='/test')

            # create_game(paired[0], paired[1], count)
            socketio.emit('join_room',  {'user': paired[0], 'room': count}, paired[0], namespace='/test')
            socketio.emit('join_room', {'user': paired[1], 'room': count}, paired[1], namespace='/test')
            socketio.emit('server_response', {'data': f"Created game #{str(game)}, between {paired[0]} and {paired[1]}"},
                 broadcast=True, namespace='/test')

            global rooms
            rooms[str(count)] = {'name': str(count), 'players': {paired[0], paired[1]}}

@app.route("/", methods=["GET"])
def index():
    return render_template('index.html')


@app.route("/game")
def game():
    return render_template('game.html')


@socketio.on('connect', namespace='/test')
def connect():
    emit('server_response', {'data': f'Connected {request.sid}'}, broadcast=True)
    global thread
    if thread is None:
        logger.info("Start Thread")
        thread = socketio.start_background_task(background_thread)


@socketio.on('disconnect', namespace='/test')
def disconnect():
    emit('server_response', {'data': f'Disconnected {request.sid}'}, broadcast=True)
    logger.info(f"Client disconnected: {request.sid}")


@socketio.on('join_room', namespace='/test')
def on_join(data):
    logger.info(f'data: {data}')
    logger.info(f"Adding {request.sid} to a room")
    username = request.sid # request.sid
    room = data['room']
    join_room(str(room))
    session['room'] = str(room)
    emit('server_response', username + ' has entered the room ' + str(room), room=str(room))

    emit('redirect', {'url': url_for('game')}, namespace='/test')


@socketio.on('join', namespace='/test')
def join(message):
    emit('server_response', {'data': f"Client {request.sid} joined waiting."}, broadcast=True)
    clients_in_waiting.append(request.sid)
    logger.debug(f"CLIENTS IN WAITING: {clients_in_waiting}")
    emit('update_waiting_room', {'clients_in_waiting': clients_in_waiting}, broadcast=True)


@socketio.on('move', namespace='/test')
def move(data):
    logger.info(data)
    room = rooms[data['room']]
    sid = data['player']
    # find all players in room
    logger.info(data['player'])
    logger.info(f"ROOMS NIGGA {room} {room['players']}")
    clients_in_room = room['players']
    if sid in clients_in_room:
        opponent = clients_in_room - {request.sid}
        logger.info(f"Je tegenstander is {list(opponent)[0]}. Succes nerd")
        emit('move', data, list(opponent)[0], namespace='/test')

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', debug=True)
