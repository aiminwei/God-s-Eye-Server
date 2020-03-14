# [EggShell](http://lucasjackson.io/eggshell)



## About

EggShell is a post exploitation surveillance tool written in Python. It gives you a command line session with extra functionality between you and a target machine. EggShell gives you the power and convenience of uploading/downloading files, tab completion, taking pictures, location tracking, shell command execution, persistence, escalating privileges, password retrieval, and much more.  This is project is a proof of concept, intended for use on machines you own.

<img src="http://lucasjackson.io/images/eggshell/main-menu.png?3" alt="Main menu" width="500px;"/>

For detailed information and how-to visit http://lucasjackson.io/eggshell

Follow me on twitter: @neoneggplant

<hr style="height:1px; background:#9EA4A9">


## New In Version 3.0.0
 - More secure socket connection using SSL
 - Linux support
 - Tab completion
 - Improved over all structure and efficiency of session handling
 - Native iOS python support for 64 bit devices

<hr style="height:1px; background:#9EA4A9">


## Getting Started
- Requires python 2.7

### macOS/Linux Installation
```sh
git clone https://github.com/neoneggplant/eggshell
cd eggshell
python eggshell.py
```



## Creating Payloads
Eggshell payloads are executed on the target machine.  The payload first sends over instructions for getting and sending back device details to our server and then chooses the appropriate executable to establish a secure remote control session.

### bash
Selecting bash from the payload menu will give us a 1 liner that establishes an eggshell session upon execution on the target machine

<img src="http://lucasjackson.io/images/eggshell/bash-payload.png" alt="Bash payload" width="300px"/>



## Interacting with a session
<img src="http://lucasjackson.io/images/eggshell/session-interaction.png" alt="Session interaction" width="400"/>

After a session is established, we can execute commands on that device through the EggShell command line interface.
We can show all the available commands by typing "help"

<img src="http://lucasjackson.io/images/eggshell/help-command.png" alt="Command help" width="500px"/>


## Taking Pictures
<img src="http://lucasjackson.io/images/eggshell/macos-picture.png" alt="Session interaction" width="700px"/>

Both iOS and macOS payloads have picture taking capability. The picture command lets you take a picture from the iSight on macOS as well as the front or back camera on iOS.



### Tab Completion
Similar to most command line interfaces, EggShell supports tab completion.  When you start typing the path to a directory or filename, we can complete the rest of the path using the tab key.

<img src="http://lucasjackson.io/images/eggshell/tab-completion.png" alt="Tab completion" width="500px"/>

<hr style="height:1px; background:#9EA4A9">



## Multihandler
The Multihandler option lets us handle multiple sessions.  We can choose to interact with different devices while listening for new connections in the background.  

<img src="http://lucasjackson.io/images/eggshell/multihandler-start.png" alt="Drawing" width="450px;"/>

Similar to the session interface, we can type "help" to show Multihandler commands

<img src="http://lucasjackson.io/images/eggshell/multihandler-help.png" alt="Drawing" width="400"/>

<hr style="height:1px; background:#9EA4A9">


## DISCLAMER
By using EggShell, you agree to the GNU General Public License v2.0 included in the repository. For more details at http://www.gnu.org/licenses/gpl-2.0.html. Using EggShell for attacking targets without prior mutual consent is illegal. It is the end user's responsibility to obey all applicable local, state and federal laws. Developers assume no liability and are not responsible for any misuse or damage caused by this program.

<hr style="height:1px; background:#9EA4A9">



## Commands

#### macOS
* **brightness**     : adjust screen brightness
* **cd**             : change directory
* **download**       : download file
* **getfacebook**    : retrieve facebook session cookies
* **getpaste**       : get pasteboard contents
* **getvol**         : get speaker output volume
* **idletime**       : get the amount of time since the keyboard/cursor were touched
* **imessage**       : send message through the messages app
* **itunes**         : iTunes Controller
* **keyboard**       : your keyboard -> is target's keyboard
* **lazagne**        : firefox password retrieval | (https://github.com/AlessandroZ/LaZagne/wiki)
* **ls**             : list contents of a directory
* **mic**            : record mic
* **persistence**    : attempts to re establish connection after close
* **picture**        : take picture through iSight
* **pid**            : get process id
* **prompt**         : prompt user to type password
* **screenshot**     : take screenshot
* **setvol**         : set output volume
* **sleep**          : put device into sleep mode
* **su**             : su login
* **suspend**        : suspend current session (goes back to login screen)
* **upload**         : upload file



#WsServer


## About

Listen for connections from Hololens client and communicate with EggShell server to execute commands and return back the results.

## Server Info
* **Server Platform**             : AWS
* **Server Public IP**            : 13.52.100.31
* **Server Port**                 : 5000
* **Accept Connections**          : 10 (For current use)

## Transport Protocol

This WsServer use WebSocket Protocol to build the connections between server and its clients.
Clients must be compatible with server using the same protocol.

## Functions

###macos
* **screenshot**     : take screenshot
* **picture**        : take picture through iSight

## WorkFlow

1. Server start
    create eggshell thread to accept victim connection
    create WsServer to accept client (Hololens) to connect

2. Once server and client have built the connection
    server send push message to client

3. After server have sent the push message
    Loop Flow:
        client send request to server
        server send back response
        optional: when server gets any update, server may send push messages


## Message Format

### Push Message

Example:
```
{
    "id": "Success",
    "content-type": "json",
    "content": "{}"
}
```

| Key           |  Value                | Description |
| ----          |  ----                 | ----        |
|status         |"Success" or "Fail"    |Fail means server cannot handle request|
|content-type   |"json"                 |json→ content: object|
|content        |Object                 |current Victim information|

####content example:
    session_id: {"name": "", "picture": "", "privacy": ""}
    name     →  victim name
    picture  →  victim picture
    privacy  →  the detail info json file path on server
    
```
{
    1: {
        "name":     "Gagan",
        "picture":  "DB/Gagan/gagan_face.jpg",
        "privacy":  "DB/Gagan/profile_Gagan Vasudev.json"
    }
}
```
### Request Message

Example:
```
{
    "id": 1,
    "cmd": "picture",
    "para": ""
}
```

|Key                |Value                                |Description|
|       ----        |       ----                          |----|
|id                 |1,2,...                              |Session_id, which victim to execute the command|
|cmd                |"fetch", "picture", "screenshot"     |command to run|
|para               |""                                   |For now, no use|

#### Command Sets:

1. exit:           close the connection between client and server
2. fetch:          get the current victims information (picture and profile json file)  
3. picture:        take a picture using victims' camera (id specifies which victim to perform)
4. screenshot:     get a screenshot of victim's machine (id specifies which victim to perform)

### Response Format

Example:
```
{
    "status": "Success",
    "content-type": "file",
    "content": "picture_1.jpg"
}
```

| Key           |  Value                | Description |
| ----          |  ----                 | ----        |
|id             |"Success" or "Fail"    |Fail means server cannot handle request|
|content-type   |"json" or "file"       |json → content: object, file → content: file_path|
|content        |""                     |real content for communication|


