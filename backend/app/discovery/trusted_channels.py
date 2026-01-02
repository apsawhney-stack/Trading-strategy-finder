"""
Trusted sources configuration.
User can edit this file to add/remove trusted channels and subreddits.
"""

# Trusted YouTube channels - results from these get a quality boost
# Format: "Channel Name": "YouTube Channel ID"
# To find Channel ID: View channel page source, search for "channelId"
TRUSTED_YOUTUBE_CHANNELS = {
    "tastytrade": "UCfMGjXY4el4ueVlYRMQVWJQ",
    "Option Alpha": "UCc4CZw0AnNPRPdpJoGQMsXg",
    "InTheMoney": "UCfMOHqxPRLCWqV1fZaAjF-g",
    "Theta Profits": "UCmVr1oU_PYVLZ4hHcjPGmRg",
    "SMB Capital": "UCE4CRLdLwXPBsmhNqU0G5Xw",
    "ProjectOption": "UCZ7sFfGqMLfDq3_m_zK97Ew",
    # Add your own channels here:
    # "Channel Name": "Channel ID",
}

# Trusted subreddits - ranked by quality for options strategies
TRUSTED_SUBREDDITS = [
    "thetagang",      # Premium selling strategies
    "options",        # General options
    "optionstrading", # Active community
    "Daytrading",     # Intraday strategies
]

# Quality boost for trusted sources (added to score)
TRUSTED_CHANNEL_BOOST = 20
TRUSTED_SUBREDDIT_BOOST = 15
