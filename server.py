#  coding: utf-8
import socketserver, os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):

    def handle(self):
        self.data = self.request.recv(1024).strip()
        method, url = requestParser(self.data)
        #self.request.sendall(bytearray("OK",'utf-8'))

        current_dir = os.path.abspath(os.getcwd())
        local_path = current_dir + '/www'

        # method can't handle
        if method != 'GET':
            self.request.sendall(bytearray("HTTP/1.1 405 Method Not Allowed\r\n\r\n405 Method Not Allowed",'utf-8'))
            return

        # if the url requested is a file
        elif os.path.isfile(local_path + url):
            self.sendOK(local_path, url, is_Dir = False)

        # if the url requested is a directory
        elif os.path.isdir(local_path + url):
            if url[-1] != '/': # the path is wrong
                address = self.server.server_address
                server_url = "http://" + address[0]+ ":" +str(address[1])
                location = server_url + url + "/"
                self.request.sendall(bytearray(f"HTTP/1.1 301 Moved Permanently\r\nLocation:{location}\r\n\r\n301 Moved Permanently",'utf-8'))
                return
            else:
                self.sendOK(local_path, url, is_Dir = True)

        # 404 not found
        else:
            self.request.sendall(bytearray(f"HTTP/1.1 404 Not Found\r\n\r\n404 Not Found",'utf-8'))
            return

    def sendOK(self, local_path, url, is_Dir):
        status = 'HTTP/1.1 200 OK\r\n'
        file_path = local_path + url

        if is_Dir: # return index.html from directories
            file_path += 'index.html'
            with open(file_path, 'r') as f:
                content = f.read()
            header = 'Content-Type: text/html\r\n'

        else:
            with open(file_path, 'r') as f:
                content = f.read()
            if 'css' in url.split('/')[-1]:
                header = 'Content-Type: text/css\r\n'
            elif 'html' in url.split('/')[-1]:
                header = 'Content-Type: text/html\r\n'
            else: # file type not supported
                self.request.sendall(bytearray(f"HTTP/1.1 404 Not Found\r\n\r\n404 Not Found",'utf-8'))
                return

        self.request.sendall(bytearray(f"{status}{header}\r\n{content}",'utf-8'))
        return

def requestParser(data):
    data_ = data.decode().splitlines()
    method, url, _ = data_[0].split(' ')
    return method, url

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
