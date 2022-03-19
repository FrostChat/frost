import sqlite3
import hashlib
import base64
import json
import datetime
import random
import string

class InvalidPassword(Exception): pass
class InvalidUsername(Exception): pass
class UserExists(Exception): pass
class UserNotFound(Exception): pass
class UserMuted(Exception): pass
class UserNotMuted(Exception): pass
class UserBlocked(Exception): pass
class UserNotBlocked(Exception): pass
class MessageNotFound(Exception): pass
class EmptyMessage(Exception): pass
class InvalidBio(Exception): pass

class User:
    def __init__(self, username: str, id: str, api_key: str, avatar_url: str, bio: str, website: str, hash: str = "") -> None:
        self.username = username
        self.id = id
        self.api_key = api_key
        self.avatar_url = avatar_url
        self.bio = bio
        self.website = website
        self.hash = hash
        self.is_muted = False
        self.is_blocked = False
        self.is_friend = False

        self.bio = self.bio.replace("\n", "{newline}")

    @classmethod
    def from_kwargs(cls, **kwargs):
        username = kwargs.get('username')
        id = kwargs.get('id')
        api_key = kwargs.get('api_key')
        avatar_url = kwargs.get('avatar_url')
        bio = kwargs.get('bio')
        website = kwargs.get('website')

        return cls(username, id, api_key, avatar_url, bio, website)

    def __str__(self) -> str:
        return f"{self.username} ({self.id})"

    def to_json(self, show_api_key=False, show_hash=False) -> dict:
        return {
            "username": self.username,
            "id": self.id,
            "avatar_url": self.avatar_url,
            "bio": self.bio,
            "website": self.website,
            "is_muted": self.is_muted,
            "is_blocked": self.is_blocked,
            "is_friend": self.is_friend,
            "api_key": self.api_key if show_api_key else "",
            "hash": self.hash if show_hash else ""
        }

class Message:
    def __init__(self, id: str, content: str, author_id: str, receiver_id: str, timestamp: str) -> None:
        self.id = id
        self.content = content
        self.author_id = author_id
        self.receiver_id = receiver_id
        self.timestamp = timestamp

        # self.content = json.dumps(self.content)
        # if self.content[0] == '"' and self.content[-1] == '"':
        #     self.content = self.content[1:-1]

        self.content = self.content.replace('"', '')
        self.content = self.content.replace("'", "")
        self.content = self.content.replace("\\", "")
        self.content = self.content.replace("\n", "{newline}")

    def __str__(self) -> str:
        return f"{self.content} ({self.timestamp})"

    def to_json(self) -> dict:
        return {"id": f"{self.id}", "content": self.content, "author_id": f"{self.author_id}", "receiver_id": f"{self.receiver_id}", "timestamp": f"{self.timestamp}"}

