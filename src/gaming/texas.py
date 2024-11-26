from khl.card import CardMessage
from khl import Message, User

import asyncio
import random

from gaming.texas_utils import Card, get_max_score

help_message="""您想要查看[德州扑克（版本: 1.0)]的指令列表是吗？我知道了。
`.texas help` //指令列表
`.texas join [积分值]` //设置初始积分值并加入游戏，重复加入将改变顺位
`.texas exit` //离开游戏
`.texas order` //查看所有参与者和顺位，目前默认按照加入顺序排序
`.texas setp [积分值]` //重设积分值，可以使用加减号来加减设置
`.texas showp` //查看当前积分值
`.texas bet [下注值]` //下注或加注
`.texas fold` //盖牌

以下功能建议只由主持人操作：
`.texas clear` //清空所有参与者
`.texas perflop` //perflop阶段，为所有参与者发底牌
`.texas flop` //flop阶段，发3张公共牌
`.texas turn` //turn阶段，发第4张公共牌
`.texas river` //river阶段，发第5张公共牌
`.texas showdown` //亮牌，计算胜者，注池积分并自动重新洗牌
`.texas shuffle` //清空所有抽牌并重新洗牌

**注意**：
- 牌堆并行化功能尚在开发中，目前仅支持同时运行一局游戏。
- 仅限娱乐与学习，游戏请勿涉及金钱往来。
"""

class Deck:
    def __init__(self):
        self.cards = []
        self.shuffle()
    
    def set_cards(self):
        self.cards = []
        for color in range(4):
            for point in range(13):
                self.cards.append(Card(color, point))
        random.shuffle(self.cards)

    def shuffle(self):
        self.set_cards()

    def draw(self):
        return self.cards.pop()

class Player:
    def __init__(self, user: User, point=0):
        self.point = point
        self.id = user.id
        self.nickname = user.nickname
        self.bet = 0
        self.fold = False
        self.hand_card = (None, None)

    def reset(self):
        self.point += self.bet
        self.bet = 0
        self.fold = False
        self.hand_card = (None, None)

