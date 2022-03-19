from utils.sqlite import Database, UserExists

db = Database()

# username = input("Username: ")
# password = input("Password: ")

# db.add_user(username, password)
# user = db.get_user_by_username(username)

# print(user.to_json(show_api_key=True))

# jim = db.get_user_by_username("jim")
# bob = db.get_user_by_username("bob")

# try:
#     db.mute_user(jim.id, bob.id)
# except Exception as e:
#     print(e)

# print(db.is_user_muted(jim.id, bob.id))

print(db.get_user("YmVu.NlFnVG5iR3dub3oxN21DVQ=="))