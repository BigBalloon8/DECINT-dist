import node
import logging
import os
import asyncio
import traceback


# send to all non dist nodes

def relay():
    try:
        print("---RELAY STARTED---")
        dist_protocols = ["TRANS", "STAKE", "UNSTAKE"]
        logging.basicConfig(filename='relay.log', filemode='a', format='%(asctime)s  :  %(message)s', datefmt='%d-%b-%Y %H:%M:%S %p')
        while True:
            with open(f"{os.path.dirname(__file__)}/relay_messages.txt", "r") as file:
                messages = file.read().splitlines()
            open(f"{os.path.dirname(__file__)}/relay_messages.txt", "w").close()
            if messages:
                print("RELAY messages = ", messages)
                for message in messages:
                    if message.split(" ")[1] in dist_protocols and len(message.split(" ")) > 2: #greater than <ip> <message>
                        print(f"relaying {message}")
                        asyncio.run(node.send_to_all_no_dist("DIST " + message))
                        logging.info(message)
    except:
        while True:
            traceback.print_exc()
