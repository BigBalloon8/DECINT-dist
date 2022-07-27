import node
import time
from requests import get
import pickle
#import blockchain


def read():
    time.sleep(60)
    print("---READER STARTED---")
    ip = get('https://api.ipify.org').text
    while True:
        NODE_Lines = node.request_reader("NODE")
        if NODE_Lines:
            print(f"NODE LINES: {NODE_Lines}\n")
            for message in NODE_Lines:
                message = message.split(" ")
                try:
                    node.message_handler(message)
                except Exception as e:
                    node.send(message[0], f"ERROR {e}")
                    print(message[1], e)
                    continue

                if message[1] == "HELLO":
                    print("HELLO")
                    node.new_node(float(message[2]), message[0], message[3], int(message[4]), float(message[5]), message[6], message[7])

                elif message[1] == "UPDATE":
                    print("UPDATE")
                    node.update_node(message[0], float(message[2]), message[3], int(message[4]), float(message[5]), message[6])

                elif message[1] == "DELETE":
                    print("DELETE")
                    node.delete_node(float(message[2]), message[0], message[3], message[4])

                else:
                    pass



if __name__ == "__main__":
    read()
