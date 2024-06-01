from collections import deque
from sys import stderr, stdout
import time
from typing import Optional
import numpy as np
import logging

# logging.basicConfig(level=logging.INFO)

from agent.agent import Agent
from agent.position import Position
from mitm import MITM
from utils import *

def logic(agent: Agent, mitm: MITM):
    """
    Control the logic of victim and the player at the same time
    """
    if mitm.is_multi:
        return logic_multi(agent, mitm)
    while not agent.is_ready():
        agent._update()
        time.sleep(0.1)
    obstacle = convert_map(agent.map)
    def choose_origin_victim() -> Optional[tuple]:
        # print(f"Supply: {agent.supplies[0].position}")
        origin = None
        max_count = 0
        for supply in agent.supplies:
            if supply.kind == 'GRENADE' and supply.count > max_count:
                origin = (supply.position.x + 0.1, supply.position.y + 0.1)
                max_count = supply.count
        if not origin:
            # No grenade, wait to die
            for (i, j), obs in np.ndenumerate(obstacle):
                if obs:
                    continue
                if any((i, j) == (supply.position.x, supply.position.y) for supply in agent.supplies):
                    continue
                origin = (i, j)
                break
        return origin

    origin_victim = choose_origin_victim()
    if not saiblo:
        print(f"Victim origin: {origin_victim}",flush=True)

    def choose_origin_player(origin_victim):
        origin = (0, 0)
        for y, obs in enumerate(obstacle[0]):
            if obs:
                continue
            t = (0, y)
            d1 = dist(origin, origin_victim)
            d2 = dist(t, origin_victim)
            if d2 > d1:
                origin = t
        return origin

    origin_player = choose_origin_player(origin_victim)
    agent.choose_origin(Position[float](*origin_player))

    agent._update()
    print(f"Logic start tick: {agent.ticks}")
    last_grenade = 0
    while not agent.terminated:
        agent._update()

        # Victim logic
        if agent.ticks >= 180 and agent.ticks < 200:
            # if agent.ticks == 195:
            #     print("Choosing origin", flush=True)
            agent.choose_origin(Position[float](*origin_victim), token=mitm.victim_token)
        # agent.stop()
        if agent.ticks >= 195:
            # if agent.ticks == 250:
            #     print("Freeze")
            agent.move(Position[float](*origin_victim), token=mitm.victim_token)
            if agent.ticks <= 220:
                if not agent.grenade_info:
                    if agent.ticks == 210:
                        print("G 1")
                    agent.pick_up(supply='GRENADE', count=1, token=mitm.victim_token)
                    agent.use_grenade(Position[float](*origin_victim), token=mitm.victim_token)
                if agent.enemy.current_armor_health:
                    agent.abandon("PREMIUM_ARMOR", 1, token=mitm.victim_token)
                    agent.abandon("PRIMARY_ARMOR", 1, token=mitm.victim_token)
            elif any(supply.kind == 'GRENADE' and \
                    dist((supply.position.x, supply.position.y), origin_victim) <= 1 \
                    for supply in agent.supplies):
                agent.pick_up(supply='GRENADE', count=1, token=mitm.victim_token)
                agent.use_grenade(Position[float](*origin_victim), token=mitm.victim_token)
            elif (last_grenade + 20 < agent.ticks and \
                    any(supply.kind == 'GRENADE' for supply in agent.enemy.inventory)):
                # print("G 2,3,4")
                agent.use_grenade(Position[float](*origin_victim), token=mitm.victim_token)
                last_grenade = agent.ticks
        # print(f"Victim position: {agent.player.position}  health: {agent.player.health}  armor: {agent.player.armor}",
        #       file=stderr,
        #       flush=True)
        time.sleep(0.01)

        # Player logic
        player = agent.player
        enemy = agent.enemy
        opos_f = enemy.position.x, enemy.position.y
        if agent.ticks > 200 and dist(opos_f, origin_victim) > 1:
            print(f"Deviated: {origin_victim} to {opos_f}", flush=True)
            print(f"Deviated: {origin_victim} to {opos_f}", flush=False)
        if any(supply.kind in ["PREMIUM_ARMOR", "PRIMARY_ARMOR", "FIRST_AID"] and \
                player.position == supply.position \
                for supply in agent.supplies):
            agent.pick_up("PREMIUM_ARMOR", 1)
            agent.pick_up("PRIMARY_ARMOR", 1)
            agent.pick_up("FIRST_AID", 1)
        if agent.ticks >= 350:
            if (agent.ticks - 350) % 200 == 0:
                print(f"Fuck, {player.health}, {enemy.health}, {dist(opos_f, origin_victim)}")
            # exit(124)
            agent.move(Position[float](-1e-200, origin_player[1]))
            # if not player.current_armor_health and (not player.inventory or len(player.inventory) == 0):
            #     continue
            # print(f"Tick: {agent.ticks}", file=stderr, flush=True)
            # ppos_f = player.position.x, player.position.y
            # ppos = int(ppos_f[0]), int(ppos_f[1])
            # opos_f = enemy.position.x, enemy.position.y
            # opos = int(opos_f[0]), int(opos_f[1])
            # dist_op = dist(ppos_f, opos_f)
            # if dist_op <= 2:
            #     agent.attack(Position[float](*opos_f))
            # if dist_op > 0.5:
            #     matrix = convert_map(agent.map).T.astype(int)
            #     grid = Grid(matrix=matrix)
            #     finder = BestFirst()
            #     start = grid.node(*ppos)
            #     end = grid.node(*ppos)
            #     agent._update()
            #     path, runs = finder.find_path(start, end, grid)
            #     agent._update()
            #     if len(path) > 1:
            #         nx, ny = path[1]
            #         agent.move(position=Position[float](nx+0.5, ny+0.5))
            # print(f"Not finished yet\n"
            #       f"Player position: {ppos_f}  Health: {player.health}  Armor: {player.current_armor_health}\n"
            #       f"Enemy  position: {opos_f}  Health: {enemy.health}  Armor: {enemy.current_armor_health}\n",
            #       file=stderr,
            #       flush=True)

    if not agent.is_win():
        logging.error("Victim wins, this shouldn't happen")

