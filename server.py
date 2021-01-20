from uuid import uuid4
import threading
import socket
import json
import re
import os

ALL_SOCKETS_IN_USE = 'All sockets are being used at the time please wait'  # Used when all there are 10 users logged

class Server(object):  # This is server class
    
    def __init__(self):
        """The constructor of the Server"""
        self.IP = '127.0.0.1'  # The IP of the server.
        self.PORT = 3001 # The chosen port to have the connection on
        self.thread_writing = -1  # Used to know if someone can read at the time + thread using
        self.thread_reading = -1  # Used to know if someone is reading at the time + thread using
        self.active_users = []  # This is a list containing hte threads that are active and if there are any open
        self.users_allowed = 10  # This is the amount of users that are allowed to be logged in at the same time
        self.sem = threading.Semaphore(self.users_allowed)  # users allowed is a variable making the program dynamic

        self.file_table = {"name": "", "sector_number": -1, "current": 0}   #file key entry for storage
        self.sector_table = {"sector_number": -1, "nodes": [], "data": ""}  #sector entry for storage
        self.open_file_table = []  #To keep track of opened files
        if not os.path.exists('storage.json'):  #initializing storage file
            self.drive = open("storage.json", "w+")
            self.storage_array = [{"files":[], "sectors":[]}]
            self.create_root()
            self.save()
            self.reset()
            self.open_file_table.append({"root": "w+"})
        else:
            self.drive = open("storage.json", "r+")
            self.storage_array = self.load()
            self.open_file_table.append({"root": "w+"})
            
    def save(self):
        """This function is used to write to the storage file"""
        self.drive.seek(0)
        json.dump(self.storage_array, self.drive)
        self.drive.close()

    def load(self):
        """This function is used to get data from the storage file"""
        self.drive.seek(0)
        data = json.load(self.drive)
        return data

    def reset(self):
        """This function is used to reset the file pointers and storage array after changes"""
        self.drive = open('storage.json', 'r+')
        self.storage_array = self.load()

    def uuid_str(self):
        """This function generates the sector numbers"""
        return str(uuid4())

    def create_entry(self, name, sector_number, current):
        """This function creates the entry which is to be written in the storage file"""
        self.file_table["name"] = name
        self.file_table["current"] = current
        self.file_table["sector_number"] = sector_number
        self.sector_table["sector_number"] = self.file_table["sector_number"]
        return [self.file_table, self.sector_table]

    def create_root(self):
        """This function is used to create the root directory as the initial state of the storage file"""
        to_write = self.create_entry("root", self.uuid_str(), 1)
        (self.storage_array[0]["files"]).append(to_write[0])
        (self.storage_array[0]["sectors"]).append(to_write[1])

    #file management operations
    def create_directory(self, dirName):
        """This function is used to create directory that can hold other files in it"""
        to_write = self.create_entry(dirName, self.uuid_str(), 0)
        (self.storage_array[0]["files"]).append(to_write[0])
        (self.storage_array[0]["sectors"]).append(to_write[1])
        for k in range(len(self.storage_array[0]["sectors"])):
            if (self.storage_array[0]["sectors"][k]["sector_number"] == self.storage_array[0]["files"][0]["sector_number"]):
                self.storage_array[0]["sectors"][k]["nodes"].append(to_write[0]["sector_number"])
        self.save()
        self.reset()
        return("Directory" + dirName + "is created successfully\n")

    def create_file(self, fname):
        """This function is used to create a file"""
        for k in range(len(self.storage_array[0]["files"])):
            if (self.storage_array[0]["files"][k]["name"] == fname):
                return('Error: File Already created')       
        to_write = self.create_entry(fname, self.uuid_str(), 0)
        (self.storage_array[0]["files"]).append(to_write[0])
        (self.storage_array[0]["sectors"]).append(to_write[1])	
        for k in range(len(self.storage_array[0]["sectors"])):
            if (self.storage_array[0]["sectors"][k]["sector_number"] == self.storage_array[0]["files"][0]["sector_number"]):
                self.storage_array[0]["sectors"][k]["nodes"].append(to_write[0]["sector_number"])
        self.save()
        self.reset()
        return("File" + fname + "is created successfully\n")

    def open_file(self, fname, mode):
        """This function is used to open a file in read or write mode"""   
        for k in range(len(self.storage_array[0]["files"])):
            if (self.storage_array[0]["files"][k]["name"] == fname):
                if (len(self.open_file_table) == 0):
                    self.open_file_table.append({fname : mode})
                    return ("File opened successfully\n")
                else:
                    for i in range(len(self.open_file_table)):
                        if (self.open_file_table[i] == {fname: mode}):
                            return("File already open\n")
                    self.open_file_table.append({fname: mode})
        if {fname: mode} not in self.open_file_table:
            return("Error: Cannot open file\n")

    def close_file(self, fname):
        """This function is used close the file entry from open file table"""
        for k in range(len(self.open_file_table)):
            if (fname in self.open_file_table[k]):
                del (self.open_file_table[k])
                return ("File closed successfully\n")

    def write_to_file(self,  client_socket, thread_num, fname, start_at=0, text=""):
        """This function is used to write data to the file"""
        if thread_num == self.thread_reading or self.thread_reading == -1:   # checking if open for read or reader is writer
            if {fname: 'w'} in self.open_file_table:
                for k in range(len(self.storage_array[0]["files"])):
                    if (self.storage_array[0]["files"][k]["name"] == fname):
                        if (self.storage_array[0]["files"][k]["sector_number"] == self.storage_array[0]["sectors"][k]["sector_number"]):
                            self.storage_array[0]["sectors"][k]["data"] += text
                            self.save()
                            self.reset()
                            return("The contents of the file are: \n" + self.storage_array[0]["sectors"][k]["data"] + "\n")
            else:
                return ("Error: File Not Opened\n")
        else:
            client_socket.send('Please wait someone is currently reading from the database'.encode())
            while self.thread_reading != -1:  # This basically waits until there isn't a thread reading
                continue
            return self.write_to_file(fname, client_socket, thread_num, 0, "")
        self.thread_writing = -1  # Changing now because there isn't someone writing anymore

    def read_from_file(self, fname, client_socket, thread_num):
        """This function is used to read data from a file"""
        if thread_num == self.thread_writing or self.thread_writing == -1:  # checking if open for read or reader is writer
            if {fname: 'r'} in self.open_file_table:
                for k in range(len(self.storage_array[0]["files"])):
                    if (self.storage_array[0]["files"][k]["name"] == fname):
                        if (self.storage_array[0]["files"][k]["sector_number"] == self.storage_array[0]["sectors"][k]["sector_number"]):
                            text = self.storage_array[0]["sectors"][k]["data"]
                            return("The contents of the file are: \n" + text + "\n")
            else:
                return ('Error: File not opened\n')
        else:
            client_socket.send('Please wait, someone is currently writing to the database'.encode())
            while self.thread_writing != -1:  # This basically waits until there is not a thread writing or adding
                continue
            return self.read_from_file(fname, client_socket, thread_num)

    def show_memory_map(self, client_socket, thread_num):
        """This function is used to show the memory map of the storage file"""
        return(self.storage_array[0]["files"][0]["name"] + ':\n' + ''.join(str(e) for e in self.storage_array[0]["sectors"][0]["nodes"]))

    def delete_file(self, fname, client_socket, thread_num):
        """This function is used to delete the file from the storage"""
        if thread_num == self.thread_reading or self.thread_reading == -1:   # checking if open for read or reader is writer
            if {fname: 'w'} in self.open_file_table:
                for k in range(len(self.storage_array[0]["files"])):
                    if (self.storage_array[0]["files"][k]["name"] == fname):
                        if (self.storage_array[0]["files"][k]["sector_number"] == self.storage_array[0]["sectors"][k]["sector_number"]):
                            self.storage_array[0]["sectors"][0]["nodes"].remove(self.storage_array[0]["files"][k]["sector_number"])
                            del(self.storage_array[0]["sectors"][k])
                            del (self.storage_array[0]["files"][k])
                            self.drive = open("storage.json", "w")
                            self.save()
                            self.reset()
                            return("File " + fname + " deleted successfully\n")
            else:
                return("Error: File Not Opened\n")
        else:
            client_socket.send('Please wait someone is currently reading from the database'.encode())
            while self.thread_reading != -1:  # This basically waits until there isn't a thread reading
                continue
            return self.delete_file(fname, client_socket, thread_num)
        self.thread_writing = -1  # Changing now because there isn't someone writing anymore

    def change_directory(self, fname):
        """This function is used to change the current working directory"""
        return("Function not implemented yet :(\n")

    def move(self, source, target):
        """This function is used to move a file or directory from source location to destination"""
        return("Function not implemented yet :(\n")

    def move_within_file(self, fname, fromPos, toPos, size, client_socket, thread_num):
        """This function is used to move data within the file"""
        if thread_num == self.thread_reading or self.thread_reading == -1:   # checking if open for read or reader is writer
            if {fname: 'w'} in self.open_file_table:
                for k in range(len(self.storage_array[0]["files"])):
                    if (self.storage_array[0]["files"][k]["name"] == fname):
                        if (self.storage_array[0]["files"][k]["sector_number"] == self.storage_array[0]["sectors"][k]["sector_number"]):                      
                            sub_string  = self.storage_array[0]["sectors"][k]["data"][int(fromPos):(int(fromPos) + int(size))]
                            first_part = self.storage_array[0]["sectors"][k]["data"][0:int(toPos)].replace(sub_string, '')
                            second_part = self.storage_array[0]["sectors"][k]["data"][int(toPos):].replace(sub_string, '')
                            self.storage_array[0]["sectors"][k]["data"] = first_part + sub_string + second_part
                            self.drive = open("storage.json", "w")
                            self.save()
                            self.reset()
                            return("The updated data in file is: \n" + self.storage_array[0]["sectors"][k]["data"] + "\n")
            else:
                return("Error: File Not Opened\n")
        else:
            client_socket.send('Please wait someone is currently reading from the database'.encode())
            while self.thread_reading != -1:  # This basically waits until there isn't a thread reading
                continue
            return self.move_within_file(fname, fromPos, toPos, size, client_socket, thread_num)
        self.thread_writing = -1  # Changing now because there isn't someone writing anymore

    def truncate_file(self, fname, maxSize, client_socket, thread_num):
        """This function is used to reduce the size of the file"""
        if thread_num == self.thread_reading or self.thread_reading == -1:   # checking if open for read or reader is writer
            if {fname: 'w'} in self.open_file_table:
                for k in range(len(self.storage_array[0]["files"])):
                    if (self.storage_array[0]["files"][k]["name"] == fname):
                        if (self.storage_array[0]["files"][k]["sector_number"] == self.storage_array[0]["sectors"][k]["sector_number"]):
                            self.storage_array[0]["sectors"][k]["data"] = self.storage_array[0]["sectors"][k]["data"][0:int(maxSize)]
                            self.drive = open("storage.json", "w")
                            self.save()
                            self.reset()
                            return("The updated data in file is: \n" + self.storage_array[0]["sectors"][k]["data"] + "\n")
            else:
                return("Error: File Not Opened\n")    
        else:
            client_socket.send('Please wait someone is currently reading from the database'.encode())
            while self.thread_reading != -1:  # This basically waits until there isn't a thread reading
                continue
            return self.truncate_file(fname, maxSize, client_socket, thread_num)
        self.thread_writing = -1  # Changing now because there isn't someone writing anymore

    def break_further_input(self, type_of_request, client_sock, thread_num):
        """This function is called to get the further input for the specific modes that need them. It 
        checks if what the user has entered is valid and does as requested or returns an error message."""
        request_fulfilled = False
        while not request_fulfilled:
            further_input = client_sock.recv(1024).decode()  # Getting the further input for the request
            self.thread_reading = thread_num  # So that writers can not access
            if type_of_request == 'create_file':
                client_sock.send(self.create_file(further_input).encode())
                request_fulfilled = True
            elif type_of_request == 'delete_file':
                client_sock.send(self.delete_file(further_input, client_sock, thread_num).encode())
                request_fulfilled = True
                self.thread_writing = -1  # No longer reading can free it up                
            elif type_of_request == 'make_directory':
                client_sock.send(self.create_directory(further_input).encode())
                request_fulfilled = True 
            elif type_of_request == 'change_directory':
                client_sock.send(self.change_directory(further_input).encode())
                request_fulfilled = True 
            elif type_of_request == 'move':
                if re.search('.*,.*', further_input):  # Checking if the user has entered the correct format key:value
                    sourceFileName, targetFileName = further_input.split(',')  # Now a list containing the key and the value
                    client_sock.send(self.move(sourceFileName, targetFileName).encode())
                    request_fulfilled = True
                else:
                    client_sock.send(('ERROR, please use this format for move: sourceFileName,targetFileName\r\n').encode())
            elif type_of_request == 'open_file':
                if re.search('.*,.*', further_input):  # Checking if the user has entered the correct format key:value
                    fileName, mode = further_input.split(',')  # Now a list containing the key and the value
                    self.open_file(fileName, mode)
                    client_sock.send("Opened".encode())
                    request_fulfilled = True
                else:
                    client_sock.send(('ERROR, please use this format for open file: fileName,mode\r\n').encode())
            elif type_of_request == 'close_file':
                client_sock.send(self.close_file(further_input).encode())
                request_fulfilled = True 
            elif type_of_request == 'write_to_file':
                if re.search('.*,.*,.*', further_input):  # Checking if the user has entered the correct format key:value
                    fileName, startAt, text = further_input.split(',')  # Now a list containing the key and the value
                    client_sock.send(self.write_to_file(client_sock, thread_num, fileName, startAt, text).encode())
                    request_fulfilled = True
                    self.thread_writing = -1  # No longer reading can free it up
                else:
                    client_sock.send(('ERROR, please use this format for write to file: fileName,startAt,text\r\n').encode())
            elif type_of_request == 'read_from_file':
                client_sock.send(self.read_from_file(further_input, client_sock, thread_num).encode())
                request_fulfilled = True
                self.thread_reading = -1  # No longer reading can free it up 
            elif type_of_request == 'move_within_file':
                if re.search('.*,.*,.*,.*', further_input):  # Checking if the user has entered the correct format key:value
                    fileName, fromPos, toPos, size = further_input.split(',')  # Now a list containing the key and the value
                    client_sock.send(self.move_within_file(fileName, fromPos, toPos, size, client_sock, thread_num).encode())
                    request_fulfilled = True
                    self.thread_writing = -1
                else:
                    client_sock.send(('ERROR, please use this format for move within file: fileName,from,to,size\r\n').encode()) 
            elif type_of_request == 'truncate_file':
                if re.search('.*,.*', further_input):  # Checking if the user has entered the correct format key:value
                    fileName, maxSize = further_input.split(',')  # Now a list containing the key and the value
                    client_sock.send(self.truncate_file(fileName, maxSize, client_sock, thread_num).encode())
                    request_fulfilled = True
                    self.thread_writing = -1  # No longer reading can free it up
                else:
                    client_sock.send(('ERROR, please use this format for truncate file: fileName,maxSize\r\n').encode())

    def receive_from_client(self, client_sock, thread_num):
        """This function receives the request from the client. It then classifies the user's request and does what he
        specified."""
        message = client_sock.recv(1024).decode()  # Receive the data from the user
        while 'quit' != message:
            print('Thread number: ' + str(thread_num) + ', asked to: ' + message + '\r\n')
            if 'create_file' == message:
                self.break_further_input(message, client_sock, thread_num)
            elif 'delete_file' == message:
                self.break_further_input(message, client_sock, thread_num)
            elif 'make_directory' == message:
                self.break_further_input(message, client_sock, thread_num)
            elif 'change_directory' == message:
                self.break_further_input(message, client_sock, thread_num)
            elif 'move' == message:
                self.break_further_input(message, client_sock, thread_num)
            elif 'open_file' == message:
                self.break_further_input(message, client_sock, thread_num)
            elif 'close_file' == message:
                self.break_further_input(message, client_sock, thread_num)
            elif 'write_to_file' == message:
                self.thread_writing = thread_num
                self.break_further_input(message, client_sock, thread_num)
            elif 'read_from_file' == message:
                self.thread_reading = thread_num
                self.break_further_input(message, client_sock, thread_num)
            elif 'move_within_file' == message:
                self.break_further_input(message, client_sock, thread_num)
            elif 'truncate_file' == message:
                self.break_further_input(message, client_sock, thread_num)
            elif 'show_memory_map' == message:
                client_sock.send(str(self.show_memory_map(client_sock, thread_num)).encode())
            message = client_sock.recv(1024).decode()  # Getting the new input
        if 'quit' == message:
            client_sock.send(('You have been successfully disconnected').encode())
            self.sem.release()  # Clearing up the user's used thread for new available clients
            self.active_users[thread_num-1] = 0  # -1 because indexes start at 0
            print ('User has been successfully disconnected ' + str(self.sem._value) + ' sockets left\r\n')
            return None

    def connect_client(self, client_sock):
        """This function knows how to handle many clients coming in, it let's a user know if all the sockets are full
        and he has to wait. It returns the thread number that it will be assigned later."""
        connection_available = True
        printed_once = False
        while connection_available:  # used so
            for user in range(self.users_allowed):
                if self.active_users[user] == 0:
                    self.active_users[user] = self.active_users.index(0) + 1
                    return self.active_users[user]  # We have found a number that can be assigned to the thread
            if not printed_once:  # If we have not send a reply to the user yet
                print (ALL_SOCKETS_IN_USE)
                client_sock.send((ALL_SOCKETS_IN_USE).encode())
                printed_once = True  # Now the user won't get the message anymore

    def handle_thread(self, client_sock, thread_num):
        """ This function handles the clients. Since only users_allowed (10 at the time), can be connected and send
        requests at a time. """
        # print("Welcome " + self.username[thread_num])
        print ('you are thread number: ' + str(thread_num))
        client_sock.send(('Connecting you to the server now!').encode())
        self.sem.acquire()  # Decreases the users logged in at the time (new thread opened)
        print ('New client connected to the database + ' + str(self.sem._value) + ' sockets left\r\n')
        self.receive_from_client(client_sock, thread_num)

    def zeroing_active_users_list(self):
        """This function adds the amount of sockets that are allowed (The value of user_allowed)
        It is set as zero (it means that there isn't someone using that socket, else if there is a number then
        it is in use"""
        for user in range(self.users_allowed):
            self.active_users.append(0)  # making all of the active users slot value, zero

    def start(self):
        """Another main function in the server side, It is mainly used to aceept new clients through creating sockets
        and then directing the code to assaign them their jobs to find."""
        try:
            # check_sockets_active(OPEN_SOCKETS)  # change if got time to make sure every number is ran
            print('Server starting up on ip %s port %s' % (self.IP, self.PORT))
            # Create a TCP/IP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind((self.IP, self.PORT))
            sock.listen(1)
            while True:
                print('\r\nWaiting for a new client')
                client_socket, client_address = sock.accept()  # Last step of being on a socket
                print('New client entered!')
                client_socket.sendall('Hello this is FAAM\'s server'.encode())  # First connection message
                thread_number = self.connect_client(client_socket)
                thread = threading.Thread(target=self.handle_thread, args=(client_socket, thread_number))
                thread.start()

        except socket.error as e:
            print(e)

if __name__ == '__main__':
    s = Server() 
    s.zeroing_active_users_list()  # Adding the amount of sockets that can be used with the database
    s.start()