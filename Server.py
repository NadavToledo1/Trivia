import socket
import time
import select
import random
import threading

hostname = socket.gethostname()
ip = socket.gethostbyname(hostname)
UDP_PORT = 58800

MAGIC_COOKIE = b'\xab\xcd\xdc\xba'
MESSAGE_TYPE_OFFER = b'\x02'
SERVER_NAME = "TransmitTower".ljust(32).encode('utf-8')


Questions = ["A hat trick in soccer refers to a player scoring three goals in a single game.",
             "The Olympic Games were held in ancient Rome.",
             "In basketball, a field goal is worth three points if the shooter is beyond the three-point line.",
             "The sport of curling originated in Scotland.",
             "Michael Phelps holds the record for the most Olympic gold medals in a single event.",
             "The Super Bowl is the most-watched television event in the United States.",
             "Tennis player Serena Williams has won more Grand Slam singles titles than her sister Venus Williams.",
             "Table tennis is an Olympic sport.",
             "The Tour de France is an annual cycling race that primarily takes place in Italy.",
             "The term birdie is used in golf to describe a score one stroke under par on a hole.",
             "Polo takes up the largest amount of space in terms of land area.",
             "Every golf ball has the same number of dimples.",
             "Football players started wearing helmets in 1943",
             "Brazil is the only nation to have played in every World Cup finals tournament.",
             "World-renowned jeweler Tiffany & Co. is the maker of the Vince Lombardi trophy",
             "There are 30 NFL teams.",
             "The New York Marathon is the largest in the world",
             "Three strikes in a row in bowling is called a chicken.",
             "An astronaut has played golf on the moon.",
             "The Tour de France always finishes in Italy.",
             "Soccer (football) is estimated to have more than 2 billion fans around the world.",
             "A golf ball is the fastest recorded object in sports.",
             "Soccer is also known as football in most countries outside of North America",
             "The Olympic Games are held every three years",
             "Michael Jordan played the majority of his basketball career with the Los Angeles Lakers",
             "Golf is played on an 18-hole course for professional tournaments",
             "The Super Bowl is the championship game of the National Basketball Association (NBA)",
             "A home run in baseball earns the batter four points",
             "Tennis scoring system includes points like 15, 30, and 40",
             "Usain Bolt holds the world record for the fastest marathon time",
             "The Tour de France is a multi-stage bicycle race",
             "Swimming is one of the four strokes in competitive individual medley events"
             ]
Answer = [["y", "t", "1"], ["n", "f", "0"], ["y", "t", "1"], ["y", "t", "1"],
          ["y", "t", "1"], ["y", "t", "1"], ["y", "t", "1"], ["y", "t", "1"],
          ["n", "f", "0"], ["y", "t", "1"],["y", "t", "1"],["n", "f", "0"],["y", "t", "1"],["y", "t", "1"],["y", "t", "1"],
          ["n", "f", "0"],["y", "t", "1"],["n", "f", "0"],["y", "t", "1"],["n", "f", "0"],["n", "f", "0"],["n", "f", "0"],["y", "t", "1"],["n", "f", "0"],["n", "f", "0"],
          ["y", "t", "1"],["n", "f", "0"],["n", "f", "0"],["y", "t", "1"],["n", "f", "0"],["y", "t", "1"],["y","t","1"]]

# Initialize UDP server
udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Set socket options to allow broadcast
udp_server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
# Get the local IP address and subnet mask
local_ip = socket.gethostbyname(hostname)
subnet_mask = "255.255.255.0"
# Create the broadcast address by bitwise ANDing the local IP with the subnet mask
broadcast_address = '.'.join(str(int(ip) | int(mask) ^ 255) for ip, mask in zip(local_ip.split('.'), subnet_mask.split('.')))


# Initialize TCP server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((ip, 0))
TCP_PORT = server.getsockname()[1]


# This function sends UDP offers to connect clients
def broadcast_offers():
    print("\033[91m" + "offer sent" + "\033[0m")
    message = MAGIC_COOKIE + MESSAGE_TYPE_OFFER + SERVER_NAME + TCP_PORT.to_bytes(2, byteorder='big')

    # Send the UDP message to the broadcast address
    udp_server.sendto(message, (broadcast_address, UDP_PORT))


