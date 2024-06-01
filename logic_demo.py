from sys import stderr
import time
import numpy as np
from agent.position import Position
from utils import *

from agent.agent import Agent

def logic(agent: Agent):
    print(f"Start demo logic", flush=True)
    from pathfinding.core.grid import Grid
    from pathfinding.finder.best_first import BestFirst
    from pathfinding.finder.breadth_first import BreadthFirstFinder
    while not agent.is_ready():
        time.sleep(0.1)
        agent._update()
    origin = None
    for supply in agent.supplies:
        if supply.kind == 'PREMIUM_ARMOR':
            origin = (supply.position.x, supply.position.y)
            break
    if not origin:
        for supply in agent.supplies:
            if supply.kind == 'FIRST_AID':
                origin = (supply.position.x, supply.position.y)
                break
    if not origin:
        for supply in agent.supplies:
            if supply.kind == 'PRIMARY_ARMOR':
                origin = (supply.position.x, supply.position.y)
                break
    if origin:
        agent.choose_origin(Position[float](*origin))
    print(f"Choose origin at {origin}", flush=True)
    while not agent.terminated:
        agent._update()
        time.sleep(0.01)
        player = agent.player
        enemy = agent.enemy
        # print(f"Tick: {agent.ticks}", file=stderr, flush=True)
        ppos_f = player.position.x, player.position.y
        ppos = int(ppos_f[0]), int(ppos_f[1])
        opos_f = enemy.position.x, enemy.position.y
        opos = int(opos_f[0]), int(opos_f[1])
        dist_op = dist(ppos_f, opos_f)
        # print(f"Supply Position: {agent.supplies[0].position}", flush=True)
        print(f"Player position: {player.position}  health: {player.health}", flush=True)
        print(f"Enemy position: {enemy.position}  health: {enemy.health}", flush=True)
        if any(ppos == (supply.position.x, supply.position.y) for supply in agent.supplies):
            agent.pick_up("PREMIUM_ARMOR", 1)
            agent.pick_up("PRIMARY_ARMOR", 1)
            agent.pick_up("FIRST_AID", 1)
        if dist_op <= 2:
            agent.attack(Position[float](*opos_f))
        if dist_op > 0.5:
            matrix = convert_map(agent.map).T.astype(int)
            grid = Grid(matrix=matrix)
            finder = BestFirst()
            start = grid.node(*ppos)
            end = grid.node(*opos)
            path, runs = finder.find_path(start, end, grid)
            if len(path) > 1:
                nx, ny = path[1]
                agent.move(position=Position[float](nx+0.5, ny+0.5))
            else:
                print(f"Path: {path}", flush=True)


