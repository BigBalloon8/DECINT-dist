import node
import distributor
import os

def rec():
    print("---RECEIVER STARTED---")
    while True:
        message, address = node.receive()
        print(f"Message from {address} , {message}\n")
        with open(f"{os.path.dirname(__file__)}/recent_messages.txt", "a") as file:
            file.write(f"{address[0]} {message}\n")
        with open(f"{os.path.dirname(__file__)}/relay_messages.txt", "a") as file:
            file.write(f"{address[0]} {message}\n")


if __name__ == "__main__":
    rec()
