import os
import node
import reciever
import reader
import pre_reader
import concurrent.futures
import socket
import distributor


"""
update tensorflow
update Blockchain and nodes
"""
def run():
    open(f"{os.path.dirname(__file__)}/recent_messages.txt", "w").close()#clear recent message file
    open(f"{os.path.dirname(__file__)}/relay_messages.txt", "w").close()
    local_ip = socket.gethostbyname(socket.gethostname())
    #os.system("pip3 install --upgrade ecdsa")

    """
    try:
        os.remove("install_decint.py")
        os.remove("install.exe")
    except:
        pass#wont work after first time ill come up with better way later
    """

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.submit(reciever.rec)#start recieving
        executor.submit(pre_reader.read)
        executor.submit(node.get_nodes).result()#update nodes
        executor.submit(reader.read)
        executor.submit(distributor.relay)














