import boto3
import discord
from discord.ext import commands
import logging
import os
import time

import credentials

log = logging.getLogger(__name__)

@commands.command(name='mc')
async def launch_server(ctx):
    client = boto3.client(
        'ec2',
        aws_access_key_id=credentials.ACCESS_KEY,
        aws_secret_access_key=credentials.SECRET_KEY,
        region_name=credentials.EC2_REGION
    )
    message = manage_server(client)
    await ctx.send(message)

def manage_server(client):
    returnString = 'ERROR'
    instanceIds = [credentials.INSTANCE_ID]
    response = client.describe_instances(InstanceIds = instanceIds)
    reservations = response['Reservations']
    reservation = reservations[0]
    instances = reservation['Instances']

    if len(instances) > 0:
        instance = instances[0]
        state = instance['State']
        stateName = state['Name']

        if (stateName == 'stopped') or (stateName == 'shutting-down'):
            returnString = start_server(client)
        elif stateName == 'running':
            returnString = instance['PublicIpAddress']
        else:
            returnString = 'ERROR'
    return returnString

def start_server(client):
    returnString = 'ERROR'
    instanceIds = [credentials.INSTANCE_ID]
    response = client.start_instances(InstanceIds = instanceIds)
    stateCode = 0

    while not (stateCode == 16):
        time.sleep(3)

        response = client.describe_instances(InstanceIds = instanceIds)
        reservations = response['Reservations']
        reservation = reservations[0]
        instances = reservation['Instances']
        instance = instances[0]
        state = instance['State']
        stateCode = state['Code']

    ipAddress = instance['PublicIpAddress']
    returnString = 'Server is starting, this may take a few minutes.\n' + ipAddress
    return returnString

def setup(bot):
    bot.add_command(launch_server)
