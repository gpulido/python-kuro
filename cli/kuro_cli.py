#!/usr/bin/env python

import kuro
import sys
import argparse

def executeCommand(args):
    gat = kuro.Gateway(args.port)
    gat.executeCmd(args.command, args.parameter)


parser = argparse.ArgumentParser(prog='kuro-cli')
parser.add_argument("port", type=str, help="serial port")
parser.add_argument("command", type=str, help="command to execute")
parser.add_argument("parameter", type=str, default="", help="parameter for the command")
parser.set_defaults(func=executeCommand)
args = parser.parse_args()
args.func(args)









