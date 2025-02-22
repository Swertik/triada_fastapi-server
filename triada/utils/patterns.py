"""
Регулярные выражения для обработки сообщений и постов

MESSAGE_PATTERN - паттерн для обработки основного сообщения
BATTLE_PLAYERS_PATTERN - паттерн для определения игроков в битве
BATTLE_TIME_PATTERN - паттерн для определения времени на пост
BATTLE_HIDDEN_ACTION_PATTERN - паттерн для обработки скрытых действий
"""
import re


MESSAGE_PATTERN = re.compile(
    r'\.([А-Яа-я\s]+)(?:https://vk.com/wall-229144827_(\d+))?(.*)'
)

BATTLE_PLAYERS_PATTERN = re.compile(
    r"\[id(\d+)\|(.*?)\] в роли [\"«'](.*)[\"»'](?:.*)[\"«'](.*)[\"»']",
    flags=re.IGNORECASE
)

BATTLE_TIME_PATTERN = re.compile(
    r'Время на пост:\s*(\d*)'
)

BATTLE_HIDDEN_ACTION_PATTERN = re.compile(
    r'(?:СД|Скрытое \w+)\s+https://vk.com/wall-214293883_(\d+)\s+(.+)',
    flags=re.IGNORECASE
) 