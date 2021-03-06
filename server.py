import socket
from threading import Thread
import sys
import signal

MESSAGE_SIZE = 1024

sock = None
separator_token = "<SEP>"  # we will use this to separate the client name & message
client_sockets = None


def sigterm_handler(_signum, _frame) -> None:
    sys.exit(1)


def clean_up():
    global sock
    global client_sockets

    # close client sockets
    print("Clean up")
    if not (client_sockets is None):
        for cs in client_sockets:
            cs.close()

    # close server socket
    if not (sock is None):
        sock.close()


def listen_for_client(cs):
    """
    This function keep listening for a message from `cs` socket
    Whenever a message is received, broadcast it to all other connected clients
    """
    global separator_token
    global client_sockets

    while True:
        try:
            # keep listening for a message from `cs` socket
            msg = cs.recv(MESSAGE_SIZE).decode()
        except Exception as e:
            # client no longer connected
            # remove it from the set
            print(f"[!] Error: {e}")

            print(f"Remove a socket")
            client_sockets.remove(cs)
        else:
            # if we received a message, replace the <SEP>
            # token with ": " for nice printing
            msg = msg.replace(separator_token, ": ")

        # iterate over all connected sockets
        for client_socket in client_sockets:
            # and send the message
            client_socket.send(msg.encode())


def run_server():
    global sock
    global client_sockets

    # server's IP address
    SERVER_HOST = "0.0.0.0"
    SERVER_PORT = 5002  # port we want to use

    # initialize list/set of all connected client's sockets
    client_sockets = set()

    # create a TCP socket
    sock = socket.socket()

    # make the port as reusable port
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # bind the socket to the address we specified
    sock.bind((SERVER_HOST, SERVER_PORT))

    # listen for upcoming connections
    sock.listen(5)
    print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

    while True:
        print(f"Wait a connection")
        # we keep listening for new connections all the time
        client_socket, client_address = sock.accept()
        print(f"[+] {client_address} connected.")

        # add the new connected client to connected sockets
        client_sockets.add(client_socket)

        # start a new thread that listens for each client's messages
        thr = Thread(target=listen_for_client, args=(client_socket,))

        # make the thread daemon so it ends whenever the main thread ends
        thr.daemon = True

        # start the thread
        thr.start()


def main():
    # ???????????????????????????????????????????????????????????????????????????????????????
    signal.signal(signal.SIGTERM, sigterm_handler)

    try:
        run_server()
    finally:
        # ????????????????????????????????????????????????????????????????????????????????????????????????????????????
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        clean_up()
        # ???????????????????????????????????????????????????
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
        signal.signal(signal.SIGINT, signal.SIG_DFL)


# ???????????????????????????????????????????????????????????????????????????????????????
if __name__ == "__main__":
    sys.exit(main())
