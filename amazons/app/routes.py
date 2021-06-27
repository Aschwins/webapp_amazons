import time

from flask import request, make_response, flash
from flask import render_template, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
from flask_login import current_user, login_user, logout_user, login_required

from util import configure_loggers
from forms import LoginForm, RegistrationForm

from app import app, db, socketio, migrate
from app.models import User, Game, Player, Move

from werkzeug.urls import url_parse

logger = configure_loggers()

# Configure App

async_mode = None
thread = None

# Set Global Variables
clients_in_waiting = []


def pair_clients_in_waiting(clients):
    """Client get paired via FIFO, First In First Out"""
    new_waiting_room = clients
    # p1, p2 = random.choices(new_waiting_room, 2, replace=False)
    p1, p2 = new_waiting_room[0], new_waiting_room[1]
    new_waiting_room.remove(p1)
    new_waiting_room.remove(p2)
    return new_waiting_room, tuple([p1, p2])


def create_game(user1, user2):
    """
    Function that pairs two players from the waiting room to a amazons game.

    Make entry in Game Model with player1 and player2 and game
    """
    user1 = User.query.get(user1[0])
    user2 = User.query.get(user2[0])

    game = Game(user_started_id=user1.id)
    db.session.add(game)
    db.session.commit()

    for user in [user1, user2]:
        socketio.emit('join_game', {'uid': user.id, 'game_id': game.id, 'turn': user1.id}, user.sid, namespace='/test')

    player1 = Player(user_id=user1.id, game_id=game.id)
    player2 = Player(user_id=user2.id, game_id=game.id)
    db.session.add_all([player1, player2])
    db.session.commit()
    socketio.emit('server_response', {'data': f"Created game #{str(game.id)}, between {user1} and {user2}"},
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

            create_game(paired[0], paired[1])



@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
@login_required
def index():
    logger.debug(f"Clients in waiting: {clients_in_waiting}")
    resp = make_response(render_template('index.html', waiting=clients_in_waiting))
    return resp


@app.route("/login", methods = ["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))


@login_required
@app.route("/dashboard")
def dashboard():
    return render_template('dashboard.html')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Registered user: {form.username.data}')
        return redirect(url_for('login'))
    return render_template("register.html", title='Register', form=form)


@login_required
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

    if current_user.is_authenticated:
        emit('server_response', {'data': f'Connected {request.sid, current_user.username}'}, broadcast=True)

        # Set socket_id for user whenever user connects.
        current_user.sid = request.sid
        db.session.commit()


@socketio.on('disconnect', namespace='/test')
def disconnect():
    emit('server_response', {'data': f'Disconnected {request.sid}'}, broadcast=True)
    if current_user.is_authenticated:
        logger.info(f"Client {current_user.sid} disconnected")


@socketio.on('join_room', namespace='/test')
def on_join(data):
    sid = request.sid  # request.sid
    game_id = data['game_id']
    emit('server_response', sid + ' has entered the room ' + str(game_id), room=str(game_id))
    emit('redirect', {'url': url_for('game')}, namespace='/test')


@socketio.on('join_waiting', namespace='/test')
def join_waiting():
    global clients_in_waiting
    current_user.sid = request.sid
    if (current_user.id, current_user.username) not in clients_in_waiting:
        clients_in_waiting.append((current_user.id, current_user.username))
        emit('update_waiting_room', {'clients_in_waiting': clients_in_waiting}, broadcast=True)
    else:
        return



@socketio.on('move', namespace='/test')
def move(data):
    logger.info(f"Recieved a move from a client {data}")
    logger.info(f"from client: {current_user.id}, {current_user.username}")
    game_id = int(data["game_id"])
    uid = current_user.id
    player = Player.query.filter_by(user_id=uid, game_id=game_id).first()

    # get move order
    last_move_in_game = Move.query.filter_by(game_id=game_id).order_by(Move.id.desc()).first()
    if last_move_in_game:
        move_order = last_move_in_game.move_order + 1
    else:
        move_order = 0

    # Log move in db
    m = Move(game_id=game_id, player_id=player.id, move_type=data["move_type"], move_order=move_order,
             from_position=str(data.get("from_position")), to_position=str(data["to_position"]))

    db.session.add(m)
    db.session.commit()

    # Now with the uid and game_id we can find his opponent, and his channel.
    players = Player.query.filter_by(game_id=int(game_id))
    for player in players:
        logger.info(f'Found player in gameid: {game_id}: {player.id}, {player.user_id}, {player.game_id}')

        if int(player.user_id) != int(uid):
            # found opponent
            opponent_uid = player.user_id
            opponent_sid = User.query.get(opponent_uid).sid

    logger.info(f"Sending game over state to opponent: {opponent_sid}")
    data["turn"] = opponent_uid
    emit('move', data, opponent_sid, namespace='/test')

@socketio.on('end', namespace='/test')
def end(data):
    logger.info(f"Game ended for player  {current_user.id}, {current_user.username}")
    logger.info(f"with status {data}")
    game_id = int(data["game_id"])
    uid = current_user.id
    player = Player.query.filter_by(user_id=uid, game_id=game_id).first()
    sid = User.query.get(uid).sid

    # Now with the uid and game_id we can find his opponent, and his channel.
    players = Player.query.filter_by(game_id=int(game_id))
    for player in players:
        logger.info(f'Found player in gameid: {game_id}: {player.id}, {player.user_id}, {player.game_id}')

        if int(player.user_id) != int(uid):
            # found opponent
            opponent_uid = player.user_id
            opponent_sid = User.query.get(opponent_uid).sid

    logger.info(f"Sending move to opponent: {opponent_sid}")
    data["turn"] = opponent_uid
    logger.info(f"Current user socket: {sid}")
    emit('end', data, sid, namespace='/test')
    emit('end', data, opponent_sid, namespace='/test')

@socketio.on("game_ready", namespace='/test')
def game_ready(data):
    """
    Whenever the game is ready we want to update the status with the right request.sids.
    """
    current_user.sid = request.sid
    db.session.commit()

    logger.info("Updated sid")
    logger.info(current_user.sid)


@app.route("/singleplayer")
def singleplayer():
    return render_template('singleplayer.html')



if __name__ == "__main__":
    db.create_all()
    socketio.run(app, host='0.0.0.0', debug=True)
