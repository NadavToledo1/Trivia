import random
import socket
import threading
import time
from inputimeout import inputimeout, TimeoutOccurred
import sys

MAGIC_COOKIE = b'\xab\xcd\xdc\xba'
MESSAGE_TYPE_OFFER = b'\x02'


def print_colorful_text():
    colorful_text = """
*     *  \033[91m*******\033[0m  \033[92m*        \033[91m*******\033[0m   \033[93m*****\033[0m   *     *  \033[94m*******\033[0m
*  *  *  \033[91m*\033[0m        \033[92m*        \033[91m*\033[0m        \033[93m*\033[0m     \033[93m*\033[0m  **   **  \033[94m*\033[0m
*     *  \033[91m*\033[0m        \033[92m*        \033[91m*\033[0m        \033[93m*\033[0m     \033[93m*\033[0m  * * * *  \033[94m*\033[0m
* * * *  \033[91m*******\033[0m  \033[92m*        \033[91m*\033[0m        \033[93m*\033[0m     \033[93m*\033[0m  *  *  *  \033[94m*******\033[0m
*     *  \033[91m*\033[0m        \033[92m*        \033[91m*\033[0m        \033[93m*\033[0m     \033[93m*\033[0m  *     *  \033[94m*\033[0m
**   **  \033[91m*\033[0m        \033[92m*        \033[91m*\033[0m        \033[93m*\033[0m     \033[93m*\033[0m  *     *  \033[94m*\033[0m
*     *  \033[91m*******\033[0m  \033[92m*******\033[0m  \033[91m*******\033[0m   \033[93m*****\033[0m   *     *  \033[94m*******\033[0m
"""
    print(colorful_text)


def clear_last_line():
    # Move the cursor up one line and clear the line
    sys.stdout.write('\x1b[1A')  # Move cursor up one line
    sys.stdout.write('\x1b[2K')  # Clear the entire line


names = [
    "Snow White",
    "Cinderella",
    "Aurora",
    "Ariel",
    "Belle",
    "Jasmine",
    "Pocahontas",
    "Mulan",
    "Tiana",
    "Rapunzel",
    "Merida",
    "Elsa",
    "Anna",
    "Moana",

    "Prince Charming",
    "Prince Phillip",
    "Prince Eric",
    "Beast",
    "Aladdin",
    "John Smith",
    "Li Shang",
    "Naveen",
    "Flynn Rider",
    "Kristoff",
]
hostname = socket.gethostname()
ip = socket.gethostbyname(hostname)
UDP_PORT = 58800

nickname = random.choice(names)


# This function waits to receive offers from the server.
# as soon as received, initializes the TCP SOCKET and creates a THREAD for writing and reading
def listen_offers(flag):
    global stop
    if flag:
        print("Client started, listening for offer requests...")
        print_colorful_text()
        print(f"you are {nickname}, greetings {nickname}!")
    while True:
        try:
            stop = threading.Event()
            udp_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_client.bind(('', UDP_PORT))
            message, address = udp_client.recvfrom(1024)
            first_byte = message[0:4]
            if first_byte == MAGIC_COOKIE:
                # Check if the message type is offer
                if message[4:5] == MESSAGE_TYPE_OFFER:
                    # Extract server name (32 characters) and server port (2 bytes)
                    server_name = message[5:37].decode('utf-8').strip()
                    server_port = int.from_bytes(message[37:39], byteorder='big')
                    print(f'Received offer from server "{server_name}" at address {address}, attempting to connect...')
                    # Connect to the server using TCP
                    tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    tcp_client.connect((address[0], server_port))
                else:
                    print("Invalid message type. Expected offer.")
            else:
                pass
            udp_client.close()
            write_thread = threading.Thread(target=write, args=(tcp_client, stop,))
            receive_thread = threading.Thread(target=receive, args=(tcp_client, stop,))
            receive_thread.start()
            write_thread.start()
            receive_thread.join()  # Wait for the threads to finish
            write_thread.join()
            print("Server closed. Listening for offer requests...")
        except ConnectionRefusedError:
            print("Server closed. Listening for offer requests...")
            time.sleep(1)
            continue
        except ConnectionError:
            print('Connection to server lost. Reconnecting...')
            continue
        except KeyboardInterrupt:
            print("Keyboard interrupt detected. Exiting...")
            print("to play again press enter")
            stop.set()
            tcp_client.close()
        except Exception as e:
            print(f"Error: {e}")
            print("Server disconnected, listening for offer requests...")


# This function is responsible for receiving messages and printing them
def receive(client, stop):

    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if not message:
                print("server shut down, to search a new server press enter")
                stop.set()
                client.close()
                return
            if message == 'NICK':
                client.send(nickname.encode('utf-8'))
            else:
                print(message)
            if message.startswith('Game over!'):
                print("to play again press enter")
                stop.set()
                client.close()
                return
        except ConnectionError:
            print('Connection to server lost. Reconnecting...')
            return
        except socket.error as e:
            pass
        except KeyboardInterrupt:
            print("Keyboard interrupt detected. Exiting...")
            print("to play again press enter")
            stop.set()
            client.close()
            return
        except Exception as e:
            print(f"Error: {e}")
            print("Server disconnected, listening for offer requests...")
            return


# This function is responsible for writing messages and sending them
def write(client, stop):
    while True:
        if stop.is_set():
            return
        try:
            try:
                c = inputimeout(prompt='', timeout=10)
                # print(c)
            except TimeoutOccurred:
                # clear_last_line()
                c = None
            if c is not None:
                if not c.isascii():
                    print("bad input!")
                    pass
                else:
                    message = f'{nickname}:{c}'
                    client.send(message.encode('utf-8'))
        except ConnectionError:
            print('Connection to server lost. Reconnecting...')
            return
        except socket.error as e:
            pass
        except KeyboardInterrupt:
            print("Keyboard interrupt detected. Exiting...")
            return
        except Exception as e:
            return


listen_offers(True)
