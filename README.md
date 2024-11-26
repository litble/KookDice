# 使用方式

在`./src/config.json`的`robot_token`填入你的kook机器人token，然后运行main.py即可。

# 指令

## .texas 德扑指令
- `.texas help` //指令列表
- `.texas clear` //清空所有参与者
- `.texas join [积分值]` //设置初始积分值并加入游戏，重复加入将改变顺位
- `.texas exit` //离开游戏
- `.texas order` //查看所有参与者和顺位，目前默认按照加入顺序排序
- `.texas setp [积分值]` //重设积分值，可以使用加减号来加减设置
- `.texas showp` //查看当前积分值
- `.texas bet [下注值]` //下注或加注
- `.texas fold` //盖牌
- `.texas perflop` //perflop阶段，为所有参与者发底牌
- `.texas flop` //flop阶段，发3张公共牌
- `.texas turn` //turn阶段，发第4张公共牌
- `.texas river` //river阶段，发第5张公共牌
- `.texas showdown` //亮牌，计算胜者，注池积分并自动重新洗牌
- `.texas shuffle` //清空所有抽牌并重新洗牌

**注意事项**：
- 牌堆并行化功能尚在开发中，目前仅支持同时运行一局游戏。
- 仅限娱乐与学习，游戏请勿涉及金钱往来。

**开发中事项**：
- 记录大小盲注和顺位提醒功能
- 优化注池，目前出现平局情况下的主边池逻辑和规则存在出入
- 牌堆按照频道并行化，每个频道内独立运行游戏
- 主持人功能：添加主持人注册功能，`clear`，`flop`，`turn`，`river`，`showdown`和`shuffle`功能仅限主持人运行，防止玩家误触发