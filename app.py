from flask import Flask, render_template, request, session, url_for, redirect
from flask_session import Session
from flask_socketio import SocketIO, join_room, emit, leave_room

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'some_secret'
app.config['SESSION_TYPE'] = 'filesystem'

Session(app)

socket = SocketIO(app, manage_session=False)


CONNECTED_USERS = []


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        username = request.form['username']
        session['username'] = username
        CONNECTED_USERS.append(session.get('username'))
        return render_template('chat.html', session=session, users=CONNECTED_USERS)
    else:
        if session.get( 'username' ) is not None:
            return render_template('chat.html', session=session, users=CONNECTED_USERS)
        else:
            return redirect(url_for('index'))


@socket.on('join')
def join(message):
    join_room("chat")
    emit('status', {'msg': session.get('username') + ' est arrivé.'}, room="chat")


@socket.on('text')
def text(message):
    print(message)
    emit('message', {'msg': session.get('username') + ': ' + message['msg']}, room="chat")


@socket.on('left')
def left(message):
    print("leaving")
    CONNECTED_USERS.remove(session.get('username'))
    emit('status', {'msg': session.get('username') + ' est parti.'}, room="chat")
    leave_room("chat")
    session.clear()


if __name__ == '__main__':
    socket.run(app, port=3000)