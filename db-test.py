from utils.sqlite import Database, UserExists

db = Database()

username = input("Username: ")
password = input("Password: ")

db.add_user(username, password)
print("User added.")
