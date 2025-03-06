from triada.commands.user_commands import MyBattlesCommand, BattlesCommand, CommandsCommand, MyStatCommand
from triada.config.settings import JUDGE_CHAT_ID, FLOOD_CHAT_ID
from triada.schemas.models import Message
from triada.utils.patterns import MESSAGE_PATTERN
from triada.config.logg import logger
from triada.commands.judge_commands import VerdictCommand, CloseCommand, OpenCommand, PauseCommand, RePauseCommand, \
    ExtendCommand, SuspectsCommand, GradeActivateCommand, update_mmr
from typing import Optional, Tuple
from triada.utils.redis_client import redis_client


async def handle_message(message: dict) -> dict:
    """
    Функция, принимающая сообщение и определяющая обработчик для этого сообщения

    Args:
        message: Словарь аргументов сообщения

            {text: Текст полученного сообщения,

            peer_id: Идентификатор чата, откуда пришло сообщение,

            from_id: Идентификатор того, кто отправил сообщение (Если сообщение из лс, то равен peer_id),

            date: Дата и время отправленного сообщения,

            attachments: Все прикреплённые к сообщению файлы (музыка, фото, видео)},

    Returns:
        Сконструированный словарь с информацией о том, какая команда была выполнена

    """
    message = Message(**message)
    text = "Not a command"
    command = None



    if message.text.startswith("."):
        logger.info(f"Received message: {message}")

        if pattern := await parse_message(message):
            command, link, text = pattern
            command, text = command.strip().lower(), text.strip()
            link = 0 if link is None else link
            if message.peer_id == JUDGE_CHAT_ID:
                #TODO: Добавить в return выше нормальный словарь
                await handle_battle_commands(command, link, text, message)
                text = "Message from judges"

            elif message.peer_id == FLOOD_CHAT_ID or message.peer_id == message.from_id:
                await handle_user_commands(command, message)
                text = "Message from judges"

            else:
                text = "Message from ?"
    if not command:
        user = f"user:{message.from_id}:state"
        state = await redis_client.get(user)
        if state and state.startswith("waiting for grade"):
            await redis_client.delete(user)
            data = await redis_client.get(user+':data')
            await update_mmr(message.text, data, int(state.split(' ')[-1]))
            text = "Update of mmr"


    return {'response': 'ok',
            'status': 200,
            'message': text,
            'peer_id': message.peer_id,
            "command": command}


async def parse_message(message: Message) -> Optional[Tuple[str, str, str]]:
    """
    Разбирает сообщение на команду, ссылку и текст

    Returns:
        Tuple[команда, ссылка, текст] или None если сообщение не соответствует паттерну
    """
    if pattern := MESSAGE_PATTERN.match(message.text):
        return pattern.groups()
    return None


#TODO: Написать адекватные описания для функций, вместе с типизацией
async def handle_battle_commands(command: str, link: int, text: str, message: Message) -> None:
    """
    Обрабатывает команды, связанные с боями
    """
    link = int(link)
    commands = {
        #TODO: Добавить проверку значений в базе данных, если к ней идёт обращение
        'вердикт': lambda: VerdictCommand(link, text, message.peer_id), #TODO: Добавить обработчик вложений
        'закрыть': lambda: CloseCommand(link, text, message.peer_id),
        'открыть': lambda: OpenCommand(link, text, message.peer_id),
        'пауза': lambda: PauseCommand(link, text, message.peer_id),
        'возобновить': lambda: RePauseCommand(link, text, message.peer_id),
        'продление': lambda: ExtendCommand(link, text, message.peer_id),
        'подсудимые': lambda: SuspectsCommand(message.peer_id, message.from_id),
        'оценка': lambda: GradeActivateCommand(message.peer_id, message.from_id, link)
        #TODO: Добавить команду оценки боя
    }

    if command_creator := commands.get(command.lower()):
        logger.info(f"Received command: {command}")
        try:
            await command_creator().execute()
            logger.debug(f"Command executed: {command}")
        except Exception as e:
            logger.error(f"Error executing command: {e}")
    return


async def handle_user_commands(command: str, message: Message) -> None:
    params = [message.peer_id, message.from_id]
    commands = {
        'мои бои': lambda: MyBattlesCommand(*params),
        'бои': lambda: BattlesCommand(*params),
        'команды': lambda: CommandsCommand(*params),
        'моя стата': lambda: MyStatCommand(*params),
    }

    if command_creator := commands.get(command.lower()):
        logger.info(f"Executing command: {command}")
        try:
            text = await command_creator().execute()
            logger.debug(f"Command executed: {text}")
        except Exception as e:
            logger.error(f"Error executing command: {e}")
    return