import numpy as np
import scipy.linalg

NEGATIVE = ["Don't count on it.", "My reply is no.", "My sources say no.", "Outlook not so good.", "Very doubtful."]
NEUTRAL = [
    "Reply hazy, try again later.",
    "Ask again later.",
    "Better not tell you now.",
    "Cannot predict now.",
    "Concentrate and ask again.",
]
SLIGHT_POSITIVE = ["As I see it, yes.", "Most likely.", "Outlook good.", "Yes.", "Signs point to yes."]
STRONG_POSITIVE = ["It is certain.", "It is decidely so.", "Without a doubt.", "Yes - definitely.", "You may rely on it."]


def random_quantum(x):
    arr = np.array([ord(ch) for ch in x.lower()])
    science = scipy.linalg.circulant(arr)[:5].prod(axis=0)
    quantum = (science % 42069 == 25266).any()
    return quantum


async def eightball(message):
    if message.author.bot:
        return
    content, author = message.content, message.author.display_name
    if not content.startswith('.8ball'):
        return

    # Use quantum fluctuations in a split beam of light as a source of extra randomness
    if random_quantum(author):
        choices = NEUTRAL
    elif random_quantum(content):
        choices = STRONG_POSITIVE
    else:
        choices = NEGATIVE + NEUTRAL + SLIGHT_POSITIVE + STRONG_POSITIVE
    out = np.random.choice(choices)
    await message.channel.send(out)


def setup(bot):
    bot.add_listener(eightball, 'on_message')