class AllPlayers:
    def __init__(self):
        self._lock = asyncio.Lock()
        self.players = []
        self.pub_cards = []
        self.deck = Deck()

    async def join(self, new_p):
        async with self._lock:
            new_player_list = []
            for p in self.players:
                if(p.id != new_p.id):
                    new_player_list.append(p)
            new_player_list.append(new_p)
            self.players = new_player_list
            rep_str = "玩家 " + str(new_p.nickname) + f" 加入游戏，积分为{str(new_p.point)}。"
            rep_str += "\nTips: \n使用`.texas exit`退出游戏。\n\
使用`.texas order`查看所有玩家顺位。\n\
使用`.texas setp [积分]`来重设自己的积分。\
决定开始时，使用`.texas perflop`发底牌。"
            return rep_str

    async def exit(self, user):
        async with self._lock:
            new_player_list = []
            for p in self.players:
                if(p.id != user.id):
                    new_player_list.append(p)
            self.players = new_player_list
            return "玩家 " + str(user.nickname) + " 退出游戏。"

    async def print_order(self):
        async with self._lock:
            rep_str = "当前的顺位为:\n"
            i = 0
            for p in self.players:
                i += 1
                rep_str += f"第{str(i)}位: " + p.nickname + " 注额: " + str(p.bet) + " 剩余积分: " + str(p.point)
                if(p.fold):
                    rep_str += "[已盖牌]"
                rep_str += "\n"
            return rep_str
        
    async def setp(self, user, new_point):
        async with self._lock:
            for p in self.players:
                if(p.id == user.id):
                    p.point = new_point
                    rep_str = "已将玩家 " + str(user.nickname) + " 的积分修改为" + str(p.point)
                    return rep_str
            return "您尚未加入游戏，可以使用`.texas join [初始积分]`命令加入游戏。"
        
    async def changep(self, user, new_point):
        async with self._lock:
            for p in self.players:
                if(p.id == user.id):
                    p.point += new_point
                    rep_str = "已将玩家 " + str(user.nickname) + " 的积分修改为" + str(p.point)
                    if(new_point < 0):
                        rep_str += "\n注意：这将导致您的积分变为负数。"
                    return rep_str
            return "您尚未加入游戏，可以使用`.texas join [初始积分]`命令加入游戏。"
        
    async def showp(self, user):
        async with self._lock:
            for p in self.players:
                if(p.id == user.id):
                    rep_str = "玩家 " + str(user.nickname) + " 的注额为" + str(p.bet) + " 剩余积分为" + str(p.point)
                    return rep_str
            return "您尚未加入游戏，可以使用`.texas join [初始积分]`命令加入游戏。"
        
    async def perflop(self, channel):
        async with self._lock:
            for p in self.players:
                card1 = self.deck.draw()
                card2 = self.deck.draw()
                p.hand_card = (card1, card2)
                await channel.send("玩家 " + str(p.nickname) + " ，您的底牌为:" + card1.to_str() + " " + card2.to_str(), temp_target_id=p.id)

    async def shuffle(self):
        async with self._lock:
            self.deck.shuffle()
            for p in self.players:
                p.reset()
            self.pub_cards = []

    async def public_card(self, channel, next_stage, num=1):
        async with self._lock:
            rep_str="新的公开牌: "
            for _ in range(num):
                card = self.deck.draw()
                self.pub_cards.append(card)
                rep_str += card.to_str() + " "
            rep_str += "\n当前公开牌: "
            self.pub_cards.sort(key=lambda card:card.point)
            for c in self.pub_cards:
                rep_str += c.to_str() + " "
            rep_str += "\nTips: \n使用`.texas order`获取所有玩家顺位。\n使用`.texas bet [下注值]`来下注。"
            rep_str += "\n使用`.texas fold`盖牌放弃。"
            rep_str += "\n使用`.texas "+ next_stage +"`进入下一阶段。"
            await channel.send(rep_str)
            for p in self.players:
                rep_str = "玩家 " + str(p.nickname) + "，您的底牌和公共牌合计如下:\n"
                cards = [p.hand_card[0], p.hand_card[1]]
                cards.extend(self.pub_cards)
                cards.sort(key=lambda card:card.point)
                for c in cards:
                    rep_str += c.to_str() + " "
                await channel.send(rep_str, temp_target_id=p.id)
    
    async def bet(self, user, betting):
        async with self._lock:
            for p in self.players:
                if(p.id == user.id):
                    p.bet += betting
                    p.point -= betting
                    rep_str = "玩家 " + str(user.nickname) + " 加注 " + str(betting) + "，当前总注值: " + str(p.bet)
                    rep_str += "\n剩余积分: " + str(p.point)
                    if(p.point < 0):
                        rep_str += " 注意：您的剩余积分为负数。"
                    return rep_str
            return "您尚未加入游戏，可等待游戏结束后使用`.texas join [初始积分]`命令加入游戏。"
    
    async def fold(self, user, channel):
        async with self._lock:
            remain_user = 0
            rep_str = None
            for p in self.players:
                if(p.id == user.id):
                    p.fold = True
                    rep_str = "玩家 " + str(user.nickname) + " 盖牌。"
                elif(not p.fold):
                    remain_user += 1
            if(rep_str is not None):
                await channel.send(rep_str)
            else:
                await channel.send("您尚未加入游戏，可等待游戏结束后使用`.texas join [初始积分]`命令加入游戏。")
            if(remain_user > 1):
                return False
            
            # 只剩一名玩家在场，结算胜利
            total_bet = 0
            winner_bet = 0
            for p in self.players:
                if(not p.fold):
                    winner_bet = p.bet
            for p in self.players:
                total_bet += min(p.bet, winner_bet)
                p.bet -= min(p.bet, winner_bet)
            for p in self.players:
                if(not p.fold):
                    rep_str = "恭喜玩家 " + str(p.nickname) + " 留到了最后。能坚持到胜利的确令人钦佩，但及时撤退的勇气也同样是值得赞美的品质。\n"
                    rep_str += "玩家 " + str(p.nickname) + " 赢得了共计"+ str(total_bet)+"积分。"
                    p.point += total_bet
                    break
            rep_str += "目前场上积分：\n"
            for p in self.players:
                p.reset()
                rep_str += str(p.nickname) + ": " + str(p.point) + "\n"
            self.deck.shuffle()
            self.pub_cards = []
            rep_str += "已重新洗牌，要开始下一局吗？\n"
            rep_str += "Tips:使用`.texas perflop`命令重新发牌。"
            await channel.send(rep_str)
            return True
    
    async def showdown(self, channel):
        async with self._lock:
            rep_str = ""

            #============公布底牌并计算最大牌型==============
            winner_cards = None
            winner_id = []
            for p in self.players:
                if(p.fold): #跳过盖牌玩家
                    continue
                rep_str += "玩家 " + str(p.nickname) + " 的底牌为: " + p.hand_card[0].to_str() + " " + p.hand_card[1].to_str() + "，"
                cards = [p.hand_card[0], p.hand_card[1]]
                cards.extend(self.pub_cards)
                cards.sort(key=lambda card:card.point)
                max_cards = await get_max_score(cards)
                rep_str += "最大牌型: " + max_cards.to_str() + "\n"

                if(len(winner_id) < 1):
                    winner_id = [p.id]
                    winner_cards = max_cards
                else:
                    comp = max_cards.comp(winner_cards)
                    if(comp > 0):
                        winner_id = [p.id]
                        winner_cards = max_cards
                    elif(comp == 0):
                        winner_id.append(p.id)

            await channel.send(rep_str)

            #============计算注池分配==============
            # TODO: 目前平局情况下分配没有处理ALL IN的情况
            rep_str = ""
            if(len(winner_id) == 1):
                total_bet = 0
                winner_bet = 0
                for p in self.players:
                    if(p.id in winner_id):
                        winner_bet = p.bet
                for p in self.players:
                    total_bet += min(p.bet, winner_bet)
                    p.bet -= min(p.bet, winner_bet)
                for p in self.players:
                    if(p.id in winner_id):
                        rep_str += "恭喜玩家 " + str(p.nickname) + " 成为胜者。摘得胜利桂冠需要的……不止有运气。\n"
                        rep_str += "玩家 " + str(p.nickname) + " 赢得了共计"+ str(total_bet)+"积分。"
                        p.point += total_bet
                        break
            else:
                total_bet = 0
                for p in self.players:
                    if(p.id not in winner_id):
                        total_bet += p.bet
                        p.bet = 0
                _ = len(winner_id)
                for p in self.players:
                    if(p.id in winner_id):
                        get_bet = total_bet // _
                        _ -= 1
                        p.point += get_bet
                        rep_str += "玩家 " + str(p.nickname) + " 成为胜者，赢得了共计"+ str(get_bet)+"积分。\n"
            await channel.send(rep_str)
                
            #============初始化==============
            rep_str = "目前场上积分：\n"
            for p in self.players:
                p.reset()
                rep_str += str(p.nickname) + ": " + str(p.point) + "\n"
            self.deck.shuffle()
            self.pub_cards = []
            rep_str += "已重新洗牌，要开始下一局吗？\n"
            rep_str += "Tips:使用`.texas perflop`命令重新发牌。"
            await channel.send(rep_str)

    async def clear(self):
        async with self._lock:
            self.players = []
            self.pub_cards = []
            self.deck.shuffle()

