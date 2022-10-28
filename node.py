"""
node
"""
import socket
import random
import time
import ast
import blockchain
import time
from ecdsa import SigningKey, VerifyingKey, SECP112r2
import asyncio
import os
import json
from threading import Thread
import copy
import traceback


__version__ = "1.0"


# recieve from nodes
def receive():
    """
    message is split into array the first value the type of message the second value is the message
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("", 1379))
    server.listen()
    message_handle = MessageManager()
    while True:
        try:
            client, address = server.accept()
            message = client.recv(2 ** 16).decode("utf-8")  # .split(" ")
            if "\n" in message:
                continue
            print(f"Message from {address} , {message}\n")
            message_handle.write(address, message)
            continue
        except Exception as e:
            traceback.print_exc()


class TimeOutList(): #TODO test in working simulation
    def __init__(self):
        self.t_list = []
        self.times = []

    def timeout(self):
        removed = 0
        if len(self.t_list) == 0:
            return
        for i in range(len(self.t_list)):
            if time.time()-self.times[i-removed] > 5.0:
                self.t_list.pop(i-removed)
                self.times.pop(i-removed)
                removed +=1

    def __len__(self):
        return len(self.t_list)

    def append(self, value):
        self.t_list.append(value)
        self.times.append(time.time())

    def __setitem__(self,index, value):
        return self.t_list.__setitem__(index,value)

    def __getitem__(self, index):
        self.timeout()
        return self.t_list.__getitem__(index)

    def remove(self, value):
        self.times.pop(self.t_list.index(value))
        self.t_list.remove(value)

    def __iter__(self):
        self.timeout()
        for i in self.t_list:
            yield i

    def __delitem__(self, index):
        self.t_list.__delitem__(index)
        self.times.__delitem__(index)

    def insert(self, index, value):
        self.t_list.insert(index, value)
        self.times.insert(index, time.time())



class MessageManager:
    def __init__(self):
        self.long_messages = TimeOutList()

    def write(self, address, message):
        if "DIST" in message:
            with open(f"{os.path.dirname(__file__)}/dist_messages.txt", "a") as file:
                file.write(f"{address[0]} {message}\n")

        else:
            if (
                    " " not in message and "ONLINE?" not in message and "GET_NODES" not in message) or "NREQ" in message:  # TODO clean this up
                self.long_messages.append((address[0], message))

            else:
                with open(f"{os.path.dirname(__file__)}/recent_messages.txt", "a+") as file:
                    file.write(f"{address[0]} {message}\n")
                with open(f"{os.path.dirname(__file__)}/relay_messages.txt", "a+") as file:
                    file.write(f"{address[0]} {message}\n")

        for i in self.long_messages:
            if "]]" in i[1] or "]]]" in i[1] or "}]]" in i[1]:
                # if len([j for j in self.long_messages if j[0] == i[0]]) == len(self.long_messages):
                with open(f"{os.path.dirname(__file__)}/recent_messages.txt", "a+") as file:
                    with open(f"{os.path.dirname(__file__)}/relay_messages.txt", "a+") as relay_file:
                        complete_message = [k for k in self.long_messages.t_list if k[0] == i[0]]
                        long_write_lines = ''.join([l[1] for l in complete_message])
                        file.write(f"{i[0]} {long_write_lines}\n")
                        relay_file.write(f"{i[0]} {long_write_lines}\n")
                for m in complete_message:
                    self.long_messages.remove(m)


# send to node
def send(host, message, port=1379, send_all=False):
    """
    sends a message to the given host
    tries the default port and if it doesn't work search for actual port
    this process is skipped if send to all for speed
    """
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((host, port))
        client.sendall(message.encode("utf-8"))
        print(f"Message to {host} {message}\n")
    except ConnectionRefusedError:
        if send_all:
            return
        try:
            with open(f"{os.path.dirname(__file__)}/info/nodes.json", "r") as file:
                nodes = json.load(file)
            for node in nodes:
                if node["ip"] == host:
                    if not int(node["port"]) == 1379:
                        client.connect((host, int(node["port"])))
                        client.sendall(message.encode("utf-8"))
                        print(f"Message to {host} {message}\n")
        except ConnectionRefusedError:
            return "node offline"
        client.close()

async def async_send(host, message, port=1379, send_all=False):
    """
    sends a message to the given host
    tries the default port and if it doesn't work search for actual port
    this process is skipped if send to all for speed
    """
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((host, port))
        client.sendall(message.encode("utf-8"))
        print(f"Message to {host} {message}\n")
    except ConnectionError:
        if not send_all:
            try:
                with open(f"{os.path.dirname(__file__)}/info/nodes.json", "r") as file:
                    nodes = json.load(file)
                for node in nodes:
                    if node[1] == host:
                        if not int(node["port"]) == 1379:
                            client.connect((host, int(node["port"])))
                            client.sendall(message.encode("utf-8"))
                            print(f"Message to {host} {message}\n")
            except ConnectionError:
                return "node offline"

    client.close()

# check if nodes online
def online(address):
    try:
        send(address, "ONLINE?") #TODO add a way to timeout
        return True
    except TimeoutError:
        return False

def rand_act_node(num_nodes=1, type_=None):
    """
    returns a list of random active nodes which is x length
    """
    with open(f"{os.path.dirname(__file__)}/info/Public_key.txt", "r") as file:
        key = file.read()
    nodes = []
    i = 0
    while i != num_nodes:  # turn into for loop
        with open(f"{os.path.dirname(__file__)}/info/nodes.json", "r") as file:
            all_nodes = json.load(file)
        if type_:
            all_nodes = [node for node in all_nodes if node["node_type"] == type_]
        me = socket.gethostbyname(socket.gethostname())
        node_index = random.randint(0, len(all_nodes) - 1)
        node = all_nodes[node_index]
        # print(node)
        if node["pub_key"] == key or node["ip"] == me:
            continue
        alive = online(node["ip"])
        if alive:
            nodes.append(node)
            i += 1

    if len(nodes) == 1:
        return nodes[0]
    return nodes

def line_remover(del_lines, file_path):
    with open(file_path, "r") as file:
        lines = file.readlines()
    new_lines = [line for line in lines if line.strip("\n") not in del_lines]
    open(file_path, "w").close()
    with open(file_path, "a") as file:
        for line in new_lines:
            file.write(line)

def request_reader(type, ip="192.168.68.1"):
    """
    reads the recent messages and returns the message of the requested type
    """
    with open(f"{os.path.dirname(__file__)}/recent_messages.txt", "r") as file:
        lines = file.read().splitlines()
    pre_protocol = ["ONLINE?", "GET_NODES"]
    node_lines = []
    nreq_lines = []
    online_lines = []
    del_lines = []
    if str(lines) != "[]":
        for line in lines:
            line = line.split(" ")
            try:
                message_handler(line)
            except NodeError as e:
                print("ERROR LINE: ", [" ".join(line)], e)
                send(" ".join(line), f"ERROR {e}")
                del_lines.append(" ".join(line))
                continue
            except NotCompleteError:
                continue

            if line[0] in ("" ,"\n"):
                lines.remove(line)  # delete blank lines

            elif line[1] == "NREQ":
                try:
                    ast.literal_eval(line[2])
                    nreq_lines.append(" ".join(line))
                except ValueError:
                    node_lines.append(" ".join(line))
                except IndexError:
                    node_lines.append(" ".join(line))
                except SyntaxError:
                    pass

            elif line[1] in pre_protocol:
                online_lines.append(" ".join(line))

            else:
                try:
                    ast.literal_eval(line[4])
                    node_lines.append(" ".join(line))
                except ValueError:
                    node_lines.append(" ".join(line))
                except IndexError:
                    node_lines.append(" ".join(line))
                except SyntaxError:
                    pass

        if type == "NODE":
            if len(node_lines) == 0:
                return node_lines
            line_remover(node_lines + del_lines, f"{os.path.dirname(__file__)}/recent_messages.txt")
            return node_lines

        elif type_ == "NREQ":
            if len(nreq_lines) == 0:
                return nreq_lines
            line_remover(nreq_lines + del_lines, f"{os.path.dirname(__file__)}/recent_messages.txt")
            return nreq_lines

        elif type_ == "ONLINE":
            if len(online_lines) == 0:
                return online_lines
            line_remover(online_lines + del_lines, f"{os.path.dirname(__file__)}/recent_messages.txt")
            return online_lines


async def send_to_all(message, no_dist=False):
    """
    sends to all nodes
    """
    while True:
        try:
            with open(f"{os.path.dirname(__file__)}/info/nodes.json", "r") as file:
                all_nodes = json.load(file)
                break
        except json.decoder.JSONDecodeError:
            pass
        if no_dist:
            all_nodes = [i for i in all_nodes if i["node_type"] != "dist"]
    for _ in asyncio.as_completed(
        [async_send(node["ip"], message, port=node["port"], send_all=True) for node in all_nodes]):
        result = await _

async def send_to_all_no_dist(message):
    """
    sends to all nodes
    """
    with open(f"{os.path.dirname(__file__)}/info/nodes.json", "r") as file:
        all_nodes = json.load(file)
    for f in asyncio.as_completed([async_send(node_["ip"], message, port=node_["port"], send_all=True) for node_ in all_nodes if node_["node_type"]!="dist"]):
        result = await f

def announce(pub_key, port, version, node_type, priv_key):
    announcement_time = str(time.time())
    if not isinstance(priv_key, bytes):
        priv_key = SigningKey.from_string(bytes.fromhex(priv_key), curve=SECP112r2)
    sig = str(priv_key.sign(announcement_time.encode()).hex())
    print(f"HELLO {announcement_time} {pub_key} {port} {version} {node_type} {sig}")
    asyncio.run(send_to_all(f"HELLO {announcement_time} {pub_key} {port} {version} {node_type} {sig}"))


def update(old_key, port, version, priv_key, new_key=None):
    if not new_key:
        new_key = old_key
    update_time = str(time.time())
    if not isinstance(priv_key, bytes):
        priv_key = SigningKey.from_string(bytes.fromhex(priv_key), curve=SECP112r2)
    sig = str(priv_key.sign(update_time.encode()).hex())
    asyncio.run(send_to_all(f"UPDATE {update_time} {old_key} {new_key} {port} {version} {sig}"))
    with open(f"{os.path.dirname(__file__)}/info/Public_key.txt", "w") as file:
        file.write(new_key)


def delete(pub_key, priv_key):
    update_time = str(time.time())
    if not isinstance(priv_key, bytes):
        priv_key = SigningKey.from_string(bytes.fromhex(priv_key), curve=SECP112r2)
    sig = str(priv_key.sign(update_time.encode()).hex())
    asyncio.run(send_to_all(f"DELETE {update_time} {pub_key} {sig}"))


def get_nodes(nodes=[]):
    print("---GETTING NODES---")
    pre_nodes = copy.copy(nodes)
    while True:
        node = rand_act_node()
        if node in nodes:
            break
            continue
        else:
            break
    time.sleep(0.1)
    send(node["ip"], "GET_NODES")
    tries = 0
    while True:
        if tries == 10:
            return get_nodes(pre_nodes)
        time.sleep(2)
        lines = request_reader("NREQ")
        if lines:
            line = lines[0].split(" ")
            if line[0] == node["ip"]:
                nodes_1 = ast.literal_eval(line[2])
                print("---NODES 1 RECEIVED---")
                break
        else:
            tries += 1
    nodes.append(node)
    while True:
        node = rand_act_node()
        if node in nodes:
            break
            continue
        else:
            break
    time.sleep(0.1)
    send(node["ip"], "GET_NODES")
    tries = 0
    while True:
        if tries == 10:
            return get_nodes(pre_nodes)
        time.sleep(2)
        lines = request_reader("NREQ")
        if lines:
            line = lines[0].split(" ")
            if line[0] == node["ip"]:
                nodes_2 = ast.literal_eval(line[2])
                print("---NODES 2 RECEIVED---")
                break
        else:
            tries += 1
    nodes.append(node)
    if nodes_1 == nodes_2:
        with open(f"{os.path.dirname(__file__)}/info/nodes.json", "w") as file:
            json.dump(nodes_1, file)
        print("---NODES UPDATED---")
        return nodes
    return get_nodes(pre_nodes)


def send_node(host):
    with open(f"{os.path.dirname(__file__)}/info/nodes.json", "r") as file:
        nodes = json.load(file)
    str_node = str(nodes)
    str_node = str_node.replace(" ", "")
    send(host, "NREQ " + str_node)


def new_node(initiation_time, ip, pub_key, port, node_version, node_type, sig):
    with open(f"{os.path.dirname(__file__)}/info/nodes.json", "r") as file:
        nodes = json.load(file)
    public_key = VerifyingKey.from_string(bytes.fromhex(pub_key), curve=SECP112r2)
    if public_key.verify(bytes.fromhex(sig), str(initiation_time).encode()):
        new_node = {"time": initiation_time, "ip": ip, "pub_key": pub_key, "port": port, "version": node_version,
                    "node_type": node_type}
        for node in nodes:
            if node["pub_key"] == pub_key:
                return
            if node["ip"] == ip:
                return
        nodes.append(new_node)
        with open(f"{os.path.dirname(__file__)}/info/nodes.json", "w") as file:
            json.dump(nodes, file)
        print("---NODE ADDED---")
    else:
        return "node invalid"


def update_node(ip, update_time, old_key, new_key, port, node_version, sig):
    with open(f"{os.path.dirname(__file__)}/info/nodes.json", "r") as file:
        nodes = json.load(file)
    public_key = VerifyingKey.from_string(bytes.fromhex(old_key), curve=SECP112r2)
    try:
        assert public_key.verify(bytes.fromhex(sig), str(update_time).encode())
        for node in nodes:
            if node["ip"] == ip:
                node["pub_key"] = new_key
                node["port"] = port
                node["version"] = node_version
        with open(f"{os.path.dirname(__file__)}/info/nodes.json", "w") as file:
            json.dump(nodes, file)
            print("NODE UPDATED")
    except:
        return "update invalid"


def delete_node(deletion_time, ip, pub_key, sig):
    with open(f"{os.path.dirname(__file__)}/info/nodes.json", "r") as file:
        nodes = json.load(file)
    public_key = VerifyingKey.from_string(bytes.fromhex(pub_key), curve=SECP112r2)
    try:
        assert public_key.verify(bytes.fromhex(sig), str(deletion_time).encode())
        for node in nodes:
            if node["ip"] == ip and node["pub_key"] == pub_key:
                nodes.remove(node)
        with open(f"{os.path.dirname(__file__)}/info/nodes.json", "w") as file:
            json.dump(nodes, file)
    except:
        return "cancel invalid"

def version():
    asyncio.run(send_to_all(f"VERSION {__version__}"))

def version_update(ip, ver):
    with open(f"{os.path.dirname(__file__)}/info/nodes.json", "r") as file:
        nodes = json.load(file)
    for nod in nodes:
        if nod["ip"] == ip:
            nod["version"] = ver
            break

class NotCompleteError(Exception):
    """
    Raised when problem with line but the line is needed to be kept in recent messages
    """
    pass

class NodeError(Exception):
    pass


class UnrecognisedCommand(NodeError):
    pass


class ValueTypeError(NodeError):
    pass


class UnrecognisedArg(NodeError):
    pass

def check_float(value):
    try:
        float(value)
        if float(value) < 0:
            raise ValueTypeError
        if value.isdigit():
            raise ValueTypeError
        return True
    except ValueError:
        return False


def check_int(value):
    if value.isdigit():
        return True
    return False


#  TODO add AI_JOB protocols
def message_handler(message):
    """
    All messages are in the form of "<ip> PROTOCOL <args...>"

    HELLO <ip> <port> <pub_key> <version> <node_type> <signature>
    UPDATE <ip> <update_time> <old_key> <new_key> <port> <version> <signature>
    DELETE <ip> <deletion_time> <public_key> <signature>
    GET_NODES <ip>
    NREQ <ip> <nodes>
    ONLINE? <ip>
    ERROR <ip> <error_message>
    """
    len_1_messages = ["ONLINE?", "GET_NODES"]
    if len(message) == 2:
        if message[1] not in len_1_messages:
            raise UnrecognisedArg("No Protocol Found")
    if len(message) < 2:
        raise UnrecognisedArg("number of args given incorrect")
    protocol = message[1]

    node_types = ["Lite", "Blockchain", "AI", "dist"]

    if protocol == "GET_NODES":
        if len(message) != 2:
            raise UnrecognisedArg(f"number of args given incorrect during {protocol}")

    elif protocol == "HELLO":
        # host, HELLO, announcement_time, public key, port, version, node type, sig
        if len(message) != 8:
            raise UnrecognisedArg("number of args given incorrect")

        if not check_float(message[2]):
            raise ValueTypeError("time not given as float")

        if len(message[3]) != 56:
            raise UnrecognisedArg("Public Key is the wrong size")

        if not check_int(message[4]):
            raise ValueTypeError("port not given as int")
        else:
            port = int(message[4])

        if not port > 0 and port < 65535:
            raise ValueTypeError("TCP port out of range")

        if not check_float(message[5]):
            raise ValueTypeError("version not given as float")

        if message[6] not in node_types:
            raise UnrecognisedArg("Node Type Unknown")

        if len(message[7]) != 56:
            raise UnrecognisedArg("Signature is the wrong size")

    elif protocol == "ONLINE?":
        # host, ONLINE?
        if len(message) != 2:
            raise UnrecognisedArg("number of args given incorrect")

        if not check_int(message[2]):
            raise ValueTypeError("Chunk Index not given as int")

    elif protocol == "UPDATE":
        # host, UPDATE, update time, old public key, new public key, port, version, sig
        if len(message) != 7:
            raise UnrecognisedArg("number of args given incorrect")

        if not check_float(message[2]):
            raise ValueTypeError("time not given as float")

        if len(message[3]) != 56:
            raise UnrecognisedArg("Old Public Key is the wrong size")

        if len(message[4]) != 56:
            raise UnrecognisedArg("New Public Key is the wrong size")

        if not check_int(message[5]):
            raise ValueTypeError("port not given as int")
        else:
            port = int(message[5])

        if not port >= 0 and port < 65535:
            raise ValueTypeError("TCP port out of range")

        if not check_float(message[6]):
            raise ValueTypeError("version not given as float")

        if len(message[7]) != 56:
            raise UnrecognisedArg("Signature is the wrong size")

    elif protocol == "DELETE":
        # host, DELETE, time, public key, sig
        if len(message) != 5:
            raise UnrecognisedArg("number of args given incorrect")

        if not check_float(message[2]):
            raise ValueTypeError("time not given as float")

        if len(message[3]) != 56:
            raise UnrecognisedArg("Public Key is the wrong size")

        if len(message[4]) != 56:
            raise UnrecognisedArg("Signature is the wrong size")

    elif protocol == "NREQ":
        # host, NREQ, nodes
        try:
            ast.literal_eval(message[2])
        except ValueError:
            raise ValueTypeError("Nodes not given as Node List")
        except SyntaxError:
            raise NotCompleteError("NREQ list not complete yet")

    elif protocol == "ERROR":
        pass

    elif protocol == "yh":
        pass

    else:
        raise UnrecognisedCommand("protocol unrecognised")
