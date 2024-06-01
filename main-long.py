import time
all_start_t = time.time()

import argparse
import logging
import os
import socket
# from threading import Thread
from agent.position import Position
# from glitch_2pow import Glitch2Pow
# from utils import *
# from agent.agent_hack import Agent
print(f"Import time: {time.time() - all_start_t}")
# from agent.agent import Agent

print(f"Import time: {time.time() - all_start_t}")
from mitm import MITM

print(f"Import time: {time.time() - all_start_t}")

logging.basicConfig(level=logging.INFO)


# print("IP address of server:", get_ip_address('localhost'), file=stderr)
# print("IP address of server:", get_ip_address('server'), file=stderr)


def main_victim(agent, mitm: MITM):
    import logic_victim
    print("Main v", flush=True)
    # print("Saiblo:", saiblo, flush=True)
    # if not saiblo:
    #     print("Victim token:", mitm.victim_token, flush=True)
    # Control the victim
    # agent_victim = Agent(token=mitm.victim_token, server=agent._server, is_normal=False)
    # Thread(target=logic_victim.logic, args=(agent_victim,)).start()
    logic_victim.logic(agent, mitm)
    # while not agent.is_ready():
    #     time.sleep(0.1)
    #     agent._update()
    # Thread(target=logic_victim.logic, args=(agent, mitm)).start()
    # logic_demo.logic(agent)


def main_dos(agent, mitm: MITM):
    print("Main d", flush=True)
    agent.close()
    mitm.exit()
    exit(123)
    while not agent.is_ready():
        time.sleep(0.1)
        agent._update()
    obstacle = convert_map(agent.map)
    origin = (0, 0)
    while obstacle[origin]:
        origin = (origin[0], origin[1] + 1)
    agent.choose_origin(Position[float](*origin))
    while agent.ticks < 200:
        agent._update()
        time.sleep(1)
    while not agent.terminated:
        agent.move(Position[float](-1e-200, origin[1]))
        agent._update()
        time.sleep(1)

def main_demo(agent, mitm: MITM):
    import logic_demo
    logic_demo.logic(agent)




def main():
    parser = argparse.ArgumentParser("opponent")
    parser.add_argument("--token", type=str, help="Token in the game", default="1919810")
    parser.add_argument("--server", type=str, help="Server address", default="ws://localhost:14514")
    args = parser.parse_args()
    server = os.getenv("SERVER", default=args.server)
    token = os.getenv("TOKEN", default=args.token)
    mitm = MITM(server=server)
    print(f"Timer: {mitm.timer - all_start_t}", flush=True)

    # stderr.flush()
    from agent.agent import Agent
    if mitm.get_token(timeout=5.):
        print("pwned")
        agent = Agent(token=token, server=server)
        # mitm.collect_info()
        main_victim(agent, mitm)
    # elif mitm.get_rev():
    #     print("server to enemy sniffed")
    #     agent = Agent(token=token, server=server)
    #     # Send RST
    #     mitm.disconnect_victim_c()
    #     main_demo(agent, mitm)
    else:
        print("float")
        agent = Agent(token=token, server=server)
        main_dos(agent, mitm)

    # while not agent.hack_ready():
    #     time.sleep(0.1)
    #     agent._update()
    # print("hack clients connected")


    # glitch = Glitch2Pow(agent)
    # glitch.choose_origin()
    # glitched = False


    # stderr.flush()
    # mitm.collect_info()
    # mitm.disconnect_victim_c()





if __name__ == '__main__':
    print(f"Main time: {time.time() - all_start_t}")
    main()
