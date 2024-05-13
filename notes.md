game_env

定义 gym 环境。

observation:

* all_player_info

* * armor_health: int

  * health: int
  * firearm: [bool, bool]
  * firearms_pool: [int, int]
  * range: int
  * position: bool 256x256, and two floats
  * inventory: int array, len=4

* * 

* map

  MultiBinary 256x256

* supply

  MultiDiscrete 256x256, 10

* safe_zone

  Box 256x256, float

action:

* choose_origin

  目前不选出生点

* move

  [float, float]

* stop

  bool

* abandon

  Discrete 10, and a count (Box)

* switch_firearm

  bool

* use_medicine

  MultiBinary 2

* use_grenade

  a bool and a float position

* attack

  a bool and a float position

调用 Agent：

从一组权重中调用。

指定一个被训练的 Agent 和一个陪练，将陪练当作后端，选手当作那个 PPO 的 Agent。

