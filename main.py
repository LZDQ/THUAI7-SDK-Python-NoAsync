import argparse
import os
from sys import stderr
import socket
from glitch_2pow import Glitch2Pow
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
    agent = Agent(token=token, server=server, num_hack_ws=20)
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

    # glitch = Glitch2Pow(agent)
    # glitch.choose_origin()
    # glitched = False

    while not agent.terminated:

        if False:  # Make server convert NaN to int and access -2147..
            agent._ws_client.send('''{
                "messageType": "PERFORM_ATTACK",
                "token": "%s", 
                "targetPosition":{
                    "x": %s,
                    "y": %s
                }
            }''' % (agent._token, "1e-300", "1e-300"))

        if True:
            agent.spam_msg(msg=['''{
                "messageType": "PERFORM_MOVE",
                "token": "%s", 
                "destination":{
                    "x": %s,
                    "y": %s
                }
            }''' % (agent._token, "1e400", "1e400"),
                                '''{
                "messageType": "PERFORM_MOVE",
                "token": "%s", 
                "destination":{
                    "x": %f,
                    "y": %f
                }
            }''' % (agent._token,
                    agent.player.position.x + np.random.choice([0.1, -0.1]),
                    agent.player.position.y + np.random.choice([0.1, -0.1]))],
                           tot=10, group=2)

        # if not glitched:
        #     glitch.move()
        #     if agent.player.position.x >= glitch.wall[0]:
        #         glitched = True
        #     print(f"Trying. Current position: {agent.player.position}")
        # else:
        #     print(f"Glitched! Current position: {agent.player.position}")
        agent._update()
        # time.sleep(0.05)



if __name__ == '__main__':
    main()
