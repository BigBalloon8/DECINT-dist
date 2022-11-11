import node
import time
from requests import get
import pickle
#import blockchain


def read(queue):
    #time.sleep(60)
    print("---READER STARTED---")
    while True:
        #NODE_Lines = node.request_reader("NODE")
        if not queue.empty():
            #print(f"NODE LINES: {NODE_Lines}\n")
            message = queue.get()
            message = message.split(" ")

            if message[1] == "HELLO":
                node.new_node(float(message[2]), message[0], message[3], int(message[4]), float(message[5]), message[6], message[7])

            elif message[1] == "UPDATE":
                node.update_node(message[0], float(message[2]), message[3], int(message[4]), float(message[5]), message[6])

            elif message[1] == "DELETE":
                node.delete_node(float(message[2]), message[0], message[3], message[4])

            elif message[1] == "ERROR":  # TODO add raise error with type
                print("ERROR")
                print(message[2])
                continue

            elif message[1] == "GET_NODES":
                node.send_node(message[0])

            else:
                pass



if __name__ == "__main__":
    read()
