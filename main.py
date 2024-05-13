import argparse
import os
from sys import stderr
import socket
from utils import *
import time
from agent.agent_hack import Agent


print("IP address of server:", get_ip_address('localhost'), file=stderr)
print("IP address of server:", get_ip_address('server'), file=stderr)

# input()


try:
    print("fuck", file=stderr)
    if saiblo:
        for key, value in os.environ.items():
            print(f"{key}={value}", file=stderr)
except:
    pass






def main():
    parser = argparse.ArgumentParser("opponent")
    parser.add_argument("--token", type=str, help="Token in the game", default="1919810")
    parser.add_argument("--server", type=str, help="Server address", default="ws://localhost:14514")
    args = parser.parse_args()
    server = os.getenv("SERVER", default=args.server)
    token = os.getenv("TOKEN", default=args.token)
    agent = Agent(token=token, server=server, num_hack_ws=0)
    while not agent.is_ready():
        time.sleep(0.1)

    while not agent.hack_ready():
        time.sleep(0.1)
        agent._update()

    print("hack clients connected")

    # Send huge number to server

    if False:
        # Choose_origin is blocked
        agent._ws_client.send('''{
            "messageType": "CHOOSE_ORIGIN",
            "token": "%s", 
            "originPosition":{
                "x": %s,
                "y": %s
            }
        }''' % (agent._token, "1e400", "1e400"))

    if True:
        # Choose_origin to (0.0, 0.0)
        agent._ws_client.send('''{
            "messageType": "CHOOSE_ORIGIN",
            "token": "%s", 
            "originPosition":{
                "x": %s,
                "y": %s
            }
        }''' % (agent._token, "0", "0"))

    while not agent.terminated:

        if False:
            agent._ws_client.send('''{
                "messageType": "PERFORM_MOVE",
                "token": "%s", 
                "destination":{
                    "x": %s,
                    "y": %s
                }
            }''' % (agent._token, "1e400", "1e400"))

        if False:
            agent._ws_client.send('''{
                "messageType": "PERFORM_ATTACK",
                "token": "%s", 
                "targetPosition":{
                    "x": %s,
                    "y": %s
                }
            }''' % (agent._token, "1e-300", "1e-300"))

        if False:
            agent.spam_msg(msg='''{
                "messageType": "PERFORM_MOVE",
                "token": "%s",
                "destination":{
                    "x": %s,
                    "y": %s
                }
            }''' % (agent._token, "1e400", "1e400"),
                           tot=100, group=10)

        if True:
            agent.spam_msg(msg='''{
                "messageType": "PERFORM_ATTACK",
                "token": "%s", 
                "targetPosition":{
                    "x": %s,
                    "y": %s
                }
            }''' % (agent._token, "1e-300", "1e-300"),
                           tot=10, group=100)
        agent._update()
        # time.sleep(0.05)



if __name__ == '__main__':
    main()
