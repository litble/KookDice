import gaming.texas
from khl import Bot, Message

from configuration import JsonConfiguration
import gaming

params = JsonConfiguration("./data/config.json")
kook_bot = Bot(token=params["robot_token"])

def main():
    # 开机
    print("=====Bot Start=====")
    kook_bot.run()

# 开机测试指令
@kook_bot.command(name="hello", case_sensitive=False)
async def hello(msg: Message):
    await msg.reply("hello world!")

@kook_bot.command(name="texas", prefixes=[".", "/", "。"])
async def texas(msg: Message, *args):
    await gaming.texas.texas(msg, *args)

if(__name__ == '__main__'):
    main()