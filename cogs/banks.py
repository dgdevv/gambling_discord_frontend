import nextcord, requests

from nextcord.ext import commands
from nextcord.ui import Button, View
from datetime import datetime

from main import GUILD_ID
import utils.view_btn as view_btn

class banks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(guild_ids=[GUILD_ID], description="거래내역을 확인합니다", name="거래내역")
    async def CheckTransactions(self, interaction: nextcord.Interaction):
        view = view_btn.TransactionView(user_id=interaction.user.id)
        await view.update_transactions(interaction)

    @nextcord.slash_command(guild_ids=[GUILD_ID], description="계좌를 생성합니다", name="계좌생성")
    async def CreateAccount(self, interaction: nextcord.Interaction):
        response = requests.post("http://localhost:8000/users/create_user/", json={"discord_user_id": str(interaction.user.id)})
        if response.status_code != 200 and response.json()['detail'] != "User already exists.":
            embed = nextcord.Embed(title="계좌 생성 오류", description="계좌를 생성할 수 없습니다", color=0xff0f0f)
            await interaction.response.send_message(embed=embed)
            return
        
        json_data = {   "bank_name": "3금융권 은행",
                        "discord_user_id": str(interaction.user.id),
                        "balance": 0 }
        response = requests.post("http://localhost:8000/banks/create_account/", json=json_data)
        if response.status_code == 200:
            embed = nextcord.Embed(title="계좌 생성", description="계좌가 성공적으로 생성되었습니다", color=0x04ff00)
            await interaction.response.send_message(embed=embed)
        elif response.json()['detail'] == "Account already exists.":
            embed = nextcord.Embed(title="계좌 생성 오류", description="이미 계좌가 존재합니다", color=0xff0f0f)
            await interaction.response.send_message(embed=embed)
        else:
            embed = nextcord.Embed(title="계좌 생성 오류", description="계좌를 생성할 수 없습니다", color=0xff0f0f)
            await interaction.response.send_message(embed=embed)

    @nextcord.slash_command(guild_ids=[GUILD_ID], description="남은 잔고를 확인합니다", name="잔고보기")
    async def CheckBalance(self, interaction: nextcord.Interaction):
        response = requests.get(f"http://localhost:8000/banks/get_balance/?discord_user_id={interaction.user.id}")
        if response.status_code == 200:
            embed = nextcord.Embed(title="잔고 확인", description=f"{interaction.user.mention}님의 잔고는 {response.json()['balance']:,} 원 입니다", color=0x04ff00)
            await interaction.response.send_message(embed=embed)
        else:
            embed = nextcord.Embed(title="잔고 확인 오류", description="잔고를 확인할 수 없습니다", color=0xff0f0f)
            await interaction.response.send_message(embed=embed)

    @nextcord.slash_command(guild_ids=[GUILD_ID], description="계좌간 송금을 합니다", name="송금하기")
    async def TransferMoney(self, interaction: nextcord.Interaction, recipient: nextcord.Member = nextcord.SlashOption(name="예금주", description="송금 받을 사람을 지정하세요"), amount: int = nextcord.SlashOption(name="송금액", min_value=1, description="송금할 금액을 입력하세요"), message: str = nextcord.SlashOption(name="메시지", description="송금 메시지를 입력하세요", required=False)):
        if recipient.bot:
            embed = nextcord.Embed(title="송금 오류", description="봇에게 송금할 수 없습니다", color=0xff0f0f)
            await interaction.response.send_message(embed=embed)
            return
        if recipient.id == interaction.user.id:
            embed = nextcord.Embed(title="송금 오류", description="자신에게 송금할 수 없습니다", color=0xff0f0f)
            await interaction.response.send_message(embed=embed)
            return
        if amount < 1:
            embed = nextcord.Embed(title="송금 오류", description="송금할 금액을 1원 이상 입력하세요", color=0xff0f0f)
            await interaction.response.send_message(embed=embed)
            return
        if message and len(message) > 10:
            embed = nextcord.Embed(title="송금 오류", description="메시지는 10자 이하로 입력하세요", color=0xff0f0f)
            await interaction.response.send_message(embed=embed)
            return

        json_data = {
            "sender_discord_id": str(interaction.user.id),
            "recipient_discord_id": str(recipient.id),
            "amount": amount,
            "message": message if message else "None" }
        response = requests.post("http://localhost:8000/banks/transfer_money/", json=json_data)
        if response.status_code == 200:
            embed = nextcord.Embed(title="송금 성공", description=f"{interaction.user.mention}님께서 {recipient.mention}님에게 {amount:,} 원을 송금하셨습니다", color=0x04ff00)
            embed.add_field(name=f"송금 한 사람 잔고", value=f"{response.json()['sender_balance']:,} 원")
            embed.add_field(name=f"송금 받은사람 잔고", value=f"{response.json()['receiver_balance']:,} 원")
            embed.add_field(name="메시지", value=message if message else "None", inline=False)
            await interaction.response.send_message(embed=embed)
        elif response.status_code == 400:
            if response.json()['detail'] == "Sender account does not exist.":
                embed = nextcord.Embed(title="송금 실패", description=f"{interaction.user.mention}님은 계좌가 존재하지 않습니다", color=0xff0f0f)
                await interaction.response.send_message(embed=embed)
            elif response.json()['detail'] == "Receiver account does not exist.":
                embed = nextcord.Embed(title="송금 실패", description=f"{recipient.mention}님은 계좌가 존재하지 않습니다", color=0xff0f0f)
                await interaction.response.send_message(embed=embed)
            elif response.json()['detail'] == "Insufficient balance.":
                embed = nextcord.Embed(title="송금 실패", description=f"{interaction.user.mention}님의 계좌 잔고가 부족합니다", color=0xff0f0f)
                await interaction.response.send_message(embed=embed)
            else:
                embed = nextcord.Embed(title="송금 실패", description="송금에 실패했습니다", color=0xff0f0f)
                await interaction.response.send_message(embed=embed)
        else:
            embed = nextcord.Embed(title="송금 실패", description="송금에 실패했습니다", color=0xff0f0f)
            await interaction.response.send_message(embed=embed)


def setup(bot):
    bot.add_cog(banks(bot))