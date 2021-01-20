#importing files
import socket
import os

#starting and help text
FIRST_AND_HELP_MESSAGE= '\r\nHi, and welcome to FAAM\'s server database\r\n' \
                        'You can choose between many different requests from the database. Would you like to:\r\n' \
                        'To create a file - press c\r\n' \
                        'To delete a file - press d\r\n' \
                        'To make directory - press m\r\n' \
                        'To change directory - press h\r\n' \
                        'To move a file or directory - press o\r\n' \
                        'To open a file - press p\r\n' \
                        'To close a file - press l\r\n' \
                        'To write to a file - press w\r\n' \
                        'To read from file - press r\r\n' \
                        'To move within a file - press v\r\n' \
                        'To truncate a file - press t\r\n' \
                        'To show memory map - press s\r\n' \
                        'For help - press e\r\n' \
                        'Quit FAAM\'s database - press q\r\n'

def create_file(client, request):
    """This function is called when the user wants to create a new file"""
    request = 'create_file'
    client.send_to_server(request) #client is in create file mode
    further_input(client, request)
    return True

def delete_file(client, request):
    """This function is called when the user wants to delete a file"""
    request = 'delete_file'
    client.send_to_server(request)  #client is in delete file mode
    further_input(client, request)
    return True

def make_directory(client, request):
    """This function is called when the user wants to create a new directory"""
    request = 'make_directory'
    client.send_to_server(request)  #client is in make directory mode
    further_input(client, request)
    return True

def change_directory(client, request):
    """This function is called when the user wants to change current working directory"""
    request = 'change_directory'
    client.send_to_server(request)  #client is in change directory mode
    further_input(client, request)
    return True

def move(client, request):
    """This function is called when the user wants to move file or directory from one directory to another"""
    request = 'move'
    client.send_to_server(request)  #client is in move mode
    further_input(client, request)
    return True

def open_file(client, request):
    """This function is called when the user wants to open a file in read or write mode"""
    request = 'open_file'
    client.send_to_server(request)  #client is in open file mode
    further_input(client, request)
    return True

def close_file(client, request):
    """This function is called when the user wants to close a file"""
    request = 'close_file'
    client.send_to_server(request)  #client is in close file mode
    further_input(client, request)
    return True

def write_to_file(client, request):
    """This function is called when the user wants to write to some file opened in write mode"""
    request = 'write_to_file'
    client.send_to_server(request)  #client is in write to file mode
    further_input(client, request)
    return True

def read_from_file(client, request):
    """This function is called when the user wants to read from a file opened in read mode"""
    request = 'read_from_file'
    client.send_to_server(request)  #client is in read from file mode
    further_input(client, request)
    return True

def move_within_file(client, request):
    """This function is called when the user wants to move data within the file file"""
    request = 'move_within_file'
    client.send_to_server(request)  #client is in move within file mode
    further_input(client, request)
    return True

def truncate_file(client, request):
    """This function is called when the user wants to truncate file"""
    request = 'truncate_file'
    client.send_to_server(request)  #client is in truncate file mode
    further_input(client, request)
    return True

def show_memory_map(client, request):
    """This function is called when the user wants to show the memory map"""
    request = 'show_memory_map'
    client.send_to_server(request)  #client is in show memory map mode
    return True

def further_input(client, request):
    """This function is used when there is a need for further input, for example in write to file mode the filename, start at and text"""
    further_input_no_error = False
    while not further_input_no_error:
        if request == 'create_file' or request == 'delete_file' or request == 'close_file' or request == 'read_from_file':
            client.send_to_server(input("Please enter the request for file using this format: fileName\r\n"))
        elif request == 'make_directory' or request == 'change_directory':
            client.send_to_server(input("Please enter the request for directory using this format: directoryName\r\n"))
        elif request == 'move':
            client.send_to_server(input("Please enter the request for file using this format: sourceFileName,targetFileName\r\n"))
        elif request == 'open_file':
            client.send_to_server(input("Please enter the request for file using this format: fileName,mode\r\n"))
        elif request == 'write_to_file':
            client.send_to_server(input("Please enter the request for file using this format: fileName,startAt,text\r\n"))
        elif request == 'truncate_file':
            client.send_to_server(input("Please enter the request for file using this format: fileName,maxSize\r\n"))
        elif request == 'move_within_file':
            client.send_to_server(input("Please enter the request for file using this format: fileName,from,to,size\r\n"))
        server_output = client.get_server_output()
        while 'Please wait' in server_output:
            print (server_output)
            server_output = client.get_server_output()
        if 'ERROR' not in server_output:
            further_input_no_error = True
        print (server_output)


