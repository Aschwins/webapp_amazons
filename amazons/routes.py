import time
import uuid
import pandas as pd

from flask import request, make_response, flash
from flask import render_template, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect

from util import configure_loggers
from forms import LoginForm

from amazons import app, db, socketio, migrate

logger = configure_loggers()

# Configure App

async_mode = None
thread = None

# Set Global Variables
status = pd.DataFrame(columns=["uid", "sid", "connected", "in_waiting", "game_id"])
clients_in_waiting = []
game_number = 0


def pair_clients_in_waiting(clients):
    """Client get paired via FIFO, First In First Out"""
    new_waiting_room = clients
    # p1, p2 = random.choices(new_waiting_room, 2, replace=False)
    p1, p2 = new_waiting_room[0], new_waiting_room[1]
    new_waiting_room.remove(p1)
    new_waiting_room.remove(p2)
    return new_waiting_room, tuple([p1, p2])


def create_game(user1, user2, game_id):
    """
    Function that pairs two players from the waiting room to a amazons game.
    """
    global status
    for user in [user1, user2]:
        socketio.emit('join_room', {'uid': user[1], 'game_id': game_id}, user[0], namespace='/test')
        status.loc[status["uid"] == user[1], "in_waiting"] = False
        status.loc[status["uid"] == user[1], "game_id"] = str(game_id)

    socketio.emit('server_response', {'data': f"Created game #{str(game_id)}, between {user1} and {user2}"},
                  broadcast=True, namespace='/test')


def background_thread():
    """
    Background thread which checks wether the waiting room has enough players to start a game.
    """
    count = 0

    while True:
        global clients_in_waiting
        time.sleep(5)
        count += 1

        # Check if there are enough players
        if len(clients_in_waiting) > 1:
            clients_in_waiting, paired = pair_clients_in_waiting(clients_in_waiting)
            socketio.emit('update_waiting_room',
                          {'clients_in_waiting': clients_in_waiting}, broadcast=True, namespace='/test')

            create_game(paired[0], paired[1], count)


@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
def index():
    resp = make_response(render_template('index.html'))
    uid = request.cookies.get('uid', None)
    global status
    if uid is None: # This is a first time user
        uid = str(uuid.uuid4())
        resp.set_cookie('uid', uid)
        status = pd.concat([
            status,
            pd.DataFrame(
                {"uid": [uid], "sid": [None], "connected": [True], "in_waiting": [False], "game_id": [None]}
            )]
        )
    else: # We've already seen this user.
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


@app.route("/login", methods = ["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash("Login requested for user {}, remember_me={}".format(form.username.data, form.remember_me.data))
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


@app.route("/game")
def game():
    return render_template('game.html')


@app.route('/getcookie')
def get_cookie():
    cookies = request.cookies

    return f'<h1>Welcome {cookies}</h1>'


@socketio.on('connect', namespace='/test')
def connect():
    global thread
    if thread is None:
        logger.info("Start Thread")
        thread = socketio.start_background_task(background_thread)

    emit('server_response', {'data': f'Connected {request.sid}'}, broadcast=True)

    uid = request.cookies.get('uid', None) # Because of document ready the cookie is there.
    global status
    status.loc[status["uid"] == uid, "sid"] = request.sid


@socketio.on('disconnect', namespace='/test')
def disconnect():
    global status
    emit('server_response', {'data': f'Disconnected {request.sid}'}, broadcast=True)
    uid = request.cookies.get('uid')

    status.loc[status["uid"] == uid, "connected"] = False
    logger.info(f"Client {uid} disconnected")


@socketio.on('join_room', namespace='/test')
def on_join(data):
    sid = request.sid  # request.sid
    game_id = data['game_id']
    emit('server_response', sid + ' has entered the room ' + str(game_id), room=str(game_id))
    emit('redirect', {'url': url_for('game')}, namespace='/test')


@socketio.on('join', namespace='/test')
def join(message):
    uid = request.cookies.get('uid')

    global status
    status.loc[status["uid"] == uid, 'sid'] = request.sid
    status.loc[status["uid"] == uid, 'in_waiting'] = True
    logger.info(f"Join: {status}")

    clients_in_waiting.append((request.sid, request.cookies.get('uid')))
    emit('update_waiting_room', {'clients_in_waiting': str(clients_in_waiting)}, broadcast=True)


@socketio.on('move', namespace='/test')
def move(data):
    game_id = data["game_id"]
    uid = request.cookies.get('uid')

    # Now with the uid and game_id we can find his opponent, and his channel.
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
    db.create_all()
    socketio.run(app, host='0.0.0.0', debug=True)
