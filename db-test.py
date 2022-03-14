from utils.sqlite import Database, UserExists

db = Database()

# username = input("Username: ")
# password = input("Password: ")

# db.add_user(username, password)
# print("User added.")

jim = db.get_user_by_username("jim")
bob = db.get_user_by_username("bob")

try:
    db.mute_user(jim.id, bob.id)
except Exception as e:
    print(e)

print(db.is_user_muted(jim.id, bob.id))