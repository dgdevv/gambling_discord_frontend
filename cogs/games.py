import nextcord
from nextcord.ext import commands
import requests
import random
import asyncio

from main import GUILD_ID

class games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
            
    @nextcord.slash_command(guild_ids=[GUILD_ID], description="도박을 합니다. (최소배율 1.75배, 최대배율 2.2배, 잭팟최대 315배)", name="도박하기")
    async def Gambling(self, interaction: nextcord.Interaction, amount: int = nextcord.SlashOption(name="배팅액", min_value=1000, description="배팅할 금액을 입력하세요")):
        # 확률 계산
        selected_range = random.choice([ (1, 5), (6, 15), (16, 30), (31, 45), (46, 55), (56, 65), (66, 75), (76, 85), (86, 95), (96, 100) ])
        chance = random.uniform(*selected_range)

        json_data = { "discord_user_id": str(interaction.user.id), "amount": amount, "chance": chance }
        response = requests.post("http://localhost:8000/discord/gambling/", json=json_data)
        
        if response.status_code == 400:
            if response.json()['detail'] == "Minimum gambling amount is 1000.": # 최소 배팅액이 1000원 미만인 경우
                embed = nextcord.Embed(title="배팅 오류", description="최소 배팅액은 1000원 입니다.", color=0xff0f0f)
                await interaction.response.send_message(embed=embed)
                return
            elif response.json()['detail'] == "Insufficient balance.": # 돈이 부족한 경우
                embed = nextcord.Embed(title="배팅 오류", description="돈이 부족합니다.", color=0xff0f0f)
                await interaction.response.send_message(embed=embed)
                return
            elif response.json()['detail'] == "Account does not exist.": # 계좌이 존재하지 않는 경우
                embed = nextcord.Embed(title="배팅 오류", description="계좌가 존재하지 않습니다.", color=0xff0f0f)
                await interaction.response.send_message(embed=embed)
                return
            elif response.status_code != 200:
                embed = nextcord.Embed(title="도박 오류", description="도박에 실패했습니다.", color=0xff0f0f)
                await interaction.response.send_message(embed=embed)
                return
        
        # 도박 결과를 가져옴
        new_balance = response.json()['new_balance']
        old_balance = response.json()['old_balance']

        embed = nextcord.Embed(title="도박 확률", description=f"{interaction.user.mention}의 도박 확률: **{chance:.2f}%** 준비 중...", color=0x04ff00)
        await interaction.response.send_message(embed=embed)
        await asyncio.sleep(2)

        profit_multiplier = ((new_balance - old_balance) / amount) + 1.00

        if profit_multiplier >= 4:
            title = "도박 결과"
            description = f"{interaction.user.mention}의 도박 성공! !!!!!**잭팟**!!!!!"
            color = 0xffff00
            info = f"배팅액: {amount:,} | 총 받는금액: {(new_balance - old_balance + amount):,}\n이득 금액: {(new_balance - old_balance):,} | 이득률: **{profit_multiplier:.2f}**배 | 현재 잔고: {new_balance:,}"
        elif new_balance > old_balance:
            title = "도박 결과"
            description = f"{interaction.user.mention}의 도박 성공!"
            color = 0x04ff00
            info = f"배팅액: {amount:,} | 총 받는금액: {(new_balance - old_balance + amount):,}\n이득 금액: {(new_balance - old_balance):,} | 이득률: **{profit_multiplier:.2f}**배 | 현재 잔고: {new_balance:,}"
        else:
            title = "도박 결과"
            description = f"{interaction.user.mention}의 도박 실패!"
            color = 0xff0f0f
            info = f"배팅액: {amount:,} | 손실: {amount:,} | 현재 잔고: {new_balance:,}"

        embed = nextcord.Embed(title=title, description=description, color=color)
        embed.add_field(name="도박 정보", value=info, inline=False)
        await interaction.followup.send(embed=embed)

def setup(bot):
    bot.add_cog(games(bot))