def quit_view_help(client, char_request):
    """This function is called when the user requested either quit view or help"""
    if char_request == 'e':  # The user has asked for help
        print (FIRST_AND_HELP_MESSAGE)  # The first message that is used which is also used as help.
    elif char_request == 'q':  # The user has requested to quit
        client.send_to_server('quit')
        print (client.get_server_output())
        os._exit(1)  # closing the client's program
    return True

USER_OPTIONS = {'c': create_file, 'd': delete_file, 'm': make_directory, 'h': change_directory,
                'o': move, 'p': open_file, 'l': close_file, 'w': write_to_file, 'r': read_from_file,
                'v': move_within_file, 't': truncate_file, 's': show_memory_map, 'e': quit_view_help,
                'q': quit_view_help}

class Client(object):  # This is the Client class

    def __init__(self):
        """The constructor of the Client"""
        self.IP = input("Enter the IP address of the FAAM server: ")  # The Ip of the server.
        if self.IP != '127.0.0.1':
            print("Error: Please enter the correct IP address")
            exit(1)
        self.PORT = 3001  # The port of the server.
        self.type = None  # At the start, the client has no type of request later it is 'add' or 'read'
        self.server_socket = None  # still need to connect

    def start(self):
        """This function binds a socket connection to the server and gets the jobs that server asks"""
        try:
            print('Trying to connect to IP %s PORT %s' % (self.IP, self.PORT))
            # Create a TCP/IP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.IP, self.PORT))
            self.server_socket = sock  # Now the Client's server value has the socket's reference
            server_connect_response = self.server_socket.recv(1024).decode()  # Getting the server's response to the 1st connection.
            while 'Connecting' not in server_connect_response:  # When we are connected the server sends message with the word connecting in it
                print (server_connect_response)
                server_connect_response = self.server_socket.recv(1024).decode()  # Waiting for the new response
            print (server_connect_response)  # This just let's the user know he is connected now
            self.get_user_request()
        except socket.error as e:
            print(e)
            self.server_socket.close()

    def get_user_request(self):
        """This function is used to ask user to select the mode"""
        username = input('Enter Username: ')
        print (FIRST_AND_HELP_MESSAGE)
        keep_asking = True
        while keep_asking:
            mode_char = input('Please enter the mode that you want: ')  # Here the user enters the mode he wants
            if mode_char in USER_OPTIONS.keys():
                keep_asking = USER_OPTIONS[mode_char](self, mode_char)
                # Calling the appropriate function based on the user's input
            else:
                print ('ERROR, you did not enter one of the supported modes. Modes available: c, d, m, h, o, p, l, w, r, v, t, s, e, q\r\n')

    def get_server_output(self):
        """This function returns the output of the server and checks if the server has sent the please wait
        message which is used to tell all of the sockets are full and the user has to wait."""
        server_output = self.server_socket.recv(1024).decode()
        printed_wait_once = False
        while 'Please wait' in server_output:  # The message the server sends if all of the connections are full
            if not printed_wait_once:
                print (server_output)
            server_output = self.server_socket.recv(1024).decode()  # Getting the output again
        return server_output

    def send_to_server(self, data_to_send):
        """This function just sends data to the server, it is used all over the client's code,
        it makes the code cleaner. Input: Just enter some data."""
        self.server_socket.send(data_to_send.encode())  # Sending the final user request to the server

if __name__ == '__main__':
    client = Client()  # Creating a client
    client.start()  # Using the client's start function
