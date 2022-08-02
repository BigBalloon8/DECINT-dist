import node
import logging
import os
import asyncio


# send to all non dist nodes

def relay():
    print("---RELAY STARTED---")
    do_not_send = ["NREQ", "NODES?", "GET_NODES", "ONLINE?", "yh", "ERROR", "BLOCKCHAIN?", "BREQ", "HELLO", "UPDATE", "DELETE"]
    logging.basicConfig(filename='relay.log', filemode='a', format='%(asctime)s  :  %(message)s', datefmt='%d-%b-%Y %H:%M:%S %p')
    while True:
        with open(f"{os.path.dirname(__file__)}./relay_messages.txt", "r") as file:
            messages = file.read().splitlines()
        open(f"{os.path.dirname(__file__)}./relay_messages.txt", "w").close()
        for message in messages:
            prot_in = False
            logging.info(message)
            for protocol in do_not_send:
                if protocol in message:
                    prot_in = True
            if prot_in:
                continue
            print(f"relaying {message}")
            asyncio.run(node.send_to_all_no_dist("DIST " + message))
            logging.info(message)
