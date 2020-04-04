import requests

GPT_ENDPOINT = 'https://transformer.huggingface.co/autocomplete/gpt2/large'
GPT_PARAMS = {'model_size': 'gpt2/large', 'top_p': 0.9, 'temperature': 1, 'max_time': 2}


async def gpt(message):
    if message.author.bot:
        return
    if not message.content.startswith('.gpt'):
        return

    # format context as a question
    context = message.content[5:]
    if not context:
        return
    if context[-1] != '?':
        context += '?'
    context = f'Q: {context}\n A: '

    await message.channel.trigger_typing()

    json = GPT_PARAMS.copy()
    json['context'] = context
    req = requests.post(GPT_ENDPOINT, json=json)
    req = req.json()

    # choose first sentence that actually ends
    sentences = [x['value'] for x in req['sentences']]
    stopch = ['.', '!', '?', '\n']
    out = sentences[0]
    for sentence in sentences:
        match = [sentence.find(ch) for ch in stopch]
        match = [x for x in match if x != -1]
        if match:
            out = sentence[: min(match)]
            break

    await message.channel.send(out)


def setup(bot):
    bot.add_listener(gpt, 'on_message')
