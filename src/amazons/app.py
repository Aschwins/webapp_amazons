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
app.config["SECRET_KEY"] = "OCML3BRawWEUeaxcuKHLpw"
Bootstrap(app)

async_mode = None

socketio = SocketIO(app, async_mode=async_mode)

clients_in_waiting = []
game_number = 0


def create_game(sid1, sid2, game):
    """
    Function that pairs two players from the waiting room to a amazons game.
    """
    join_room(str(game), sid1, '/test')
    join_room(str(game), sid2, '/test')
    leave_room('waiting_room', sid1, '/test')
    leave_room('waiting_room', sid2, '/test')
    emit('server_response', {'data': f"Created game #{str(game)}, between {sid1} and {sid2}"}, broadcast=True)


@app.route("/", methods=["GET"])
@app.route("/index", methods=["GET"])
def index():
    print(session)
    return render_template('index.html')

@app.route("/game")
def game():
    return render_template('game.html')


@socketio.on('connect', namespace='/test')
def connect():
    emit('server_response', {'data': f'Connected {request.sid}'}, broadcast=True)


@socketio.on('disconnect', namespace='/test')
def disconnect():
    emit('server_response', {'data': f'Disconnected {request.sid}'}, broadcast=True)
    logger.info(f"Client disconnected: {request.sid}")


@socketio.on('join', namespace='/test')
def join(message):
    emit('server_response', {'data': f"Client {request.sid} joined waiting."}, broadcast=True)
    clients_in_waiting.append(request.sid)
    logger.info(f"CLIENTS IN WAITING: {clients_in_waiting}")
    emit('update_waiting_room', {'clients_in_waiting': clients_in_waiting}, broadcast=True)

    # Check if the waiting room contains enough players.
    if len(clients_in_waiting) > 1:
        # Create a new room where both clients are joined.
        for client in clients_in_waiting:
            if client != request.sid:
                other_player = client
                break

        global game_number
        game_number += 1
        create_game(request.sid, other_player, game_number)
        clients_in_waiting.remove(request.sid)
        clients_in_waiting.remove(other_player)
        emit('redirect', {'url': url_for('game')}, request.sid)
        emit('redirect', {'url': url_for('game')}, other_player)


if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', debug=True)
