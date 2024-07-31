# Spenxûr
**"His will is not his own — it's yours!"**

Spenxûr, much like his brother Xûr, has travelled across dimensions and countless worlds. Unlike his brother however, he chooses to deal in information instead of weapons. 
With Spenxûr in your Discord server, after running ```python3 main.py``` you can bend his will to your own (or just get him to remind you about that dentist appointment).

Do note that Spenxûr interacts with the Destiny 2 API and thus uses basic OAUTH to receive and send tokens in requests. This requires the existence of a ``.env`` folder in the directory in order for most of the vendor-related commands to work.

Please be aware that the first use of some vendor commands will also take longer as the current Destiny 2 manifest is pulled for the first time and any relevant JSON files are rendered.

# Command List

### ```--echo```
You can tell Spenxûr to relay and repeat any message of your choosing in any given Discord channel he has permission to send messages to. 

For --echo:\
```--echo "YYYY-MM-DD HH:MM" <#channel_id> your_message```\
**Note:** The time should be in PST. Future capabilities will include compatability with all time zones.

For --echodelay:\
```--echo your_delay_in_minutes <#channel_id> your_message```\
For --repeat_echo:\
```--repeat_echo duration_in_minutes interval_in_minutes <#channel_id> your_message```\

__For example:__\
For --echo:\
```--echo "1989-01-01 12:00" <#valid_channel_id> I am selling terrible loot in the Tower.```\
For --echodelay:\
```--echodelay 30 <#valid_channel_id> Send a reminder in 30 minutes.```\
For --repeat_echo:\
```--repeat_echo 60 15 <#valid_channel_id> Send a reminder every 15 minutes for an hour.```\

**Note: `channelid` is equivalent to a Discord channel mention.

__An Example:__
![image](https://github.com/TreeRacks/SpenXur/assets/47769935/ea94939b-1338-4c9b-bbc2-6ff06506cc82)


---

### ```--show```
Shows information about all the messages that the user has scheduled, such as its id, content, and time of arrival.

---

### ```--delete```
Deletes a message by its id. Users can only delete messages they themselves have scheduled (ie. messages that are visible when ```--show``` is called).

---

### ```--time```
Returns the current PST time. Currently the only time zone implemented, but will be improved to include all time zones in the future.

---

### ```--whereisxur```
Spenxûr's brother, Xûr, could be hiding anywhere in the solar system with *fantastic loot! You can find out the Destiny 2 NPC's location, wares, and deepest secrets with a single command. If Xûr has departed for the week, this command will instead tell you how long it will be until he returns.

**your mileage may vary*

---

### ```--whatisxur```
Gives a brief rundown of Xûr's entire stock. 

---

### ```--whatisbanshee```
Gives a brief rundown of Banshee-44's entire stock. Complete with traits, rolls, and masterworks.

---

### ```--whatiseververse```
Gives a brief rundown of relevant Eververse items on sale for Bright Dust, such as any ships, Legendary and Exotic ornaments, and emotes.

---

### ```--whereisminerva```
Spenxûr has travelled to the world of Fallout 76 and made acquaintaces with the travelling saleswoman Minerva! This command wil tell you where Minerva is located and how long she will remain there.

---

### ```--whatisminerva```
Gives a brief rundown of Minerva's entire stock, along with the price in gold bullion. Get ready to pay up!



