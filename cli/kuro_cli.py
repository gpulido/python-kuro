#!/usr/bin/env python

import kuro
import sys
import argparse
import logging

def action(args):
    gat = kuro.Gateway(args.port, configure = True)

    if args.command == 'on':
        gat.turn_on()
    elif args.command == 'off':
        gat.turn_off()
    elif args.command == 'volup':
        gat.volume_up()
    elif args.command == 'voldown':
        gat.volume_down()
    elif args.command == 'osdon':
        gat.osd_state_on()
    elif args.command == 'osdoff':
        gat.osd_state_off()
    elif args.command == 'muteon':
        gat.volume_mute(True)
    elif args.command == 'muteoff':
        gat.volume_mute(False)
    elif args.command == 'picturemuteon':
        gat.video_mute(True)
    elif args.command == 'picturemuteoff':
        gat.video_mute(False)
    else:
        print(gat.get_power_status())

def executeCommand(args):
    gat = kuro.Gateway(args.port)
    gat.executeCmd(args.command, args.parameter)
    

logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger()

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)
rootLogger.setLevel(logging.DEBUG)

parser = argparse.ArgumentParser(prog='kuro-cli')
parser.add_argument("port", type=str, help="serial port")
subparsers = parser.add_subparsers(help='sub-command help')

parser_action = subparsers.add_parser('action', help="Command to execute over the tv")
parser_action.add_argument("command", choices = ['on', 'off', 'volup', 'voldown', 'muteon','muteoff','osdon', 'osdoff','picturemuteon', 'picturemuteoff', 'else'], default = 'on')
parser_action.set_defaults(func=action)

parser_command = subparsers.add_parser('command', help="Command to execute over the device")
parser_command.add_argument("command", type=str, help="command to execute")
parser_command.add_argument("--parameter", type=str, default="", help="parameter for the command")
parser_command.set_defaults(func=executeCommand)

args = parser.parse_args()
args.func(args)









