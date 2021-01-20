# Synchronized_File_Management_System
## Multi-threaded Multi-client File Management System

### Design Description:
Synchronized file management system is implmented which includes file management operations. As this system is thread enabled hence the server can handle multiple clients at one time. A client class is created in the client.py file and the server class is created in the server.py file respectively. When the client is connected to the server it then asks the client for the mode of file operation required. The user enters the mode and then the working is handled using the functions. Multiple threads can attempt to read a file and some can request a write. While the file is being read no writer is allowed while the order of writes is maintained. Multiple users can read the file concurrently but writes will be mutually exclusive.

### File Management Operations:
  1. Open File
  2. Close File
  3. Write to File
  4. Read from File
  5. Truncate File
  6. Move Within File
  7. Show Memory Map
  8. Create File
  9. Create Directory
  10.Delete File
 
### Usage:
In order to run the code:
  • open command prompt.
  • Navigate to the folder containing the client.py and server.py files.
  • Type python3 server.py.
  • The server will start running and will wait for the client to connect and send request.
  • Then open new command prompt window.
  • Type python3 client.py.
  • The client will start running.
  • It will ask for further inputs via prompt messages and generate outputs accordingly.
