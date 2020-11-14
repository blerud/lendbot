import csv
import logging
import seaborn as sns
import matplotlib.pyplot as plt

from io import StringIO, BytesIO
from collections import defaultdict
from discord import File
from discord.ext import commands
from discord.ext.commands import Context
# from util.config import POKERNOW_LOG_DIR

log = logging.getLogger(__name__)


def plot_stacks(sio: StringIO) -> BytesIO:
    """https://gist.github.com/suchir/9bf647000bd4727f9f501711405c1e2d
    """

    sns.set()
    reader = csv.reader(sio)
    lines = reversed([x[0] for x in reader])

    datapoints = defaultdict(list)
    buyin = defaultdict(float)

    idx = 0
    for row in lines:
        if any(x in row for x in ('approved', 'created', 'quits')):
            tokens = row[row.find('"')+1:].split(' ')
            name, amount = tokens[0], float(tokens[-1][:-1])
            if 'quits' in row:
                buyin[name] -= amount
                datapoints[name].append((idx, -buyin[name]))
            else:
                buyin[name] += amount
        if row.startswith('Player stacks: '):
            row = row[len('Player stacks: '):]
            groups = row.split(' | ')
            for group in groups:
                tokens = group.split(' ')
                name, amount = tokens[1][1:], float(tokens[-1][1:-1])
                datapoints[name].append((idx, amount - buyin[name]))
            idx += 1
    for points in datapoints.values():
        if points[-1][0] == idx:
            points.pop()

    plt.figure(figsize=(20, 10))
    for name, points in datapoints.items():
        xs, ys = zip(*points)
        plt.plot(xs, ys, label=name)
        plt.legend()

    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.clf()
    buf.seek(0)
    return buf


@commands.group(invoke_without_command=True)
async def pokernow(ctx: Context):
    await ctx.send(
        '''```
        .pokernow plot [attach pokernow log CSV file]
        ```'''
    )

    # r'\"(\w+(?:\s\w+)?) \@ (\w+)\" (joined|quits) the game with a stack of (\d+\.\d\d)'
    # df = pd.read_csv('poker_now_log.csv', parse_dates=True, infer_datetime_format=True)
    # username, uid, event_type, quantity
    # entry_exits = df.entry.str.extract(
    #     r'"(.+(?:.+)?)\s@\s(.+)"+ (joined|quits) the game with a stack of (\d+\.\d\d)'
    # ).dropna().iloc[::-1]
    # losing a buy in: The player "benjam @ laRAysvKgm" quits the game with a stack of 0.00.


@pokernow.command(name='plot')
async def plot_logs(ctx: Context):
    """Plot the attached pokernow CSV log file
    """
    try:
        log_attachment = ctx.message.attachments[0]
    except IndexError:
        await ctx.send('u need to attach the log file dumbass')
        return

    try:
        log.info(f'Plotting "{log_attachment.filename}"')
        log_data = await log_attachment.read()

        img = plot_stacks(StringIO(log_data.decode()))
        img_f = File(img, filename=log_attachment.filename.replace('.csv', '.png'))
        img.close()
        await ctx.send(file=img_f)

    except Exception as e:
        log.error(f'Error while parsing pokernow logs: "{e}"')


def setup(bot: commands.Bot):
    bot.add_command(pokernow)
