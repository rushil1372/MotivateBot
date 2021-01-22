# Bot works on concept of events 
import discord 

# For accessing token from .env file
import os 

# For https requests from api which returns json values 
import requests
import json  

# For choosing random messages from the list 
import random

from replit import db
from keep_alive import keep_alive


# Instance of client created 
client = discord.Client()

# List of sad words for scanning in messages 
sad_words = ["sad","unhappy","miserable","angry"]

# Words for output when sad_words encountered
# User can further add into list 
starter_encouragment = [
  "Cheer Up!",
  "Hang in there.",
  "You can get through it."
]

if "responding" not in db.keys():
  db["responding"] = True

def get_quote():
  response = requests.get("https://zenquotes.io/api/random")
  # Storing as json values
  json_data = json.loads(response.text)
  quote = json_data[0]['q'] + " -" + json_data[0]['a']
  return(quote) 

def update_encouragements(encouraging_message):
  if 'encouragments' in db.keys():
    encouragments = db["encouragments"]
    encouragments.append(encouraging_message)
    db["encouragments"] = encouragments
  else:
    db["encouragments"] = [encouraging_message]

def delete_encouragment(index):
  encouragments = db["encouragments"]
  if len(encouragments) > index:
    del encouragments[index]
  db["encouragments"] = encouragments

# Registering an event. Async works on callbacks 
@client.event  
async def on_ready():
  print("We have logged in as {0.user}".format(client))

# Registering event. Triggered when message is recieved  
@client.event 
async def on_message(message):
  if message.author == client.user:
    return 
  
  msg = message.content

  # Sending message to the channel 
  if msg.startswith('$inspire'):
    quote = get_quote()
    await message.channel.send(quote)

  if db["responding"]:
    options = starter_encouragment
    if "encouragments" in db.keys():
      options = options + db["encouragments"]

    # Checking for messages from the list
    if any(word in msg for word in sad_words):
      await message.channel.send(random.choice(options))

  # Checking for keyword and identifying message
  if msg.startswith("$new"):
    encouraging_message = msg.split("$new ",1)[1]
    update_encouragements(encouraging_message)
    await message.channel.send("Message added.")

  # For deleting message 
  if msg.startswith("$del"):
    encouragments = []
    if "encouragments" in db.keys():
      index = int(msg.split("$del",1)[1])
      delete_encouragment(index)
      encouragments = db["encouragments"]
    await message.channel.send(encouragments)

  if msg.startswith("$list"):
    encouragments = []
    if "encouragments" in db.keys():
      encouragments = db["encouragments"]
    await message.channel.send(encouragments)

  if msg.startswith("$responding"):
    value = msg.split("$responding ",1)[1]

    if value.lower() == "true":
      db["responding"] = True
      await message.channel.send("Responding is ON.")
    else:
      db["responding"] = False
      await message.channel.send("Responding is OFF.")

keep_alive()
client.run(os.getenv('TOKEN'))  
