import json

emojis = json.load(open("data/emojis.json"))
emoji_shortnames = []

for emoji in emojis["emojis"]:
    emoji_shortnames.append(emoji["shortname"])

def shortname_to_emoji(shortname):
    for emoji in emojis["emojis"]:
        if emoji["shortname"] == shortname:
            return emoji["emoji"]

    return shortname