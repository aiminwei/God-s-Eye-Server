# WsServer

## About

Listen for connections from Hololens client and communicate with EggShell server to execute commands and send back the results.

## Server Info
* **Server Platform**             : AWS
* **Server Public IP**            : 13.52.100.31
* **Server Port**                 : 5000
* **Accept Connections**          : 10 (For current use)

## Transport Protocol

This WsServer use WebSocket Protocol to build the connections between server and its clients.
Clients must be compatible with server using the same protocol.

## Functions

### macos
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

Victims Example:
```
{
    "status":       "Success",
    "content_type": "json",
    "content":      {}
}
```

| Key           |  Value                | Description |
| ----          |  ----                 | ----        |
|status         |"Success" or "Fail"    |Fail means server cannot handle request|
|content-type   |"json"                 |json → content-type: object|
|content        |Object                 |current Victim information|

#### Content Example:
    Key Explanation:
    victims         →  victims list
    total_victims   →  number of victims
    session_id      →  session_id of each victim
    victim_info     →  the host information about victim (include username, hostname and 
                       machine type)
    identified      →  whether this victim has been identified
    
```
{
     "status":       "Success",
     "content_type": "json",
     "content":
        {
            "victims": 
                [
                    {
                        "session_id":        1,
                        "ip_address": ["127.0.0.1", 49404],
                        "victim_info": 
                            {
                                "username": "aiminwei", 
                                "hostname": "Aimin\u7684MacBook Pro", 
                                "type":     "macos"
                            },
                        "identified":       true
                    }
                ],
            "total_victims": 1
        }
}
```
### Request Message

Required Format (example):
```
{
    "command":      "fetch",
    "victims_type": "identified victims",
    "content":      ""
}
```

|Key                |Value                                |Description|
|       ----        |       ----                          |----|
|command            |"fetch", "exit", "execution"         |client request for server to respond|
|victims_type       |"victims" or "identified victims"    |which victims set client request (for fetch command)|
|content            |Actual command to execution on victims machine   | only valid when it's execution command |


Execution Request Format (example):
```
For screen shot:
{
    "command":      "execution",
    "content": 
        {
            "session_id":   1,
            "action":       "screenshot",
            "para":         ""
        }
}
For taking picture:
{
    "command":      "execution",
    "content": 
        {
            "session_id":   1,
            "action":       "picture",
            "para":         ""
        }
}
For identify victim
{
    "command":      "execution",
    "content": 
        {
            "session_id":   1,
            "action":       "identify",
            "para":         ""
        }
}
```

#### Command Sets:

1. exit:            close the connection between client and server
2. fetch:           get the current victims' or identified victims' information (picture and profile json file)
3. execution:       execute command on victims' machine


#### Action Sets:
1. picture:        take a picture using victims' camera (session_id specifies which victim to perform)
2. screenshot:     get a screenshot of victim's machine (session_id specifies which victim to perform)
3. identify:       identify victim (session_id specifies which victim to perform)


### Response Format

Example:
```
Response for screenshot or picture
{
    "status":       "Success",
    "content_type": "text",
    "content":      "picture_1.jpg"
}

Response for identify command
{
    "status":       "Success",
    "content_type": "boolean",
    "content":      true
}
```

| Key           |  Value                | Description |
| ----          |  ----                 | ----        |
|status         |"Success" or "Fail"    |Fail means server cannot handle request|
|content_type   |"json" or "text"       |json → content: object, text → content: filename or filepath or error message|
|content        |"" or {}               |response content data|


Example for Fetch identified victims:
```
{
    "status":       "Success",
    "content_type": "json",
    "content": 
        {
            "identified_victims": 
                [
                    {
                        "session_id":     1,
                        "profile": 
                            {
                                "picture": "DB/Aimin/aimin_face.jpg", 
                                "name": "Aimin", 
                                "privacy": "DB/Aimin/profile_Aimin Wei.json"
                            }
                    }
                ],
            "total_identified_victims":   1
        }
    
}
```

Example Response of execution command:
```
{
    "status":       "Success",
    "content_type": "text",
    "content":      "screenshot_1586044054.jpg"
}
```

Resource Request from Server:

For the above information, like screen shots or pictures which are stored under
server DB/pictures folder, using nginx server to access this kinds of resources by using http request.
Profile infos are under certain file path which are notify in the result string.
    
Example:
1.  pictures or screen shots:
    "http://13.52.100.31/DB/pictures/screenshot_1586044054.jpg"
2.  profile_info:
    "http://13.52.100.31/DB/Aimin/aimin_face.jpg",
    "http://13.52.100.31/DB/Aimin/profile_Aimin Wei.json"



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