class Database:
    def __init__(self) -> None:
        self.database = sqlite3.connect('data/sqlite.db')

        self.database.execute('CREATE TABLE IF NOT EXISTS users (username TEXT, hash TEXT, id TEXT, api_key TEXT, avatar_url TEXT, bio TEXT, website TEXT)')
        self.database.execute('CREATE TABLE IF NOT EXISTS messages (id TEXT, content TEXT, author_id TEXT, receiver_id TEXT, timestamp TEXT)')
        self.database.execute('CREATE TABLE IF NOT EXISTS muted_users (user_id TEXT, muted_user_id TEXT)')
        self.database.execute('CREATE TABLE IF NOT EXISTS blocked_users (user_id TEXT, blocked_user_id TEXT)')
        self.database.execute('CREATE TABLE IF NOT EXISTS friends (user_id TEXT, friend_id TEXT)')

    def close(self) -> None:
        self.database.close()

    @staticmethod
    def valid_string(string: str) -> bool:
        """Check if a string contains only valid characters."""

        characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'
        for char in string:
            if char not in characters:
                return False
        return True

    @staticmethod
    def get_user_id(username: str) -> str:
        """Get a user_id from a username."""

        return base64.b64encode(username.encode('utf-8')).decode('utf-8')

    @staticmethod
    def get_message_id(timestamp: str, author_id: str) -> str:
        """Get a message_id from a timestamp."""

        json_obj = {'timestamp': timestamp, 'author_id': author_id}
        return base64.b64encode(json.dumps(json_obj).encode('utf-8')).decode('utf-8')

    @staticmethod
    def create_api_key(username: str) -> str:
        salt = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))
        user_id = Database.get_user_id(username)

        return user_id + "." + base64.b64encode(salt.encode('utf-8')).decode('utf-8')

    def mute_user(self, user_id: str, user_to_mute_id: str) -> None:
        """Mute a user."""

        if self.is_user_muted(user_id, user_to_mute_id):
            raise UserMuted("User is already muted.")

        self.database.execute('INSERT INTO muted_users (user_id, muted_user_id) VALUES (?, ?)', (user_id, user_to_mute_id))
        self.database.commit()

    def unmute_user(self, user_id: str, user_to_unmute_id: str) -> None:
        """Unmute a user."""

        if not self.is_user_muted(user_id, user_to_unmute_id):
            raise UserNotMuted("User is not muted.")

        self.database.execute('DELETE FROM muted_users WHERE user_id = ? AND muted_user_id = ?', (user_id, user_to_unmute_id))
        self.database.commit()

    def set_user_muted(self, user_id: str, user_to_mute_id: str, muted: bool) -> None:
        """Set a user's muted status."""

        if muted:
            self.mute_user(user_id, user_to_mute_id)
        else:
            self.unmute_user(user_id, user_to_mute_id)

    def is_user_muted(self, user_id: str, muted_user_id: str) -> bool:
        """Check if a user is muted."""

        is_muted = self.database.execute('SELECT * FROM muted_users WHERE user_id = ? AND muted_user_id = ?', (user_id, muted_user_id)).fetchone()
        return True if is_muted else False

    def block_user(self, user_id: str, user_to_block_id: str) -> None:
        """Block a user."""

        if self.is_user_blocked(user_id, user_to_block_id):
            raise UserBlocked("User is already blocked.")

        self.database.execute('INSERT INTO blocked_users (user_id, blocked_user_id) VALUES (?, ?)', (user_id, user_to_block_id))
        self.database.commit()

    def unblock_user(self, user_id: str, user_to_unblock_id: str) -> None:
        """Unblock a user."""

        if not self.is_user_blocked(user_id, user_to_unblock_id):
            raise UserNotBlocked("User is not blocked.")

        self.database.execute('DELETE FROM blocked_users WHERE user_id = ? AND blocked_user_id = ?', (user_id, user_to_unblock_id))
        self.database.commit()

    def set_user_blocked(self, user_id: str, user_to_block_id: str, blocked: bool) -> None:
        """Set a user's blocked status."""

        if blocked:
            self.block_user(user_id, user_to_block_id)
        else:
            self.unblock_user(user_id, user_to_block_id)

    def is_user_blocked(self, user_id: str, blocked_user_id: str) -> bool:
        """Check if a user is blocked."""

        is_blocked = self.database.execute('SELECT * FROM blocked_users WHERE user_id = ? AND blocked_user_id = ?', (user_id, blocked_user_id)).fetchone()
        return True if is_blocked else False

    def add_user(self, username: str, password: str, avatar_url: str = "https://upload.wikimedia.org/wikipedia/commons/7/7c/Profile_avatar_placeholder_large.png", bio: str = "", website: str = "") -> User:
        """Adds a user to the database."""

        if username in self.get_all_usernames():
            raise UserExists("User already exists.")

        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        user_id = self.get_user_id(username)
        api_key = self.create_api_key(username)

        if not self.valid_string(username):
            raise InvalidUsername('Username contains invalid characters.')

        if len(username) < 3:
            raise InvalidUsername('Username is too short.')

        self.database.execute('INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)', (username, hashed_password, user_id, api_key, avatar_url, bio, website))
        self.database.commit()

        return User(username, user_id, api_key, avatar_url, bio, website)

    def change_user_username(self, new_username: str, user_id: str) -> None:
        """Update the username of the user."""

        if new_username in self.get_all_usernames():
            raise UserExists("User already exists.")

        if not self.valid_string(new_username):
            raise InvalidUsername('Username contains invalid characters.')

        if len(new_username) < 3:
            raise InvalidUsername('Username is too short.')

        new_user_id = self.get_user_id(new_username)
        new_api_key = self.create_api_key(new_username)

        self.database.execute('UPDATE users SET username = ?, id = ?, api_key = ? WHERE id = ?', (new_username, new_user_id, new_api_key, user_id))
        self.database.commit()

    def change_user_password(self, password: str, user_id: str) -> None:
        """Update the password of the user."""

        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        self.database.execute('UPDATE users SET hash = ? WHERE id = ?', (hashed_password, user_id))
        self.database.commit()

    def change_user_avatar_url(self, avatar_url: str, user_id: str) -> None:
        """Update the avatar_url of the user."""

        self.database.execute('UPDATE users SET avatar_url = ? WHERE id = ?', (avatar_url, user_id))
        self.database.commit()

    def change_user_bio(self, bio: str, user_id: str) -> None:
        """Update the bio of the user."""

        # make sure the bio is not longer than 200 characters
        if len(bio) > 200:
            raise InvalidBio("Bio is too long.")

        self.database.execute('UPDATE users SET bio = ? WHERE id = ?', (bio, user_id))
        self.database.commit()

    def change_user_website(self, website: str, user_id: str) -> None:
        """Update the website of the user."""

        self.database.execute('UPDATE users SET website = ? WHERE id = ?', (website, user_id))
        self.database.commit()

    def get_user_by_username(self, username: str) -> User:
        user_id = self.get_user_id(username)
        user = self.database.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()

        if user is None:
            raise UserNotFound("User not found.")

        return User(user[0], user[2], user[3], user[4], user[5], user[6], user[1])

    def get_user(self, user_id: str) -> User:
        user = self.database.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()

        if user is None:
            raise UserNotFound("User not found.")

        return User(user[0], user[2], user[3], user[4], user[5], user[6], user[1])

    def get_all_users(self) -> list:
        """Get all users."""

        users = self.database.execute('SELECT * FROM users').fetchall()

        if users is None:
            return []

        return [User(user[0], user[2], user[3], user[4], user[5], user[6]) for user in users]

    def get_all_usernames(self) -> list:
        """Get all usernames."""

        users = self.database.execute('SELECT username FROM users').fetchall()
        if users is None:
            return []

        return [user[0] for user in users]

    def get_all_user_ids(self) -> list:
        """Get all user_ids."""

        users = self.database.execute('SELECT id FROM users').fetchall()
        if users is None:
            return []

        return [user[0] for user in users]

    def get_users_chats(self, user_id: str) -> list:
        chats = []
        other_chats = []
        
        for message in self.get_all_messages():
            # only append if the user is the author or receiver and not already in the list
            # append a user object to the list

            if message.author_id == user_id:
                user_obj = self.get_user(message.receiver_id)
                if user_obj.username not in other_chats:
                    other_chats.append(user_obj.username)
                    chats.append(user_obj)
            elif message.receiver_id == user_id:
                user_obj = self.get_user(message.author_id)
                if user_obj.username not in other_chats:
                    other_chats.append(user_obj.username)
                    chats.append(user_obj)

        return chats

    def delete_user(self, user_id: str) -> None:
        """Delete a user from the database."""

        if self.get_user(user_id) is None:
            raise UserNotFound("User not found.")

        self.database.execute('DELETE FROM users WHERE id = ?', (user_id,))
        self.database.commit()

        self.delete_all_messages_from_user(user_id)

        for message in self.get_all_messages():
            if message.receiver_id == user_id:
                self.delete_message(message.message_id)

    def add_message(self, content: str, author_id: str, receiver_id: str, timestamp: str) -> Message:
        """Adds a message to the database."""

        if content == '' or content is None or content == ' ':
            raise EmptyMessage("Message is empty.")

        message_id = self.get_message_id(timestamp, author_id)
        
        self.database.execute('INSERT INTO messages (id, content, author_id, receiver_id, timestamp) VALUES (?, ?, ?, ?, ?)', (message_id, content, author_id, receiver_id, timestamp))
        self.database.commit()

        return Message(message_id, content, author_id, receiver_id, timestamp)

    def get_message(self, message_id: str) -> Message:
        """Get a message from its message_id."""

        message = self.database.execute('SELECT content, author_id, receiver_id, timestamp FROM messages WHERE id = ?', (message_id,)).fetchone()
        if message is None:
            return None

        return Message(message_id, message[0], message[1], message[2], message[3])

    def get_users_messages(self, user_id: str) -> list:
        """Get all messages from a user."""

        messages = self.database.execute('SELECT id, content, author_id, receiver_id, timestamp FROM messages WHERE author_id = ? OR receiver_id = ?', (user_id, user_id)).fetchall()
        if messages is None:
            return None

        return [Message(message[0], message[1], message[2], message[3], message[4]) for message in messages]

    def get_messages_between(self, user_id_1: str, user_id_2: str) -> list:
        """Get all messages between two users."""

        messages = self.database.execute('SELECT id, content, author_id, receiver_id, timestamp FROM messages WHERE (author_id = ? AND receiver_id = ?) OR (author_id = ? AND receiver_id = ?)', (user_id_1, user_id_2, user_id_2, user_id_1)).fetchall()
        if messages is None:
            return None

        return [Message(message[0], message[1], message[2], message[3], message[4]) for message in messages]

    def get_all_messages(self) -> list:
        """Get all messages."""

        messages = self.database.execute('SELECT id, content, author_id, receiver_id, timestamp FROM messages').fetchall()
        if messages is None:
            return None

        return [Message(message[0], message[1], message[2], message[3], message[4]) for message in messages]

    def edit_message(self, message_id: str, content: str) -> Message:
        """Edit a message."""

        self.database.execute('UPDATE messages SET content = ? WHERE id = ?', (content, message_id))
        self.database.commit()

        message = self.get_message(message_id)
        return message

    def delete_message(self, message_id: str) -> None:
        """Delete a message from the database."""

        if self.get_message(message_id) is None:
            raise MessageNotFound("Message not found.")

        self.database.execute('DELETE FROM messages WHERE id = ?', (message_id,))
        self.database.commit()

    def delete_all_messages_from_user(self, user_id: str) -> None:
        """Delete all messages from a user."""

        messages = self.get_users_messages(user_id)
        if messages is None:
            return None

        for message in messages:
            self.delete_message(message.id)

    def valid_api_key(self, api_key: str) -> bool:
        """Check if an api_key is valid."""

        return self.database.execute('SELECT api_key FROM users WHERE api_key = ?', (api_key,)).fetchone() is not None

    def api_key_to_user(self, api_key: str) -> User:
        """Get a user from an api_key."""
        _id = api_key.split(".")[0]

        return self.get_user(_id[0])