def logic_multi(agent: Agent, mitm: MITM):
    """
    Multiplayer
    Control the logic of enemies and the player at the same time
    """
    while not agent.is_ready():
        agent._update()
        time.sleep(0.1)
    obstacle = convert_map(agent.map)
    def choose_origin_victim() -> Optional[tuple]:
        # print(f"Supply: {agent.supplies[0].position}")
        origin = None
        for supply in agent.supplies:
            if supply.kind == 'GRENADE':
                origin = (supply.position.x + 0.1, supply.position.y + 0.1)
                break
        if not origin:
            # No grenade, wait to die
            for (i, j), obs in np.ndenumerate(obstacle):
                if obs:
                    continue
                if any((i, j) == (supply.position.x, supply.position.y) for supply in agent.supplies):
                    continue
                origin = (i, j)
                break
        return origin

    origin_victim = choose_origin_victim()
    if not saiblo:
        print(f"Victim origin: {origin_victim}", file=stderr, flush=True)

    def choose_origin_player(origin_victim):
        origin = (0, 0)
        for y, obs in enumerate(obstacle[0]):
            if obs:
                continue
            t = (0, y)
            d1 = dist(origin, origin_victim)
            d2 = dist(t, origin_victim)
            if d2 > d1:
                origin = t
        return origin

    origin_player = choose_origin_player(origin_victim)
    agent.choose_origin(Position[float](*origin_player))

    token_que = deque(list(mitm.addr_to_token.values()))

    def roll_token():
        t = token_que.popleft()
        token_que.append(t)
        return t

    while not agent.terminated:
        agent._update()

        # Victim logic
        if agent.ticks >= 170 and agent.ticks < 200:
            agent.choose_origin(Position[float](*origin_victim), token=roll_token())
        # agent.stop()
        if agent.ticks >= 195:
            agent.move(Position[float](*origin_victim), token=roll_token())
            if agent.ticks <= 220:
                if not agent.grenade_info:
                    t = roll_token()
                    agent.move(Position[float](*origin_victim), token=t)
                    agent.pick_up(supply='GRENADE', count=1, token=t)
                    agent.use_grenade(Position[float](*origin_victim), token=t)
        # print(f"Victim position: {agent.player.position}  health: {agent.player.health}  armor: {agent.player.armor}",
        #       file=stderr,
        #       flush=True)
        time.sleep(0.01)

        # Player logic
        player = agent.player
        enemy = agent.enemy
        if any(supply.kind in ["PREMIUM_ARMOR", "PRIMARY_ARMOR", "FIRST_AID"] and \
                player.position == supply.position \
                for supply in agent.supplies):
            agent.pick_up("PREMIUM_ARMOR", 1)
            agent.pick_up("PRIMARY_ARMOR", 1)
            agent.pick_up("FIRST_AID", 1)
        if agent.ticks >= 350:
            # if not player.current_armor_health and (not player.inventory or len(player.inventory) == 0):
            #     continue
            # print(f"Tick: {agent.ticks}", file=stderr, flush=True)
            agent.move(Position[float](-1e-200, origin_player[1]))

    if not agent.is_win():
        logging.error("Victim wins, this shouldn't happen")
