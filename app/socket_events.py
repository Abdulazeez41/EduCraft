from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_login import current_user
from . import socketio

@socketio.on('connect')
def handle_connect():
    if current_user.is_authenticated:
        emit('message', {'msg': f'{current_user.username} has connected.'}, broadcast=True)
    else:
        emit('message', {'msg': 'A user has connected.'}, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    if current_user.is_authenticated:
        emit('message', {'msg': f'{current_user.username} has disconnected.'}, broadcast=True)
    else:
        emit('message', {'msg': 'A user has disconnected.'}, broadcast=True)

@socketio.on('send_message')
def handle_message(data):
    message = data.get('message')
    if current_user.is_authenticated:
        emit('message', {'user': current_user.username, 'msg': message}, broadcast=True)

@socketio.on('join_room')
def handle_join_room(data):
    room = data.get('room')
    join_room(room)
    emit('message', {'msg': f'{current_user.username} joined room {room}'}, room=room)

@socketio.on('leave_room')
def handle_leave_room(data):
    room = data.get('room')
    leave_room(room)
    emit('message', {'msg': f'{current_user.username} left room {room}'}, room=room)
