from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_jwt_extended import decode_token
from datetime import datetime
from models.message import MessageModel
from models.users import UserModel  # Ensure UserModel has a method to get user roles

socketio = SocketIO(cors_allowed_origins="*")

def init_socketio(app):
    """Initialize SocketIO with Flask app"""
    socketio.init_app(app)

def get_user_from_token(token):
    """Extracts user info from JWT token"""
    try:
        decoded_token = decode_token(token)
        return decoded_token["sub"]  # `sub` contains the user's email (as per auth_routes.py)
    except Exception:
        return None

@socketio.on("join")
def handle_join(data):
    """User joins a chat room"""
    user = data.get("user")
    room = data.get("room")
    join_room(room)
    emit("user_joined", {"user": user, "room": room}, room=room)

@socketio.on("leave")
def handle_leave(data):
    """User leaves a chat room"""
    user = data.get("user")
    room = data.get("room")
    leave_room(room)
    emit("user_left", {"user": user, "room": room}, room=room)

@socketio.on("send_message")
def handle_send_message(data):
    """Only logged-in users can send messages"""
    token = data.get("token")  # Token should be sent from frontend
    user_email = get_user_from_token(token)

    if not user_email:
        emit("error", {"message": "Unauthorized. Please log in."})
        return

    user = UserModel.find_by_email(user_email)  # Fetch user details
    if not user:
        emit("error", {"message": "User not found."})
        return

    message = data.get("message")
    room = data.get("room")
    timestamp = data.get("timestamp")  

    if timestamp:
        timestamp_dt = datetime.strptime(timestamp.replace("T", " ").replace("Z", ""), "%Y-%m-%d %H:%M:%S.%f")
        formatted_timestamp = timestamp_dt.strftime("%H:%M %d/%m/%Y")
    else:
        formatted_timestamp = "Không có thời gian"

    msg = MessageModel.save_message(user["username"], message, room)  # Use username from DB

    emit("new_message", {
        "message_id": str(msg["_id"]),
        "user": msg["user"],
        "message": msg["message"],
        "timestamp": formatted_timestamp
    }, room=room)

@socketio.on("delete_message")
def handle_delete_message(data):
    """Only admins can delete messages"""
    token = data.get("token")
    user_email = get_user_from_token(token)
    
    if not user_email:
        emit("error", {"message": "Unauthorized. Please log in."})
        return

    user = UserModel.find_by_email(user_email)
    if not user or user["role"] != "admin":
        emit("error", {"message": "Access denied. Only admins can delete messages."})
        return

    message_id = data.get("message_id")
    success = MessageModel.delete_message(message_id)

    if success:
        emit("message_deleted", {"message_id": message_id}, broadcast=True)
    else:
        emit("error", {"message": "Message not found or failed to delete."})