# This function handles the clients connections before the game
def handle_game():
    try:
        clients = []
        nicknames = []
        timer = 0
        socket_list = [server]
        while timer < 10:
            broadcast_offers()
            readable, _, _ = select.select(socket_list, [], [], 1)
            if len(readable) == 0:
                timer += 1
            else:
                print("\033[94m" + "client added" + "\033[94m")
                for offer in readable:
                    if offer is server:
                        client, address = offer.accept()
                        client.send('NICK'.encode('utf-8'))
                        nickname = client.recv(1024).decode('utf-8')
                        nicknames.append(nickname)
                        clients.append(client)
                        print("\033[95m"+f"TransmitTower connected with {nickname} on {str(address)}\n"+"\033[95m")
                        broadcast(("\033[95m"+f"TransmitTower connected with {nickname} on {str(address)}\n"+"\033[95m").encode('utf-8'), clients)
                timer = 0
        if len(clients) > 0:
            run_game(clients, nicknames)
        else:
            print("\033[96m" + "no one connected in the time limit, searching again" + "\033[96m")
    except Exception as e:
        print(f"Error: {e}")
        print("Failed to connect. Listening for offer requests...")


# This function makes new game to run again every time after game ends
def handle_trivia():
    while True:
        handle_game()


# This function is responsible for running the game until a client wins
def run_game(clients, nicknames):
    try:
        time.sleep(1)
        asked = []
        broadcast(('Welcome to the TransmitTower server, where we are answering trivia questions about sport\n'.encode('utf-8')), clients)
        print('Welcome to the TransmitTower server, where we are answering trivia questions about sport\n')
        teams = ''
        for i in range(len(nicknames)):
            teams += f'player {i+1}: {nicknames[i]} \n'
        broadcast(("\033[92m"+teams+"\033[92m").encode('utf-8'), clients)
        print("\033[92m"+teams+"\033[92m")
        broadcast(("\033[92m"+f'==\n'+"\033[92m").encode('utf-8'), clients)
        print("\033[92m"+f'==\n'+"\033[92m")
        correct_answer = send_question(clients, asked)
        timer = 0
        socket_list = [server] + clients
        disqualified = []
        while timer < 10:
            if len(clients) == 0:
                print("no one here")
                return
            readable, _, _ = select.select(socket_list, [], [], 1)
            if len(readable) == 0:
                if len(disqualified) == len(clients) or timer == 9:
                    broadcast(("\033[93m"+"No correct answer. Choosing another question...\n"+"\033[93m").encode('utf-8'), clients)
                    print("\033[93m"+"No correct answer. Choosing another question...\n"+"\033[93m")
                    correct_answer = send_question(clients, asked)
                    disqualified = []
                    timer = 0
                else:
                    timer += 1
            else:
                for socket in readable:
                    if socket in clients and socket not in disqualified:
                        # Receive the answer from the client
                        message = socket.recv(1024)
                        broadcast(message, clients)
                        message = message.decode('utf-8')
                        print(message)
                        name = message.split(":")[0]
                        answer = message.split(":")[1]
                        if answer.lower() in correct_answer or answer == str(correct_answer[2]):
                            broadcast(("\033[95m"+f"{name} answered correctly! {name} wins!"+"\033[95m").encode('utf-8'), clients)
                            print("\033[95m"+f"{name} answered correctly! {name} wins!"+"\033[95m")
                            broadcast(("\033[96m"+f"Game over! Congratulations to the winner: {name}"+"\033[96m").encode('utf-8'), clients)
                            print("\033[96m"+f"Game over! Congratulations to the winner: {name}"+"\033[96m")
                            disconnect(clients, socket_list)
                            return
                        else:
                            broadcast(f'{name} is disqualified.\n'.encode('utf-8'), clients)
                            print(f'{name} is disqualified.\n')
                            disqualified.append(socket)
    except Exception as e:
        print("client disconnected, listening for offer requests...")
        return


# This function receives a message and all the clients and sends the message to all the clients
def broadcast(message, clients):
    for client in clients:
        client.send(message)


# This function sends a question to all the clients and returns the answer to the question
def send_question(clients, asked):
    while True:
        question_index = random.randint(0, len(Questions) - 1)
        if question_index in asked:
            pass
        else:
            asked.append(question_index)
            break
    question = Questions[question_index]
    correct_answer = Answer[question_index]

    broadcast(("\033[1;31m"+f"True or false:{question}"+"\033[1;31m").encode('utf-8'), clients)
    print("\033[1;31m"+f"True or false:{question}"+"\033[1;31m")
    return correct_answer


# This function is responsible for closing all the clients after the game is over
def disconnect(clients, socket_list):
    for client in clients:
        client.close()
    clients.clear()
    socket_list = [server]
    print("\033[1;4;33m"+"Game over, sending out offer requests..."+"\033[1;4;33m")
    return


server.listen()
print(f'Server started, listening on IP address {ip}\n')
handle_trivia()
