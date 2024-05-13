import json
import logging
from queue import SimpleQueue
from threading import Thread
import time
from typing import List, Literal, Optional

from websocket import WebSocketApp, WebSocketException

from . import messages
from .map import Map
from .player_info import FirearmKind, Item, ItemKind, PlayerInfo
from .position import Position
from .safe_zone import SafeZone
from .supply import Supply, SupplyKind

from utils import saiblo

MedicineKind = Literal[
    "BANDAGE",
    "FIRST_AID",
]


class Agent:
    """
    I rewrite this because of async
    Agent to connect and play
    Provide some interfaces

    Getting the latest information
    Perform action
    
    Attributes
    player:
        PlayerInfo
    enemy:
        PlayerInfo
    map:
        Map
    supplies:
        List[Supply]
    safe_zone:
        SafeZone
    self_id:
        player id
    ticks:
        tick
    
    """
    def __init__(self,
                 token: str,
                 server: str,
                 logging_level: int = logging.DEBUG,
        ):
        self._token = token
        self._server = server
        self._logger = logging.getLogger("Agent")
        self._logging_level = logging_level
        self._self_id: Optional[int] = None
        self._connected = False
        self._ws_client: Optional[WebSocketApp] = None
        """
        The queue and the ws is used to receive and store info
        """
        self._que = SimpleQueue()

        def on_open(ws):
            print("on_open")
            self._que.put({
                "messageType": "open"
            })
            self.upd_info()

        def on_message(ws, msg):
            self._que.put(json.loads(msg))

        def on_close(ws, close_status_code, close_msg):
            print("on_close")
            self._que.put({
                "messageType": "close"
            })

        def start_ws():
            while True:
                # print('fuck')
                try:
                    self._ws_client = WebSocketApp(
                        server,
                        on_open=on_open,
                        on_message=on_message,
                        on_close=on_close,
                    )
                    self._ws_client.run_forever()
                    self._update()
                    if self._connected:
                        print("Fuck")
                        return
                except:
                    pass
                time.sleep(3)
                # print('end fuck')

        Thread(target=start_ws).start()

        self.player: Optional[PlayerInfo] = None
        self.enemy: Optional[PlayerInfo] = None
        self.map: Optional[Map] = None
        self.supplies: Optional[List[Supply]] = None
        self.safe_zone: Optional[SafeZone] = None
        self.ticks: Optional[int] = 0
        self.terminated = False

        self._logs_time = {
            "playerInfo": [],
            "map": [],
            "supplies": [],
            "safe_zone": [],
            "ticks": [],
        }

    def __str__(self) -> str:
        return f"Agent{{token: {self._token}}}"

    def __repr__(self) -> str:
        return str(self)

    def upd_info(self):
        self._ws_client.send(messages.GetPlayerInfoMessage(token=self._token).json())

    def is_ready(self) -> bool:
        self._update()
        """
        if self.player is None:
            print("player")
        elif self.enemy is None:
            print("enemy")
        elif self.ticks is None:
            print("ticks")
        elif self.map is None:
            print("map")
        elif self.supplies is None:
            print("supplies")
        elif self.safe_zone is None:
            print("safe_zone")
        else:
            print("else")
        """
        return  self._connected and \
                self.player is not None and \
                self.enemy is not None and \
                self.map is not None and \
                self.supplies is not None and \
                self.safe_zone is not None and \
                self.ticks is not None

    def is_done(self) -> bool:
        return self.terminated

    def is_win(self) -> bool:
        return self.enemy.health <= 0

    def check_alive(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except WebSocketException:
                # self.terminated = True
                pass
        return wrapper

    @check_alive
    def abandon(self, supply: SupplyKind, count: int):
        logging.log(self._logging_level, "%s.abandon(%s, %d)", self, supply, count)
        self._ws_client.send(
            messages.PerformAbandonMessage(
                token=self._token,
                numb=count,
                target_supply=supply,
            ).json()
        )

    @check_alive
    def pick_up(self, supply: SupplyKind, count: int):
        logging.log(self._logging_level, "%s.pick_up(%s, %d)", self, supply, count)
        self._ws_client.send(
            messages.PerformPickUpMessage(
                token=self._token, target_supply=supply, num=count
            ).json()
        )

    @check_alive
    def switch_firearm(self, firearm: FirearmKind):
        logging.log(self._logging_level, "%s.switch_firearm(%s)", self, firearm)
        self._ws_client.send(
            messages.PerformSwitchArmMessage(
                token=self._token,
                target_firearm=firearm,
            ).json()
        )

    @check_alive
    def use_medicine(self, medicine: MedicineKind):
        logging.log(self._logging_level, "%s.use_medicine(%s)", self, medicine)
        self._ws_client.send(
            messages.PerformUseMedicineMessage(
                token=self._token,
                medicine_name=medicine,
            ).json()
        )

    @check_alive
    def use_grenade(self, position: Position[float]):
        logging.log(self._logging_level, "%s.use_grenade(%s)", self, position)
        self._ws_client.send(
            messages.PerformUseGrenadeMessage(
                token=self._token,
                target_position=messages.Position(x=position.x, y=position.y),
            ).json()
        )

    @check_alive
    def move(self, position: Position[float]):
        logging.log(self._logging_level, "%s.move(%s)", self, position)
        self._ws_client.send(
            messages.PerformMoveMessage(
                token=self._token,
                destination=messages.Position(x=position.x, y=position.y),
            ).json()
        )

    @check_alive
    def stop(self):
        logging.log(self._logging_level, "%s.stop()", self)
        self._ws_client.send(
            messages.PerformStopMessage(
                token=self._token,
            ).json()
        )

    @check_alive
    def attack(self, position: Position[float]):
        logging.log(self._logging_level, "%s.attack(%s)", self, position)
        self._ws_client.send(
            messages.PerformAttackMessage(
                token=self._token,
                target_position=messages.Position(x=position.x, y=position.y),
            ).json()
        )

    @check_alive
    def choose_origin(self, position: Position[float]):
        logging.log(self._logging_level, "%s.choose_origin(%s)", self, position)
        self._ws_client.send(
            messages.ChooseOriginMessage(
                token=self._token,
                origin_position=messages.Position(x=position.x, y=position.y),
            ).json()
        )

    def teleport(self, x: int, y: int):
        self.choose_origin(position=Position[float](x+0.5, y+0.5))

    def _update(self):
        """
        Fetch all queued ws messages and update
        This should only be called in `step` to show changes, or before the game is ready
        """
        # self.upd_info()
        while not self._que.empty():
            msg_dict: dict = self._que.get_nowait()
            msg_type = msg_dict["messageType"]
            if msg_type == 'open':
                # WS connection established
                # print("opening")
                self._connected = True
                self.terminated = False

            elif msg_type == 'close':
                # WS connection closed
                if self._connected:
                    print("terminating")
                    self.terminated = True
                else:
                    print("Retrying")

            elif msg_type == 'ERROR':
                logging.error(f"{self} got error from server: {msg_dict['message']}")

            elif msg_type == 'PLAYERS_INFO':
                if not saiblo: self._logs_time["playerInfo"].append(time.time())
                for data in msg_dict["players"]:
                    # print(data.keys())
                    # ['playerId', 'armor', 'health', 'speed', 'firearm', 'position', 'inventory']
                    _p = PlayerInfo(
                        id=data["playerId"],
                        armor=data["armor"],
                        current_armor_health=data["current_armor_health"],
                        health=data["health"],
                        speed=data["speed"],
                        firearm=data["firearm"]["name"],
                        firearms_pool=[
                            weapon_data["name"] for weapon_data in data["firearms_pool"]
                        ],
                        range=data["firearm"]["distance"],
                        position=Position(
                            x=data["position"]["x"], y=data["position"]["y"]
                        ),
                        inventory=[
                            Item(kind=item["name"], count=item["num"])
                            for item in data["inventory"]
                        ],
                    )
                    if _p.id == self._self_id:
                        if _p.health == 0:
                            self.terminated = True
                        self.player = _p
                    else:
                        self.enemy = _p

            elif msg_type == 'MAP':
                if not saiblo: self._logs_time["map"].append(time.time())
                self.map = Map(
                    length=msg_dict["length"],
                    obstacles=[
                        Position(
                            x=wall["wallPositions"]["x"], y=wall["wallPositions"]["y"]
                        )
                        for wall in msg_dict["walls"]
                    ],
                )

            elif msg_type == 'SUPPLIES':
                if not saiblo: self._logs_time["supplies"].append(time.time())
                self.supplies = [
                    Supply(
                        kind=supply["name"],
                        position=Position(
                            x=supply["position"]["x"], y=supply["position"]["y"]
                        ),
                        count=supply["numb"],
                    )
                    for supply in msg_dict["supplies"]
                ]

            elif msg_type == 'SAFE_ZONE':
                if not saiblo: self._logs_time["safe_zone"].append(time.time())
                self.safe_zone = SafeZone(
                    center=Position(
                        x=msg_dict["center"]["x"], y=msg_dict["center"]["y"]
                    ),
                    radius=msg_dict["radius"],
                )

            elif msg_type == 'PLAYER_ID':
                self._self_id = msg_dict["playerId"]

            elif msg_type == "TICKS":
                self._logs_time["ticks"].append(time.time())
                self.ticks = msg_dict["elapsedTicks"]

            else:
                logging.error(f"Unhandled message type: {msg_type}")




