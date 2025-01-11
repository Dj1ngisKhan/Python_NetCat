import socket
import argparse
import textwrap
import time
import shlex
import subprocess
import threading


class netcat:
    def __init__(self, args):
        self.args = args
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def run(self):
        if self.args.server:
            self.databas()
        else:
            self.klient()

    def klient(self):
        sending = "random"
        self.socket.connect((self.args.target, self.args.port))
        while len(sending) > 0:
            sending = input("What command do you want to run on the target machine?").encode("utf-8")
            if sending.lower() == "exit":
                sending == ""
            self.socket.send(sending)

            try:

                message = self.socket.recv(1024).decode("utf-8")
                self.socket.settimeout(8)
                print("Sent from the server:", message)

            except Exception as e:
                print("Error occured when recieving message:")
                print(e)

    def databas(self):

        def trod(test):
            with test as soc:

                #soc.send(b"Working?")
                message = soc.recv(1024)
                message = message.decode("utf-8")
                print("Message from client:", message)
                try:
                    if (len(message.split) > 1):
                        message = shlex.split(message)
                except Exception:
                    pass

                cmd = subprocess.run(message, shell=True, text=True, capture_output=True)
                if cmd.returncode != 0:
                    print(f"Error occured when running the command {message} on target machine")
                    sys.exit()
                cmd_encode = cmd.stdout.encode("utf-8")
                soc.send(cmd_encode)
                if len(message) > 1:
                    trod(soc)

            self.socket.close()



        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)

        try:
            while True:
                client, addr = self.socket.accept()
                print(f"Client with ip-address: {addr[0]} is connected")
                thr = threading.Thread(target=trod, args=(client,))
                thr.start()

        except Exception as e:
            print("Error occured when accepting client socket:")
            print(e)


def start():
    epilog = textwrap.dedent('''
    Open Server: -c -t 0.0.0.0 -s -p 9998 \
    Open Client: -t 127.0.0.1 -p 9998 -c  \
    ''')

    pars = argparse.ArgumentParser(epilog=epilog, description="Testing netcat", formatter_class=argparse.RawDescriptionHelpFormatter)

    pars.add_argument("-s", "--server", help="Run as a server", action="store_true")
    pars.add_argument("-c", "--client", help="Run as a client", action="store_true")
    pars.add_argument("-t", "--target", help="Target machine to connect to", default="127.0.0.1", type=str)
    pars.add_argument("-p", "--port", help="Connection via this port", default=9998, type=int)
    # pars.add_argument("-c", "--command", help="The command you would like to execute", type=str)

    args = pars.parse_args()

    obj = netcat(args)
    obj.run()


if __name__ == "__main__":
    start()