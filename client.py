import socket
import random
from threading import Thread
from datetime import datetime
from colorama import Fore, init, Back
import sys
import signal

MESSAGE_SIZE = 1024

sock = None


def sigterm_handler(_signum, _frame) -> None:
    sys.exit(1)


def clean_up():
    global sock

    # close the socket
    sock.close()


def listen_for_messages():
    global sock

    while True:
        message = sock.recv(MESSAGE_SIZE).decode()
        print("\n" + message)


def run_server():
    global sock

    # init colors
    init()

    # set the available colors
    colors = [Fore.BLUE, Fore.CYAN, Fore.GREEN, Fore.LIGHTBLACK_EX,
              Fore.LIGHTBLUE_EX, Fore.LIGHTCYAN_EX, Fore.LIGHTGREEN_EX,
              Fore.LIGHTMAGENTA_EX, Fore.LIGHTRED_EX, Fore.LIGHTWHITE_EX,
              Fore.LIGHTYELLOW_EX, Fore.MAGENTA, Fore.RED, Fore.WHITE, Fore.YELLOW
              ]

    # choose a random color for the client
    client_color = random.choice(colors)

    # server's IP address
    # if the server is not on this machine,
    # put the private (network) IP address (e.g 192.168.1.2)
    SERVER_HOST = "127.0.0.1"
    SERVER_PORT = 5002  # server's port
    separator_token = "<SEP>"  # we will use this to separate the client name & message

    # initialize TCP socket
    sock = socket.socket()
    print(f"[*] Connecting to {SERVER_HOST}:{SERVER_PORT}...")
    # connect to the server
    sock.connect((SERVER_HOST, SERVER_PORT))
    print("[+] Connected.")

    # prompt the client for a name
    name = input("Enter your name: ")

    # make a thread that listens for messages to this client & print them
    thr = Thread(target=listen_for_messages)
    # make the thread daemon so it ends whenever the main thread ends
    thr.daemon = True
    # start the thread
    thr.start()

    while True:
        # input message we want to send to the server
        to_send = input()
        # a way to exit the program
        if to_send.lower() == 'q':
            break
        # add the datetime, name & the color of the sender
        date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        to_send = f"{client_color}[{date_now}] {name}{separator_token}{to_send}{Fore.RESET}"
        # finally, send the message
        sock.send(to_send.encode())


def main():
    # 強制終了のシグナルを受け取ったら、強制終了するようにします
    signal.signal(signal.SIGTERM, sigterm_handler)

    try:
        run_server()
    finally:
        # 強制終了のシグナルを無視するようにしてから、クリーンアップ処理へ進みます
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        clean_up()
        # 強制終了のシグナルを有効に戻します
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
        signal.signal(signal.SIGINT, signal.SIG_DFL)


# このファイルを直接実行したときは、以下の関数を呼び出します
if __name__ == "__main__":
    sys.exit(main())
