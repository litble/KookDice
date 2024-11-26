from itertools import combinations

class Card:
    def __init__(self, color, point):
        self.color = color
        self.point = point

    def to_str(self):
        color_name = ["方块", "梅花", "红桃", "黑桃"]
        point_name = ["J", "Q", "K", "A"]
        rep_str = color_name[self.color]
        if(self.point <= 8):
            rep_str += str(self.point + 2)
        else:
            rep_str += point_name[self.point - 9]
        return rep_str

type_dict = {
    0: "高牌",
    1: "一对",
    2: "两对",
    3: "三条",
    4: "顺子",
    5: "同花",
    6: "葫芦",
    7: "四条",
    8: "同花顺"
}

class FiveCards:
    def __init__(self, t, cards):
        self.t = t
        self.cards = cards
    
    def comp(self, C):
        if(self.t > C.t):
            return 1
        if(C.t > self.t):
            return -1
        for i in range(4, -1, -1):
            if(self.cards[i].point > C.cards[i].point):
                return 1
            if(self.cards[i].point < C.cards[i].point):
                return -1
        return 0
    
    def to_str(self):
        rep_str = type_dict[self.t] + " ( "
        for c in self.cards:
            rep_str += c.to_str() + " "
        rep_str += ")"
        return rep_str

# 同花
def is_flush(five_cards):
    s = five_cards[0].color
    for c in five_cards[1:]:
        if s != c.color:
            return False
    return True

# 顺子
def is_straight(five_cards):
    for i in range(4):
        if(five_cards[i+1].point != five_cards[i].point + 1):
            return False
    return True

def get_type(five_cards):
    straight = is_straight(five_cards)
    flush = is_flush(five_cards)
    if(straight and flush):
        return 8
    if(flush):
        return 5
    if(straight):
        return 4
    
    nums = [0] * 13
    for c in five_cards:
        nums[c.point] += 1
    #print(nums)
    max_freq = max(nums)
    if(max_freq == 1):
        return 0
    if(max_freq == 4):
        return 7
    if(max_freq == 3):
        if (2 in nums):
            return 6
        return 3
    if(nums.count(2) == 1):
        return 1
    return 2

async def get_max_score(seven_cards):
    max_cards = FiveCards(-1, [])
    for five_cards in combinations(seven_cards, 5):
        t = get_type(five_cards)
        now_cards = FiveCards(t, five_cards)
        if(now_cards.comp(max_cards) > 0):
            max_cards = now_cards
    return max_cards

# 单元测试
def main():
    pass

if(__name__ == '__main__'):
    main()