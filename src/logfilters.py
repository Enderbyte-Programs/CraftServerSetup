"""Filter functions to be used with the new logloader.py"""
import logutils
import re

def permit_all(logline:logutils.LogEntry) -> bool:
    return True

def is_log_entry_a_chat_line(le:logutils.LogEntry) -> bool:
    return logutils.is_log_line_a_chat_line(le.data)

def ip_addresses_with_attached_player(le:logutils.LogEntry) -> bool:
    return len(re.findall(r"\s[A-Za-z]+\s[\[|\(]\/[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:|\s[A-Za-z0-9_]+\[\/[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:",le.data)) > 0

def has_joinorleave(le:logutils.LogEntry) -> bool:
    return len(re.findall(r' \S* joined the game| \S* left the game',le.data)) > 0

def is_logentry_a_command(l:logutils.LogEntry) -> bool:
    return len(re.findall(r"[a-zA-Z0-9_]+\sissued server command: .*",l.data)) > 0

def player_rename(l:logutils.LogEntry) -> bool:
    return len(re.findall(r"\S+ \(formerly known as \S+\)",l.data)) > 0