import requests

async def gpt(message):
    if message.author.bot:
        return
    if not message.content.startswith('.gpt'):
        return

    message = message.content[5:]
    if not message:
        return
    if message[-1] != '?':
        message += '?'
    message = f'Q: {message}\n A: '

    json = {
        'context': message,
        'model_size': 'gpt2/large',
        'top_p': 0.9,
        'temperature': 1,
        'max_time': 2
    }
    req = requests.post('https://transformer.huggingface.co/autocomplete/gpt2/large', json=json)
    req = req.json()

    sentences = [x['value'] for x in req['sentences']]
    stopch = ['.', '!', '?', '\n']
    out = sentences[0]
    for sentence in sentences:
        match = [sentence.find(ch) for ch in stopch]
        match = [x for x in match if x != -1]
        if match:
            out = sentence[:min(match)]
            break

    await message.channel.send(out)

def setup(bot):
    bot.add_listener(gpt, 'on_message')
