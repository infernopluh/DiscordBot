from discord.ext import commands
import json
import os

DATA_PATH = "data/users.json"

def get_data():
    if not os.path.exists(DATA_PATH):
        return {}
    with open(DATA_PATH) as f:
        return json.load(f)

def save_data(data):
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)

class Economy(commands.Cog):
    """Simple economy system: balance, daily, give, leaderboard."""

    def __init__(self, bot):
        self.bot = bot

    def get_user(self, user_id):
        data = get_data()
        if str(user_id) not in data:
            data[str(user_id)] = {"balance": 100}
            save_data(data)
        return data

    @commands.command()
    async def balance(self, ctx, member: commands.MemberConverter = None):
        member = member or ctx.author
        data = get_data()
        bal = data.get(str(member.id), {"balance": 100})["balance"]
        await ctx.send(f"{member.display_name} has ${bal}.")

    @commands.command()
    async def daily(self, ctx):
        data = get_data()
        user_id = str(ctx.author.id)
        if user_id not in data:
            data[user_id] = {"balance": 100}
        data[user_id]["balance"] += 50
        save_data(data)
        await ctx.send(f"{ctx.author.mention}, you got your daily $50! New balance: ${data[user_id]['balance']}.")

    @commands.command()
    async def give(self, ctx, member: commands.MemberConverter, amount: int):
        if amount < 0:
            await ctx.send("You can't give a negative amount!")
            return
        data = get_data()
        giver = str(ctx.author.id)
        receiver = str(member.id)
        if data.get(giver, {"balance": 100})["balance"] < amount:
            await ctx.send("You don't have enough money!")
            return
        data[giver]["balance"] -= amount
        if receiver not in data:
            data[receiver] = {"balance": 100}
        data[receiver]["balance"] += amount
        save_data(data)
        await ctx.send(f"{ctx.author.display_name} gave ${amount} to {member.display_name}.")

    @commands.command()
    async def leaderboard(self, ctx):
        data = get_data()
        sorted_users = sorted(data.items(), key=lambda x: x[1]["balance"], reverse=True)
        msg = "**Leaderboard:**\n"
        for i, (uid, info) in enumerate(sorted_users[:5], 1):
            user = await self.bot.fetch_user(int(uid))
            msg += f"{i}. {user.display_name}: ${info['balance']}\n"
        await ctx.send(msg)

def setup(bot):
    bot.add_cog(Economy(bot))
