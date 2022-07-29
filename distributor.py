import node
import pickle
import logging
import os

#send to all non dist nodes

def relay():
    do_not_send = ["NREQ","NODES?", "GET_NODES", "ONLINE?", "yh", "ERROR", "BLOCKCHAIN?", "BREQ"]
    logging.basicConfig(filename='relay.log',filemode='a', format='%(asctime)s  :  %(message)s', datefmt='%d-%b-%Y %H:%M:%S %p')  
    while True:
        with open(f"{os.path.dirname(__file__)}./info/relay_messages.txt", "w+") as file:
            messages = file.read().splitlines()
            file.write("")
        for message in messages:
            logging.info(message)
            for protocol in do_not_send:
                if protocol in message:
                    prot_in = True
            if prot_in:
                continue
            node.send_to_all_no_dist("DIST " + message)
            logging.info(message)