# ======================公共内存区===================

stage_lock = asyncio.Lock()
stage = "start"

all_players = AllPlayers()

def stage_error_message():
    all_stages = ["start", "perflop", "flop", "turn", "river", "showdown"]
    for i in range(5):
        if(stage == all_stages[i]):
            return "当前正处于" + stage + "阶段，如果您想进入下一阶段，应使用`.texas " + all_stages[i+1] + "`命令。"

async def texas(msg: Message, *args):
    global stage, stage_lock
    #print(args)
    if(len(args) < 1):
        return
    arg0 = args[0].lower()
    if(arg0 == 'clear'):
        async with stage_lock:
            stage = "start"
        all_players.clear()
        await msg.ctx.channel.send("已清除所有加入游戏的玩家")
    elif(arg0 == 'help'):
        await msg.ctx.channel.send(help_message)
    elif(arg0 == 'join'):
        async with stage_lock:
            if(stage != "start"):
                await msg.reply("当前处于游戏中场！请使用`.texas shuffle`命令收回已发牌并洗牌后，再加入新玩家！")
                return
        if(len(args) >= 2 and args[1].isdigit()):
            new_p = Player(msg.author, int(args[1]))
        else:
            new_p = Player(msg.author, 0)
        rep_str = await all_players.join(new_p)
        await msg.reply(rep_str)
    elif(arg0 == 'exit'):
        rep_str = await all_players.exit(msg.author)
        await msg.reply(rep_str)
    elif(arg0 == 'order'):
        rep_str = await all_players.print_order()
        await msg.ctx.channel.send(rep_str)
    elif(arg0 == 'setp'):
        if(len(args) >= 2):
            if(args[1][0] == '+'):
                arg1 = args[1][1:]
                if(arg1.isdigit()):
                    rep_str = await all_players.changep(msg.author, int(arg1))
                    await msg.reply(rep_str)
            elif(args[1][0] == '-'):
                arg1 = args[1][1:]
                if(arg1.isdigit()):
                    rep_str = await all_players.changep(msg.author, -int(arg1))
                    await msg.reply(rep_str)
            elif(args[1].isdigit()):
                rep_str = await all_players.setp(msg.author, int(args[1]))
                await msg.reply(rep_str)
    elif(arg0 == 'showp'):
        rep_str = await all_players.showp(msg.author)
        await msg.reply(rep_str)
    elif(arg0 == 'perflop'):
        async with all_players._lock:
            if(len(all_players.players) < 1):
                await msg.ctx.channel.send("参与玩家人数不足！请使用`.texas join [初始积分]`加入游戏。")
                return
        async with stage_lock:
            if(stage != "start"):
                await msg.reply(stage_error_message())
                return
            stage = "perflop"
        await all_players.perflop(msg.ctx.channel)
        await msg.ctx.channel.send("所有底牌发放完毕。\n Tips:\n使用`.texas order`查看行动顺位。\n使用`.texas bet [注值]`进行下注或加注。\n使用`.texas flop`进入下一阶段。")
    elif(arg0 == 'flop'):
        async with stage_lock:
            if(stage != "perflop"):
                await msg.reply(stage_error_message())
                return
            stage = "flop"
        await all_players.public_card(msg.ctx.channel, "turn", 3)
    elif(arg0 == 'turn'):
        async with stage_lock:
            if(stage != "flop"):
                await msg.reply(stage_error_message())
                return
            stage = "turn"
        await all_players.public_card(msg.ctx.channel, "river", 1)
    elif(arg0 == 'river'):
        async with stage_lock:
            if(stage != "turn"):
                await msg.reply(stage_error_message())
                return
            stage = "river"
        await all_players.public_card(msg.ctx.channel, "showdown", 1)
    elif(arg0 == 'showdown'):
        async with stage_lock:
            if(stage != "river"):
                await msg.reply(stage_error_message())
                return
            stage = "start"
            await all_players.showdown(msg.ctx.channel)
    elif(arg0 == 'shuffle'):
        async with stage_lock:
            stage = "start"
        await all_players.shuffle()
        rep_str = "已收回所有下注和发牌，并重新洗牌完毕！" + await all_players.print_order()
        rep_str += "\n开始新一局游戏吧！"
        await msg.ctx.channel.send(rep_str)
    elif(arg0 == 'bet'):
        if(len(args) >= 2 and args[1].isdigit()):
            rep_str = await all_players.bet(msg.author, int(args[1]))
            await msg.ctx.channel.send(rep_str)
    elif(arg0 == 'fold'):
        restart = await all_players.fold(msg.author, msg.ctx.channel)
        if(restart):
            async with stage_lock:
                stage = "start"