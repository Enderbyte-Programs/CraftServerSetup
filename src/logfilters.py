"""Filter functions to be used with the new logloader.py"""
import logutils

def permit_all(logline:logutils.LogEntry) -> bool:
    return True

def is_log_entry_a_chat_line(le:logutils.LogEntry) -> bool:
    return logutils.is_log_line_a_chat_line(le.data)