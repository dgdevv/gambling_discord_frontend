import nextcord, requests

from datetime import datetime
from nextcord.ui import View, Button

class TransactionView(View):
    def __init__(self, user_id, page=0):
        super().__init__()
        self.user_id = user_id
        self.page = page
        self.is_responded = False
        self.total_transactions = 0

    async def interaction_check(self, interaction: nextcord.Interaction) -> bool:
        return interaction.user.id == self.user_id

    @nextcord.ui.button(label="이전", style=nextcord.ButtonStyle.red, custom_id="prev_page")
    async def prev_button(self, button: Button, interaction: nextcord.Interaction):
        if interaction.user.id != self.user_id:
            return
        if self.page == 0:
            return
        self.page - max(0, self.page - 1)
        await self.update_transactions(interaction)

    @nextcord.ui.button(label="다음", style=nextcord.ButtonStyle.green, custom_id="next_page")
    async def next_button(self, button: Button, interaction: nextcord.Interaction):
        if interaction.user.id != self.user_id:
            return
        response = requests.get(f"http://localhost:8000/banks/get_transaction_count/?discord_user_id={self.user_id}")
        if response.status_code == 200:
            self.total_transactions = response.json()['count']
        if self.page + 1 >= self.total_transactions:
            return
        
        self.page += 1
        await self.update_transactions(interaction)

    async def update_transactions(self, interaction: nextcord.Interaction):
        response = requests.get(f"http://localhost:8000/banks/get_transactions/?discord_user_id={self.user_id}&page={self.page}")
        if response.status_code == 200:
            embed = nextcord.Embed(title="송금 내역", description=f"<@{self.user_id}>님의 최근 송금 내역입니다", color=0x04ff00)
            json_data = response.json()
            timestamp = datetime.strptime(json_data[0]['timestamp'], '%Y-%m-%dT%H:%M:%S.%f').strftime('%Y년%m월%d일 %H시%M분%S초')
            embed.add_field(name=f"최근 송금 내역", value=f"송금 보낸사람: <@{json_data[0]['sender_id']}> | 송금 받은사람: <@{json_data[0]['receiver_id']}>\n송금 금액: **{json_data[0]['amount']:,}** 원 | 메시지: **{json_data[0]['message']}**\n송금 시간: {timestamp}", inline=False)
            
            response = requests.get(f"http://localhost:8000/banks/get_transaction_count/?discord_user_id={self.user_id}")
            if response.status_code == 200:
                self.total_transactions = response.json()['count']
            embed.set_footer(text=f"현재 거래내역 순서: {self.page + 1} | 총 거래내역 수 : {response.json()['count']}")
            
            if not self.is_responded:
                await interaction.response.send_message(embed=embed, view=self)
                self.is_responded = True
            else:
                await interaction.response.edit_message(embed=embed, view=self)

