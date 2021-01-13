import requests

GPT_ENDPOINT = 'https://transformer.huggingface.co/autocomplete/distilgpt2/small'
GPT3_ENDPOINT = 'http://dd3a16430dd5.ngrok.io'
GPT_PARAMS = {'model_size': 'distilgpt2/small', 'top_p': 0.9, 'temperature': 0.9, 'max_time': 3}


async def gpt(message):
    if message.author.bot:
        return
    content = message.content
    if not content.startswith('.gpt'):
        return
    if content.startswith('.gpt3 '):
        query = content[6:]
        await message.channel.trigger_typing()
        response = requests.post(f'{GPT3_ENDPOINT}/message', json=query).json()
        await message.channel.send(response)
        return
    elif content.startswith('.gpt3clear'):
        requests.post(f'{GPT3_ENDPOINT}/clear')
        return

    # format context as a question
    context = content[5:]
    if not context:
        return
    context = context[0].upper() + context[1:]
    if context[-1] != '?':
        context += '?'
    context = f'Question: {context}\nAnswer:'

    await message.channel.trigger_typing()

    json = GPT_PARAMS.copy()
    json['context'] = context
    req = requests.post(GPT_ENDPOINT, json=json)
    req = req.json()

    # choose longest sentence that actually ends
    sentences = [x['value'] for x in req['sentences']]
    stopch = ['.', '!', '?', '\n']
    out = ''
    for sentence in sentences:
        match = [sentence.find(ch) for ch in stopch]
        match = [x for x in match if x != -1]
        if match and max(match) + 1 > len(out):
            out = sentence[: max(match) + 1]
            break

    await message.channel.send(out or sentences[0])


def setup(bot):
    bot.add_listener(gpt, 'on_message')
