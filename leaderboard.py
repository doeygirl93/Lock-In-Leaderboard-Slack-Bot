import pandas as pd
import requests
import os
import random
from datetime import datetime

# Configuration
SHEET_ID = "177DxdI-4m_hha9O1bGUmlYgKph6P0rFX6VIwgDIsBwE"
GID = "528146575"
SLACK_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_CHANNEL = "C0P5NE354"

def get_leaderboard():
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"
    df = pd.read_csv(url, skiprows=1, header=None)
    df = df.iloc[:, :7]
    df.columns = ['id', 'raw', 'date', 'days', 'tier', 'floor', 'final']
    df = df.dropna(subset=['id'])
    df = df.sort_values(by='final', ascending=False)

    today_str = datetime.now().strftime("%b %d, %Y")
    
    intros = [
        "_It’s 4:00 AM. Your desk is a chaotic landscape of empty mugs and sticky notes. You just solved a bug that’s been haunting you for three days, and for a brief moment, you feel like a god. Then you realize you forgot to hit 'Save.'_",
        "_The terminal window is the only light in the room. Your brain feels like it has 47 tabs open, and 3 of them are playing music you can’t find. You’re deep in the zone._",
        "_You’ve rewritten the same function four times. Each time it gets shorter, and each time you get more suspicious of why it’s actually working. Don't touch it. Just walk away._",
        "_The hardware is humming, the code is deploying, and you’re pretty sure you’ve reached a level of focus that shouldn't be scientifically possible. Welcome to the lock-in._",
        "_You just spent an hour debating the naming of a single variable. Is it 'data'? Is it 'payload'? Does it even matter anymore? You check the board to find your sanity._",
        "_The logic is finally clicking. It’s that rare moment where the vision in your head actually matches the pixels on the screen. It’s not magic—it’s just a lot of caffeine and stubbornness._",
        "_Your git commit messages have devolved from 'Fixed bug' to 'Please work' to 'I am crying.' But the build passed. That's all that matters._",
        "_It’s 4am. You’re 3 energy drinks deep, and your eyebags look even deeper, yet you just realized you've been editing the wrong file for twenty minutes. Suddenly, a notification pings..._",
        "_The consistent hum of your computer fan is the only thing keeping you sane. You haven't seen sunlight in 48 hours, but the code is finally compiling. You're locked in._",
        "_Why is CSS like this? You move one div and the entire header migrates to Mexico. You sigh, stretch, and check the board..._",
        "_The soft glow of your IDE is the only light in the room. You just spent three hours debugging a missing semicolon. You are transcending reality._",
        "_You’re staring at a StackOverflow thread from 2014. The solution is written in a language you don't speak, yet it's your only hope. Welcome to the grind._",
        "_A rogue bracket has ruined your life. You’ve questioned your career, your hobbies, and your favorite color. Then, finally... 'Process finished with exit code 0.'_",
        "_The mechanical keyboard clicks are echoing in the hallway. Your neighbors think you're a hacker; you're actually just trying to center a button. You check the stats..._"
    ]

    quotes = [
        "\"Coding is fun until the code starts doing what you told it to do instead of what you wanted it to do.\"",
        "\"The best error message is the one that never shows up.\"",
        "\"A language that doesn't affect your way of thinking about programming is not worth knowing.\"",
        "\"Computers are fast; developers are slow. Use the first to help the second.\"",
        "\"First, solve the problem. Then, write the code.\"",
        "\"If you think math is hard, try web design.\"",
        "\"Sleep is just a 404 Error for the human brain.\" — Sun Tzu, probably",
        "\"Why is code so good at just spontaneously not working?\" — Every Dev Ever",
        "\"The only way to learn a new programming language is by writing programs in it.\"",
        "\"If at first you don't succeed, call it version 1.0.\"",
        "\"Deleted code is debugged code.\""
    ]

    todays_grinders = df[df['days'] == 0]['id'].tolist()
    grinders_list = ", ".join([f"<@{uid}>" for uid in todays_grinders]) if todays_grinders else "The silence is deafening... I guess Nobody locked in today :sobspin:"

    msg = f"{random.choice(intros)}\n\n"
    msg += f":rac_woah:: *WELCOME TO THE LOCK-IN LEADERBOARD :feather-sleepover: | {today_str}* \n\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    msg += ":tw_sparkles: *TODAY’S GRINDERS (+1 Point)* :tw_sparkles:\n\n"
    msg += f"> {grinders_list}\n\n"
    msg += "Keep this up and you'll be flying to Chicago in no time!!! :blobby-airplane:\n\n\n"

    msg += "🏆 *THE TOP TIER GRINDERS* 🏆\n\n"

    def format_tier_group(title, emoji, tier_name):
        tier_df = df[df['tier'] == tier_name]
        if tier_df.empty: return ""
        section = f"{emoji} *{title}*\n"
        grouped = tier_df.groupby('final')
        for pts in sorted(grouped.groups.keys(), reverse=True):
            users = grouped.get_group(pts)['id'].tolist()
            user_mentions = ", ".join([f"<@{u}>" for u in users])
            section += f"• {user_mentions} — *{pts} pts*\n"
        return section + "\n"

    msg += format_tier_group("GOLD GRANDMASTERS (12+ pts)", "👑", "Gold")
    msg += format_tier_group("SILVER STRIVERS (7-11 pts)", "🥈", "Silver")
    msg += format_tier_group("BRONZE BEGINNERS (3-6 pts)", "🥉", "Bronze")

    msg += "\n"
    msg += f"📜 *Quote of the day:* {random.choice(quotes)}\n\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    msg += ":yay: _Missed a huddle? Get back in there to make sure you don't lose points!_\n\n"
    
    return msg

def post_to_slack(text):
    if not SLACK_TOKEN:
        print("Error: SLACK_BOT_TOKEN not found.")
        return
    response = requests.post(
        "https://slack.com/api/chat.postMessage",
        headers={"Authorization": f"Bearer {SLACK_TOKEN}"},
        json={"channel": SLACK_CHANNEL, "text": text}
    )
    if response.json().get("ok"):
        print("Successfully posted to Slack!")
    else:
        print(f"Slack Error: {response.json()}")

if __name__ == "__main__":
    content = get_leaderboard()
    post_to_slack(content)
