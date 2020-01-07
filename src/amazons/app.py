## Run command
## FLASK_APP=src/amazons/app.py FLASK_ENV=development flask run
import os

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from flask import Flask, jsonify, request
from flask import render_template, session, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_socketio import SocketIO, emit, join_room, leave_room, \
     close_room, rooms, disconnect

app = Flask(__name__)
Bootstrap(app)

async_mode = None

socketio = SocketIO(app, async_mode=async_mode)

clients = []
clients_in_waiting_room = []
game_number = 0


def create_game(sid1, sid2, game):
    """
    Function that pairs two players from the waiting room to a amazons game.
    """

    join_room(game, sid1, '/test')
    join_room(game, sid2, '/test')
    leave_room('waiting_room', sid1, '/test')
    leave_room('waiting_room', sid2, '/test')
    emit('my_response', {'data': f"Created game #{game}, between {sid1} and {sid2}"}, broadcast=True)


@app.route("/", methods=["GET"])
@app.route("/index", methods=["GET"])
def index():
    print(session)
    return render_template('index.html')


@app.route("/hello/<name>", methods=["GET"])
def get_hello(name):
    return f"Hello {name}"


@app.route("/game")
def game():
    return render_template('game.html')


# Sockets
@socketio.on('my_event')
def handle_message(message):
    logger.info('recieved message: ' + message)
    emit('my_response', 'This is my response')


@socketio.on('connect', namespace='/test')
def test_connect():
    clients.append(request.sid)
    logger.info(f"Client added: {clients}")
    emit('my_response', {'data': f'Connected {request.sid}'}, broadcast=True)


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    clients.remove(request.sid)
    clients_in_waiting_room.remove(request.sid)
    emit('my_response', {'data': f'Disconnected {request.sid}'}, broadcast=True)
    logger.info(f"Client disconnected: {request.sid}")


@socketio.on('join', namespace='/test')
def join(message):
    join_room(message['room'])
    logger.info(f"ROOMS: {rooms()}")
    emit('my_response', {'data': 'In rooms: ' + ', '.join(rooms())}, broadcast=True)
    emit('joined_waiting_room', request.sid)
    clients_in_waiting_room.append(request.sid)

    # Check if the waiting room contains enough players.
    if len(clients_in_waiting_room) > 1:
        # Create a new room where both clients are joined.
        for client in clients_in_waiting_room:
            if client != request.sid:
                other_player = client
                break

        global game_number
        game_number += 1
        create_game(request.sid, other_player, game_number)
        clients_in_waiting_room.remove(request.sid)
        clients_in_waiting_room.remove(other_player)
        emit('redirect', {'url': url_for('game')})


if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', debug=True)
