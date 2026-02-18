import pandas as pd
import requests
import os
import random
from datetime import datetime

# Configuration
SHEET_ID = "177DxdI-4m_hha9O1bGUmlYgKph6P0rFX6VIwgDIsBwE"
GID = "528146575"
SLACK_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_CHANNEL = "C0AAQJZCRCH" 

def get_leaderboard():
    # URL to pull the CSV
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"
    
    # We read the CSV and tell it explicitly to ignore the first row so we can set our own headers
    df = pd.read_csv(url, skiprows=1, header=None)
    
    # We only take the first 7 columns (A through G) to avoid ghost column errors
    df = df.iloc[:, :7]
    df.columns = ['id', 'raw', 'date', 'days', 'tier', 'floor', 'final']
    
    # Clean up: remove rows where ID is empty
    df = df.dropna(subset=['id'])
    
    # Sort by Final Score
    df = df.sort_values(by='final', ascending=False)

    # --- HACK CLUB STYLE MESSAGE BUILDING ---
    today_str = datetime.now().strftime("%b %d, %Y")
    
    intros = [
        "It’s 4am. You’re 3 energy drinks deep, and your eyebags look even deeper, yet you just realized you've been editing the wrong file for twenty minutes. Suddenly, a notification pings...",
        "The consistant hum of your computer fan is the only thing keeping you sane. You haven't seen sunlight in 48 hours, but the code is finally compiling. You're locked in.",
        "Why is CSS like this? You sigh, stretch, and check the board..."
    ]

    # Find today's grinders (Days Since == 0)
    todays_grinders = df[df['days'] == 0]['id'].tolist()
    grinders_list = ", ".join([f"<@{uid}>" for uid in todays_grinders]) if todays_grinders else "The silence is deafening... I guess Nobody locked in today :sobspin:"

    msg = f"{random.choice(intros)}\n\n"
    msg += f":rac_woah:: *WELCOME TO THE LOCK-IN LEADERBOARD :feather-sleepover: | {today_str}* \n\n"
    
    msg += ":tw_sparkles: *TODAY’S GRINDERS (+1 Point)* :tw_sparkles:\n"
    msg += f"{grinders_list}\n"
    msg += "Keep this up and you'll be flying to Chicago in no time!!! :blobby-airplane:\n\n"

    msg += "🏆 *THE TOP TEIR GRINDERS* 🏆\n"

    # Helper to group by points to handle TIES nicely
    def format_tier_group(title, emoji, tier_name):
        tier_df = df[df['tier'] == tier_name]
        if tier_df.empty: return ""
        
        section = f"{emoji} *{title}*\n"
        # Group by score so people with the same points are on one line
        grouped = tier_df.groupby('final')
        for pts in sorted(grouped.groups.keys(), reverse=True):
            users = grouped.get_group(pts)['id'].tolist()
            user_mentions = ", ".join([f"<@{u}>" for u in users])
            section += f"• {user_mentions} — *{pts} pts*\n"
        return section + "\n"

    msg += format_tier_group("GOLD GRANDMASTERS (12+ pts)", "👑", "Gold")
    msg += format_tier_group("SILVER STRIVERS (7-11 pts)", "🥈", "Silver")
    msg += format_tier_group("BRONZE BEGINNERS (3-6 pts)", "🥉", "Bronze")

    msg += "📜 *Quote of the day:* 'Sleep is just a 404 Error for the human brain.' — Sun Tzu, probably\n\n"
    msg += "--- \n"
    msg += ":yay: Missed a huddle? Get back in there to stop the point decay!"
    
    return msg

def post_to_slack(text):
    if not SLACK_TOKEN:
        print("Error: SLACK_BOT_TOKEN not found.")
        return

    # Using json= ensures Slack handles the emojis and formatting correctly
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