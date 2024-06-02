# **这个库现在包含的是 hack，具体细节在 https://blog.csdn.net/LLLZDQ/article/details/139397336**


# THUAI7 Agent Template (Python)

自研 SDK，不使用 async。（因为 AI 库兼容不好）

使用方法与正统 SDK 类似。样例代码：

```python
from agent.agent import Agent
from agent.position import Position
import logging
import time

# Define your token and server here
...

agent = Agent(token=token, server=server, logging_level=logging.INFO)

# Wait until connected
while not agent.is_ready():
    time.sleep(1)
   
# Logic here
while True:
    # Update informations
    agent._update()
    if agent.is_done():
        # Game finished
        break
    agent.move(Position[float](x, y))
    time.sleep(0.01)
```

创建的进程不会 block，会新建一个线程连接并收取信息，存放到 `agent._que` 里。需要在主程序中更新时，调用 `agent._update()` 即可把 `agent._que` 里新来的信息更新到 `agent` 的其他属性（`player`, `enemy` 等）。

