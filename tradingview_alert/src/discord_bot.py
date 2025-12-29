from typing import Optional

import discord
from discord.ext import tasks
from discord import app_commands

import asyncio
import threading

from time import time
from datetime import datetime

import msg
import stock_data
import alert_manager
import realtime_manager
from toggle_settings import toggle_settings


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

    next_tick_check_time: int = 0  # tick.json 체크 시간
    mention_id: int = 0  # alert 시 멘션할 사용자 ID

    realtime_show_channel_id: int = 0  # realtime 표시 채널 ID
    realtime_channel: Optional[discord.TextChannel] = None  # realtime 채널 객체
    next_realtime_update_time: int = 0  # realtime 업데이트 시간
    last_realtime_message_id: Optional[int] = None  # 마지막 realtime 메시지 ID
    last_realtime_update_minute: int = -1  # 마지막으로 업데이트한 분 (0~59)

    subalert_channel_id: int = 0  # subalert 채널 ID (phase, etc 등)
    subalert_channel: Optional[discord.TextChannel] = None  # subalert 채널 객체

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
        self.mention_id = self.config.get("mention_id", 0) or 0  # None이면 0으로 처리
        self.realtime_show_channel_id = self.config.get("realtime_show_channel_id", 0) or 0  # None이면 0으로 처리
        self.realtime_channel = None
        self.subalert_channel_id = self.config.get("subalert_channel_id", 0) or 0  # None이면 0으로 처리
        self.subalert_channel = None

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

            # realtime 채널 설정
            if self.realtime_show_channel_id > 0:
                self.realtime_channel = self.get_channel(self.realtime_show_channel_id)
                if self.realtime_channel:
                    print(f"Realtime 채널이 설정되었습니다: {self.realtime_channel.name}")
                    # 채널에서 봇이 작성한 마지막 메시지 찾기
                    await self.find_last_realtime_message()
                else:
                    print(f"경고: Realtime 채널 ID {self.realtime_show_channel_id}를 찾을 수 없습니다.")

            # subalert 채널 설정
            if self.subalert_channel_id > 0:
                self.subalert_channel = self.get_channel(self.subalert_channel_id)
                if self.subalert_channel:
                    print(f"Subalert 채널이 설정되었습니다: {self.subalert_channel.name}")
                else:
                    print(f"경고: Subalert 채널 ID {self.subalert_channel_id}를 찾을 수 없습니다.")

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

        @self.tree.command()
        async def alert(
            interaction: discord.Interaction,
            ticker: str,
            target_price: str,
            stop_loss: str,
            purchased_price: str = "",
            purchased_quantity: str = ""
        ):
            print("alert command")
            await set_alert(interaction, ticker, target_price, stop_loss, purchased_price, purchased_quantity)

        @self.tree.command()
        async def chka(interaction: discord.Interaction):
            print("chka command")
            await check_alert(interaction)

        @self.tree.command()
        async def adel(interaction: discord.Interaction, ticker: str):
            print("adel command")
            await delete_alert(interaction, ticker)

        @self.tree.command()
        async def realtime(interaction: discord.Interaction, tickers: str = ""):
            print("realtime command")
            await set_realtime(interaction, tickers)

        @self.tree.command()
        async def phtoggle(interaction: discord.Interaction, mode: str = ""):
            print("phtoggle command")
            await toggle_phase_alert(interaction, mode)


    async def find_last_realtime_message(self):
        """realtime 채널에서 봇이 작성한 마지막 메시지 찾기"""
        if not self.realtime_channel:
            return

        try:
            # 최근 메시지 100개 확인 (충분한 범위)
            async for message in self.realtime_channel.history(limit=100):
                # 봇이 작성한 메시지인지 확인
                if message.author.id == self.user.id:
                    self.last_realtime_message_id = message.id
                    print(f"기존 realtime 메시지를 찾았습니다: {message.id}")
                    return

            print("realtime 채널에 봇이 작성한 메시지가 없습니다.")
        except Exception as e:
            print(f"realtime 메시지 찾기 오류: {e}")

    async def update_realtime_channel(self):
        """realtime 채널에 메시지 업데이트"""
        # realtime 채널이 설정되지 않았거나 티커가 없으면 스킵
        if not self.realtime_channel or not realtime_manager.realtime_tickers:
            return

        # realtime 메시지 생성
        message = realtime_manager.get_realtime_message()
        if not message:
            return

        try:
            # 마지막 메시지가 있으면 수정, 없으면 새로 생성
            if self.last_realtime_message_id:
                try:
                    # 메시지 가져오기 및 수정
                    old_message = await self.realtime_channel.fetch_message(self.last_realtime_message_id)
                    await old_message.edit(content=message)
                except discord.NotFound:
                    # 메시지를 찾을 수 없으면 새로 생성
                    new_message = await self.realtime_channel.send(message)
                    self.last_realtime_message_id = new_message.id
            else:
                # 새 메시지 생성
                new_message = await self.realtime_channel.send(message)
                self.last_realtime_message_id = new_message.id

        except Exception as e:
            print(f"Realtime 채널 업데이트 오류: {e}")


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

        # alert 확인
        alert_manager.check_alerts()

        current_time = time()

        # 1분(60초)마다 tick.json 파일 체크 및 재로드
        if current_time >= self.next_tick_check_time:
            self.next_tick_check_time = current_time + 60  # 다음 체크 시간 설정 (60초 후)
            stock_data.check_and_reload_tick_data()

        # 매분 40초 이후에 단 한 번 realtime 채널 업데이트 (채널이 설정된 경우에만)
        if self.realtime_show_channel_id > 0:
            now = datetime.now()
            # 현재 초가 40초 이상이고, 현재 분이 마지막 업데이트 분과 다르면 실행
            if now.second >= 40 and now.minute != self.last_realtime_update_minute:
                self.last_realtime_update_minute = now.minute
                await self.update_realtime_channel()

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

            # discord용 phase_string에서 메시지 읽기
            phase_message = msg.phase_string_dc.get_value()

            # discord용 etc_string에서 메시지 읽기
            etc_message = msg.etc_string_dc.get_value()

            # discord용 mamacd_string에서 메시지 읽기 (mamacdalert)
            mamacd_message = msg.mamacd_string_dc.get_value()

            # discord용 mamacd_string_2에서 메시지 읽기 (mamacd)
            mamacd_message_2 = msg.mamacd_string_dc_2.get_value()

            # discord용 ob_string에서 메시지 읽기
            ob_message = msg.ob_string_dc.get_value()

            # alert 메시지 추가
            alert_message = alert_manager.get_alert_message()
            has_alert = False
            if alert_message:
                has_alert = True
                if message:
                    message += "\n" + alert_message
                else:
                    message = alert_message

            # alert 채널로 메시지 전송
            if message:
                # 메시지 전송 (alert가 있고 mention_id가 0이 아니면 멘션 추가)
                if has_alert and self.mention_id is not None and self.mention_id > 0:
                    mention_text = f"<@{self.mention_id}> "
                    await self.alert_channel.send(mention_text + message)
                else:
                    await self.alert_channel.send(message)

            # subalert 채널로 phase와 etc, mamacd, ob 메시지 전송
            # 토글 설정 확인
            if toggle_settings.is_phase_alert_enabled() and self.subalert_channel_id > 0 and self.subalert_channel:
                # mention 텍스트 생성
                mention_text = ""
                if self.mention_id is not None and self.mention_id > 0:
                    mention_text = f"\n<@{self.mention_id}>"

                # phase_message 전송
                if phase_message:
                    await self.subalert_channel.send(phase_message + mention_text)

                # etc_message 전송
                if etc_message:
                    await self.subalert_channel.send(etc_message + mention_text)

                # mamacd_message 전송 (mamacdalert)
                if mamacd_message:
                    await self.subalert_channel.send(mamacd_message + mention_text)

                # mamacd_message_2 전송 (mamacd)
                if mamacd_message_2:
                    await self.subalert_channel.send(mamacd_message_2 + mention_text)

                # ob_message 전송
                if ob_message:
                    await self.subalert_channel.send(ob_message + mention_text)

            # 전송 후 초기화
            if self.alert_interval < 0:
                msg.safe_string.set_value("")
                msg.phase_string_dc.set_value("")
                msg.etc_string_dc.set_value("")
                msg.mamacd_string_dc.set_value("")
                msg.mamacd_string_dc_2.set_value("")
                msg.ob_string_dc.set_value("")
            else:
                # 전송 후 discord용 phase_string과 etc_string 초기화 (한 번만 전송)
                msg.phase_string_dc.set_value("")
                msg.etc_string_dc.set_value("")
                msg.mamacd_string_dc.set_value("")
                msg.mamacd_string_dc_2.set_value("")
                msg.ob_string_dc.set_value("")



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

