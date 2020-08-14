import asyncio
import datetime
import json
from typing import NamedTuple, List, Union

import aioschedule
import dateparser
import discord
from discord.ext import commands
from pytz import timezone

from util import config, guild_tools


class ScheduleEvent(NamedTuple):
    text: str
    timestamp: int
    channel: int
    mention: int
    other_timestamps: List[int]


def event_to_string(event: ScheduleEvent) -> str:
    time_str = central_time_str_from_utc(event.timestamp)
    return f'\'{event.text}\' in {guild_tools.get_channel(event.channel).name} at {time_str}'


def central_time_str_from_utc(timestamp: int) -> str:
    return datetime.datetime.fromtimestamp(timestamp).astimezone(timezone('US/Central')).strftime('%Y-%m-%d %I:%M:%S %p')


def default_timestamps(timestamp: int) -> List[int]:
    event_datetime = timezone('UTC').localize(datetime.datetime.utcfromtimestamp(timestamp))
    timestamps = [event_datetime - datetime.timedelta(minutes=30)]
    return list(map(lambda x: x.timestamp(), timestamps))


class Schedule(commands.Cog):
    schedule_events: List[ScheduleEvent]

    def __init__(self):
        self.schedule_events = []
        try:
            with open(config.schedule_file) as file:
                events_lists = json.load(file)
                for event in events_lists:
                    self.schedule_events.append(ScheduleEvent(*event))
        except FileNotFoundError:
            pass

    @commands.group()
    async def schedule(self, ctx: commands.Context):
        pass

    @schedule.command(name='add')
    async def add(self, ctx: commands.Context, text: str, mention: Union[discord.User, discord.Role], *, time: str):
        date = dateparser.parse(time, settings={'TIMEZONE': 'US/Central', 'RETURN_AS_TIMEZONE_AWARE': True}).astimezone(
            timezone('UTC')
        )
        event = ScheduleEvent(text, date.timestamp(), ctx.channel.id, mention.mention, default_timestamps(date.timestamp()))
        self.schedule_events.append(event)
        await ctx.channel.send(
            f'Registered event \'{text}\' for {mention.name} in '
            f'{ctx.channel.name} at {central_time_str_from_utc(date.timestamp())}'
        )
        self.sync_file()

    @schedule.command(name='list')
    async def list0(self, ctx: commands.Context):
        jobs = []
        for event in self.schedule_events:
            jobs.append(asyncio.create_task(ctx.send(event_to_string(event))))
        await asyncio.wait(jobs)

    @schedule.command(name='remove')
    async def remove(self, ctx: commands.Context, *, text: str):
        text_stripped = text.strip()

        removed = []
        for event in self.schedule_events:
            if event.text == text_stripped:
                removed.append(event)
                await ctx.channel.send(f'Removed event \'{text_stripped}\'')

        for event in removed:
            self.schedule_events.remove(event)

        self.sync_file()

    async def check(self):
        current_time = timezone('UTC').localize(datetime.datetime.utcnow()).timestamp()

        removed = []
        for event in self.schedule_events:
            if current_time >= event.timestamp:
                removed.append(event)
                await guild_tools.get_channel(event.channel).send(f'{event.mention} {event.text}')
                continue

            removed_other = []
            for other_timestamp in event.other_timestamps:
                if current_time >= other_timestamp:
                    removed_other.append(other_timestamp)
                    await guild_tools.get_channel(event.channel).send(
                        f'{event.mention} {event.text} at {central_time_str_from_utc(event.timestamp)}'
                    )

            for timestamp in removed_other:
                event.other_timestamps.remove(timestamp)

        for timestamp in removed:
            self.schedule_events.remove(timestamp)

        self.sync_file()

    async def report(self):
        jobs = []
        for event in self.schedule_events:
            jobs.append(
                asyncio.create_task(
                    guild_tools.get_channel(event.channel).send(
                        f'{event.mention} {event.text} at {central_time_str_from_utc(event.timestamp)}'
                    )
                )
            )
        await asyncio.wait(jobs)

    def sync_file(self):
        with open(config.schedule_file, 'w') as f:
            json.dump(self.schedule_events, f)


def setup(bot: commands.Bot):
    schedule = Schedule()
    bot.add_cog(schedule)

    aioschedule.every().minute.do(lambda: schedule.check())
    aioschedule.every().day.at('12:00').do(lambda: schedule.report())
