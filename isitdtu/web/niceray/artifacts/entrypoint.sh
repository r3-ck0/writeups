#!/bin/bash

rm /bin/sleep
rm /usr/bin/apt

INTERNAL_NETWORK="172.20.0.0/16"


iptables -F
iptables -t nat -F
iptables -X

iptables -P OUTPUT DROP
iptables -P INPUT ACCEPT


iptables -A OUTPUT -o lo -j ACCEPT
iptables -A INPUT -i lo -j ACCEPT


iptables -A OUTPUT -d $INTERNAL_NETWORK -j ACCEPT
iptables -A INPUT -s $INTERNAL_NETWORK -j ACCEPT


iptables -A OUTPUT -p udp --dport 53 -j ACCEPT
iptables -A OUTPUT -p tcp --dport 53 -j ACCEPT
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT


iptables -A OUTPUT -j DROP

exec "$@"

