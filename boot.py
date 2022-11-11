import os
import node
import reader
import concurrent.futures
import socket
import distributor
import multiprocessing
import threading


"""
update tensorflow
update Blockchain and nodes
"""
def run():
    open(f"{os.path.dirname(__file__)}/recent_messages.txt", "w").close()  # clear recent message file
    open(f"{os.path.dirname(__file__)}/relay_messages.txt", "w").close()

    req_queue = multiprocessing.Queue()
    message_queue = multiprocessing.Queue()
    relay_queue = multiprocessing.Queue()

    rec = multiprocessing.Process(target=node.receive, args=(req_queue, message_queue, relay_queue,))
    rec.start()

    up = threading.Thread(target=node.get_nodes, args=([], req_queue))
    up.start()
    up.join()
    req_queue.close()

    read = multiprocessing.Process(target=reader.read, args=(message_queue,))
    relay = multiprocessing.Process(target=distributor.relay, args=(relay_queue,))
    read.start()
    relay.start()




    # with concurrent.futures.ProcessPoolExecutor() as executor:
        # executor.submit(node.receive, req_queue, message_queue, relay_queue)  # start receiving
        # executor.submit(node.get_nodes, [], req_queue).result()  # update nodes
        # executor.submit(reader.read, message_queue)
        # executor.submit(distributor.relay, relay_queue)














