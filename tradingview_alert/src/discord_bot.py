from typing import Optional

import discord
from discord.ext import tasks
from discord import app_commands

import asyncio
import threading

from time import time

import msg
import stock_data


client = None
db_parser = None
schedule_channel = None


class DiscordBot(discord.Client):
    discord_guild_object: Optional[discord.Object] = None
    discord_response_chat_id: list = []
    discord_bot_token: str = ""
    schedule_second: int = 3

    next_alert_time: int = 0
    config: Optional[dict] = None

    alert_interval = 5
    alert_list: dict = {}
    alert_channel: Optional[int] = None
    is_closing = False  # 봇 종료 상태 추적

    def __init__(self,
            config: dict,
            schedule_second: int = 3,
            # intents: discord.Intents = discord.Intents.default()
            intents = discord.Intents().all()
    ) -> None:
        self.config =config

        server_id: int = self.config.get("server_id")
        self.discord_bot_token = self.config.get("token")
        self.discord_guild_object = discord.Object(id=server_id)
        self.discord_response_chat_id = self.config.get("channel_id")
        self.alert_channel = None  # 초기에는 None으로 설정, on_ready 이벤트 후에 설정됨
        self.alert_interval = self.config.get("alert_interval", 5)

        self.schedule_second = schedule_second

        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)


    async def setup_hook(self) -> None:
        self.tree.copy_global_to(guild=self.discord_guild_object)
        self.loop.create_task(self.schedular())
        print(f'Create in as {self.user} (ID: {self.user.id})')
        await self.tree.sync(guild=self.discord_guild_object)

        print("hook set done")


    # discord event
    def apply_event(self) -> None:
        @self.event
        async def close():
            print("Bot is closing...")
            # 진행 중인 작업 취소
            if self.schedular.is_running():
                self.schedular.cancel()

            # 디스코드 웹소켓 연결 종료
            # await super().close()
            await discord.Client.close(self)  # super() 대신 직접 클래스 메소드 호출
            print("Bot closed successfully!")

        @self.event
        async def on_ready():
            print(f'Logged in as {self.user} (ID: {self.user.id})')

            # 로그인 후 알림 채널 설정
            self.alert_channel = self.get_channel(self.discord_response_chat_id)
            if self.alert_channel:
                await self.alert_channel.send("initialize")
                print(f"알림 채널이 설정되었습니다: {self.alert_channel.name}")
            else:
                print(f"경고: 채널 ID {self.discord_response_chat_id}를 찾을 수 없습니다.")

            print('-----------------------------------')
            self.schedular.start()

        print("event set done")


    # discord bot command
    def apply_command(self) -> None:

        @self.tree.command()
        async def chk(interaction: discord.Interaction):
            print("chk command")
            await check_message(interaction)

        @self.tree.command()
        async def check(interaction: discord.Interaction):
            print("chk command")
            await check_message(interaction)

        @self.tree.command()
        async def stock(interaction: discord.Interaction, ticker: str = ""):
            print("stock command")
            await print_stock(interaction, ticker)




    async def safe_shutdown(self):
        # 봇을 안전하게 종료하는 메서드
        if self.is_closing:
            return  # 이미 종료 중이면 무시

        self.is_closing = True

        # 알림 채널이 설정되어 있으면 종료 메시지 전송
        if self.alert_channel:
            try:
                await self.alert_channel.send("봇이 종료됩니다")
            except Exception as e:
                print("디스코드 봇 종료 중 오류")
                print(e)

        # 스케줄러 정지
        if self.schedular.is_running():
            self.schedular.cancel()

        print("모든 작업을 정리하고 봇을 종료합니다...")

        # 지연 시간을 두고 봇 종료
        await asyncio.sleep(0.5)
        await discord.Client.close(self)  # super() 대신 직접 클래스 메소드 호출
        print("디스코드 봇 정리 완료")

    def start_bot(self):
        print("bot start")
        # 시그널 핸들러 등록
        self.run(self.discord_bot_token)

    # n초마다 돌면서 crash 상태인지 확인
    # @tasks.loop(seconds=5.0)
    @tasks.loop(seconds=1)
    async def schedular(self):
        # 종료 중이면 작업 중단
        if self.is_closing:
            return

        # if msg.msg_queue.is_empty() is False:
        #     msg_data = ""
        #     while True:
        #         tmp = msg.msg_queue.pop()
        #         if tmp is None:
        #             break
        #         msg_data += tmp
        #     if msg_data != "":
        #         msg.safe_string.append(msg_data)

        current_time = time()
        # self.alert_interval 초마다 메시지 전송
        if current_time >= self.next_alert_time or self.alert_interval < 0:
            self.next_alert_time = current_time + self.alert_interval
            # 채널이 여전히 None이면 다시 시도 (비정상적인 경우 대비)
            if self.alert_channel is None:
                print("알림 채널 재설정 시도")
                self.alert_channel = self.get_channel(self.discord_response_chat_id)
                if self.alert_channel:
                    await self.alert_channel.send("reconnected to channel")


            # SafeString에서 현재 메시지 읽기 (Read Lock 사용)
            message = msg.safe_string.get_value()
            if message is None or message == "":
                return

            if self.alert_interval < 0:
                msg.safe_string.set_value("")
            # 메시지 전송
            await self.alert_channel.send(message)



def discord_bot_shutdown():
    global client
    if not client:
        return

    # 비동기 함수를 동기적으로 실행하는 방법
    if client.loop and client.loop.is_running():
        # 실행 중인 이벤트 루프에 작업 추가
        future = asyncio.run_coroutine_threadsafe(client.safe_shutdown(), client.loop)
        try:
            # 최대 5초 동안 완료될 때까지 대기
            future.result(timeout=5)
        except asyncio.TimeoutError:
            print("디스코드 봇 종료 시간 초과")
        except Exception as e:
            print(f"디스코드 봇 종료 중 오류: {e}")
    else:
        # 루프가 실행 중이 아니면 새 루프에서 실행
        try:
            asyncio.run(client.safe_shutdown())
        except RuntimeError:
            # 이미 루프가 닫혀있거나 다른 문제가 있는 경우
            print("디스코드 봇 이벤트 루프 오류")

    # 클라이언트 참조 제거
    client = None
    print("디스코드 봇 종료 완료")


def discord_bot_start(conf: dict):
    global client

    # intents = discord.Intents.default()
    # intents = discord.Intents().all()
    client = DiscordBot(
        config=conf,
        schedule_second=5
    )

    client.apply_event()
    client.apply_command()

    client.start_bot()
    print("discord bot start done")


def discord_bot_run(conf: dict):
    global client

    if conf is None:
        print("discord bot config is None")
        return

    bot_use = conf["bot"]["use_discord"]
    if bot_use is False:
        print("discord bot is not used")
        return

    discord_conf: dict = conf.get("discord", None)
    if discord_conf is None:
        print("discord bot token is None")
        return

    discord_thread = threading.Thread(target=discord_bot_start, args=(discord_conf,))
    discord_thread.daemon = True
    discord_thread.start()




# import discord
async def check_message(interaction: discord.Interaction) -> None:
    msg.safe_string.set_value("")
    await interaction.response.send_message("alert check")

async def print_stock(interaction: discord.Interaction, ticker: str) -> None:
    stock_data_str = stock_data.get_stockdata_string(ticker.lower())
    await interaction.response.send_message(stock_data_str)



if __name__ == "__main__":
    main()
