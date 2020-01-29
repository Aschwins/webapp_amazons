## Run command
## FLASK_APP=src/amazons/app.py FLASK_ENV=development flask run
import os
import logging
import numpy as np
import time
import random
import uuid
import pandas as pd
from flask import Flask, jsonify, request, make_response
from flask import render_template, session, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_socketio import SocketIO, emit, join_room, leave_room, \
     close_room, rooms, disconnect

# Configure Logger
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.ERROR)

engineio_logger = logging.getLogger('engineio.server')
engineio_logger.setLevel(logging.ERROR)

app = Flask(__name__)
app.config["SECRET_KEY"] = "OCML3BRawWEUeaxcuKHLpw"
Bootstrap(app)

async_mode = None

socketio = SocketIO(app, async_mode='threading')

status = pd.DataFrame(columns=["uid", "sid", "connected", "in_waiting", "game_id"])

clients_in_waiting = []
game_number = 0
rooms = {}

thread = None


def pair_clients_in_waiting(clients):
    new_waiting_room = clients
    # p1, p2 = random.choices(new_waiting_room, 2, replace=False)
    p1, p2 = new_waiting_room[0], new_waiting_room[1]
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
    """
    Background thread which checks wether the waiting room has enough players to start a game.
    """
    count = 0

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
            socketio.emit(
                'update_waiting_room',
                {'clients_in_waiting': clients_in_waiting}, broadcast=True, namespace='/test')

            # create_game(paired[0], paired[1], count)
            socketio.emit('join_room',  {'uid': paired[0][1], 'game_id': count}, paired[0][0], namespace='/test')
            socketio.emit('join_room', {'uid': paired[1][1], 'game_id': count}, paired[1][0], namespace='/test')
            # update status
            global status
            status.loc[status["uid"] == paired[0][1], "in_waiting"] = False
            status.loc[status["uid"] == paired[1][1], "in_waiting"] = False
            status.loc[status["uid"] == paired[0][1], "game_id"] = str(count)
            status.loc[status["uid"] == paired[1][1], "game_id"] = str(count)

            socketio.emit('server_response', {'data': f"Created game #{str(count)}, between {paired[0]} and {paired[1]}"},
                 broadcast=True, namespace='/test')

            # global rooms
            # rooms[str(count)] = {'name': str(count), 'players': {paired[0], paired[1]}}
            # logger.info(f"ROOMS: {rooms}")


@app.route("/", methods=["GET", "POST"])
def index():
    resp = make_response(render_template('index.html'))
    uid = request.cookies.get('uid', None)
    global status
    if uid is None:
        uid = str(uuid.uuid4())
        resp.set_cookie('uid', uid)
        status = pd.concat([
            status,
            pd.DataFrame(
                {"uid": [uid], "sid": [None], "connected": [True], "in_waiting": [False], "game_id": [None]}
            )]
        )
    else:
        if uid in status["uid"].values:
            status.loc[status["uid"] == uid, 'connected'] = True
        else:
            status = pd.concat([
                status,
                pd.DataFrame(
                    {"uid": [uid], "sid": [None], "connected": [True], "in_waiting": [False], "game_id": [None]}
                )]
            )
    logger.info(status)
    return resp

@app.route("/game")
def game():
    return render_template('game.html')


@app.route("/cookie", methods=["GET", "POST"])
def cookie():
    return render_template("cookie.html")


@app.route("/setcookie", methods=["POST", "GET"])
def set_cookie():
    if request.method == "POST":
        user = request.form["nm"]
        resp = make_response(render_template("readcookie.html"))
        resp.set_cookie('userID', user)
        return resp


@app.route('/getcookie')
def get_cookie():
    cookies = request.cookies

    return f'<h1>Welcome {cookies}</h1>'


@socketio.on('connect', namespace='/test')
def connect():
    global status

    emit('server_response', {'data': f'Connected {request.sid}'}, broadcast=True)
    logger.info(f"LINKED: {request.sid} <-> {request.cookies.get('uid', None)}")

    # Because of document ready the cookie is there.
    uid = request.cookies.get('uid', None)
    status.loc[status["uid"] == uid, "sid"] = request.sid

    logger.info(status)

    global thread
    if thread is None:
        logger.info("Start Thread")
        thread = socketio.start_background_task(background_thread)


@socketio.on('disconnect', namespace='/test')
def disconnect():
    global status
    emit('server_response', {'data': f'Disconnected {request.sid}'}, broadcast=True)
    uid = request.cookies.get('uid')

    status.loc[status["uid"] == uid, "connected"] = False
    logger.info(f"Client {uid} disconnected")
    logger.info(status)


@socketio.on('join_room', namespace='/test')
def on_join(data):
    logger.info(f'data: {data}')
    sid = request.sid # request.sid
    game_id = data['game_id']
    join_room(str(game_id))
    emit('server_response', sid + ' has entered the room ' + str(game_id), room=str(game_id))
    emit('redirect', {'url': url_for('game')}, namespace='/test')


@socketio.on('join', namespace='/test')
def join(message):
    emit('server_response', {'data': f"Client {request.sid}/{request.cookies.get('uid')} joined waiting."}, broadcast=True)
    uid = request.cookies.get('uid')

    global status
    status.loc[status["uid"] == uid, 'sid'] = request.sid
    status.loc[status["uid"] == uid, 'in_waiting'] = True
    logger.info(status)

    clients_in_waiting.append((request.sid, request.cookies.get('uid')))
    logger.debug(f"CLIENTS IN WAITING: {clients_in_waiting}")
    emit('update_waiting_room', {'clients_in_waiting': clients_in_waiting}, broadcast=True)


@socketio.on('move', namespace='/test')
def move(data):
    logger.info(f"data: {data}")
    game_id = data["game_id"]
    uid = request.cookies.get('uid')

    sid = request.sid
    logger.info(sid)

    # Now with the uid and game_id we can find his opponent, and his channel.
    logger.info(status)

    opponent_sid = status.loc[(status['uid'] != uid) & (status["game_id"] == game_id), "sid"].values[0]
    logger.info(opponent_sid)
    emit('move', data["data"], opponent_sid, namespace='/test')

@socketio.on("game_ready", namespace='/test')
def game_ready(data):
    """
    Whenever the game is ready we want to update the status with the right request.sids.
    """
    global status
    uid = request.cookies.get('uid')
    new_sid = request.sid
    status.loc[status['uid'] == uid, 'sid'] = new_sid

    logger.debug("Updated sid")
    logger.debug(status)



if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', debug=True)
