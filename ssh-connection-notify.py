#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ssh-connection-notify - Script for Notifications successful about connect to SSH.

# Copyright © 2012 Denis 'Saymon21' Khabarov
# E-Mail: saymon at hub21 dot ru (saymon@hub21.ru)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3
# as published by the Free Software Foundation.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from os import getenv, system as system_exec
from os.path import exists as path_exists, isfile as file_exists
from socket import getfqdn, gethostname, error as SocketErrorException
from email.mime.text import MIMEText
from smtplib import SMTP, SMTPException
from datetime import datetime

try:
	from ipaddr import IPAddress, IPNetwork
	from yaml import load as loadconfig, YAMLError
except ImportError as errstr:
	print("\033[31m"+errstr+"\033[0m")
	exit(1)


def exclude_ip(ip, exclude_ips):
	if ip in exclude_ips:
		return True

def exclude_net(ip, nets):
	for net in nets:
		if IPAddress(ip) in IPNetwork(net):
			return True


def is_exclude(config,user, ip):
	if (config['users'][user].has_key('exclude_ips') and exclude_ip(ip, config['users'][user]['exclude_ips'])) or (config['users'][user].has_key('exclude_nets') and exclude_net(ip, config['users'][user]['exclude_nets'])):
		return True
	
def sendmail(config, recipient, message):
	try:
		msg = MIMEText(message)
		msg['Subject'] = 'Security notification ('+getfqdn(gethostname())+')'
		msg['From'] = config['smtp']['user']
		msg['To'] = recipient
		transport = SMTP(config['smtp']['serverhost'], config['smtp']['tcpport'],timeout=10)
		if config['smtp']['debug']:
			transport.set_debuglevel(1)
		transport.ehlo
		if config['smtp']['tls']:
			transport.starttls()
		transport.login(config['smtp']['user'], config['smtp']['password'])
		transport.sendmail(config['smtp']['user'], recipient, msg.as_string())
		transport.quit()
	except (SocketErrorException,SMTPException) as errmsg:
		if config['smtp']['debug']:
			print("Error, while sending message for %s: %s" % (recipient,errmsg))
			return None

def notify_by_email(config,recipient,message):
	if type(recipient) == str:
		sendmail(config,recipient,message)
	elif type(recipient) == list:
		for i in recipient:
			if type(i)==str:
				sendmail(config,i,message)		

def notify_wall(msg):
	if path_exists('/usr/bin/wall') and file_exists('/usr/bin/wall'):
		system_exec("echo '"+msg+"'|/usr/bin/wall")
			
def main():
	try:
		cfg=open("/etc/ssh/.ssh-connection-notify.yaml")
	except IOError as errstr:
		print("\033[31mERROR: "+errstr+"\033[0m")
		exit(1)
	
	try:
		config=loadconfig(cfg.read())
	except YAMLError as errstr:
		print("\033[31mERROR: "+errstr+"\033[0m")
		exit(1)
	
	_SSH_TTY=getenv("SSH_TTY")
	if _SSH_TTY:
		_SSH_MODE="SSH" 
	else: 
		_SSH_MODE="SFTP"
	
	_SSH_CONNECTION=getenv("SSH_CONNECTION")
	if _SSH_CONNECTION:
		ipaddr=_SSH_CONNECTION.split()[0]
		_LOGIN=getenv("USER")
		_TIME=datetime.utcnow().ctime()
		msg="On {TIME} {SSH_MODE} Authorization on {SERVERNAME} from user {USERNAME} with IP {IPADDR} successfully!".format(TIME=_TIME,SSH_MODE=_SSH_MODE,SERVERNAME=getfqdn(gethostname()),USERNAME=_LOGIN, IPADDR=ipaddr)
		if (_LOGIN in config['users'] and is_exclude(config, _LOGIN, ipaddr) is None and config['users'][_LOGIN].has_key('email')):
			notify_by_email(config, config['users'][_LOGIN]['email'], msg)
			notify_wall(msg)
		if not _LOGIN in config['users'] and config['notify_if_user_not_defined'] and config.has_key('notify_not_defined_to_email'):
			notify_by_email(config, config['notify_not_defined_to_email'], msg)
			notify_wall(msg)
				
if __name__ == "__main__":
	main()
