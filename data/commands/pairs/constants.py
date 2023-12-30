from uuid import uuid4

PAGINATION = str(uuid4())

list_of_pairs_message = """
📋 Here's a list of supported cryptocurrency pairs! 🚀 You can use /pairs <crypto_pair> to check support. \
For example: /pairs BTCUSDT. Happy trading! 🌟
"""

unsupported_pair_message = """
We're sorry, but this cryptocurrency is not supported at the moment. Please check our list for available options. 💔
"""

supported_pair_message = """
Great news! 🚀 We do support this cryptocurrency. You're all set to trade and explore its potential. Happy trading! 💪🌟 
"""