async def set_alert(
    interaction: discord.Interaction,
    ticker: str,
    target_price: str,
    stop_loss: str,
    purchased_price: str = "",
    purchased_quantity: str = ""
) -> None:
    success, message = alert_manager.set_alert(ticker, target_price, stop_loss, purchased_price, purchased_quantity)
    await interaction.response.send_message(message)

async def check_alert(interaction: discord.Interaction) -> None:
    message = alert_manager.clear_triggered_alerts()
    await interaction.response.send_message(message)

async def delete_alert(interaction: discord.Interaction, ticker: str) -> None:
    success, message = alert_manager.delete_alert(ticker)
    await interaction.response.send_message(message)

async def set_realtime(interaction: discord.Interaction, tickers: str) -> None:
    """
    /realtime 커맨드 핸들러
    - /realtime : 모든 티커 표시
    - /realtime ticker1 ticker2 ticker3 : 특정 티커 표시
    - /realtime off : realtime 표시 비활성화
    """
    # 입력값 처리
    tickers = tickers.strip()

    if tickers == "":
        # 모든 티커 표시
        all_tickers = list(stock_data.stock_data_dict.keys())
        success, message = realtime_manager.set_realtime_tickers(all_tickers)
    elif tickers.lower() == "off":
        # realtime 비활성화
        success, message = realtime_manager.set_realtime_tickers([])
    else:
        # 특정 티커 표시
        ticker_list = tickers.split()
        success, message = realtime_manager.set_realtime_tickers(ticker_list)

    await interaction.response.send_message(message)


async def toggle_phase_alert(interaction: discord.Interaction, mode: str) -> None:
    """
    /phtoggle 커맨드 핸들러 (국면 변경 알림)
    - /phtoggle : 현재 상태 표시
    - /phtoggle on : phase 알림 활성화
    - /phtoggle off : phase 알림 비활성화
    """
    mode = mode.strip().lower()

    if mode == "on":
        toggle_settings.set_phase_alert(True)
        message = "✅ Phase 알림이 활성화되었습니다."
    elif mode == "off":
        toggle_settings.set_phase_alert(False)
        message = "❌ Phase 알림이 비활성화되었습니다."
    else:
        # 현재 상태 표시
        current_status = toggle_settings.is_phase_alert_enabled()
        status_text = "활성화됨 ✅" if current_status else "비활성화됨 ❌"
        message = f"현재 Phase 알림 상태: {status_text}\n\n사용법:\n- /phtoggle on : 알림 활성화\n- /phtoggle off : 알림 비활성화"

    await interaction.response.send_message(message)


if __name__ == "__main__":
    main()
