from triada.config.settings import GROUP_ID, JUDGE_CHAT_ID, FLOOD_CHAT_ID
from triada.api.vk_api import send_message
from triada.utils.patterns import MESSAGE_PATTERN
from triada.config.logg import logger
from triada.commands.judje_commands import VerdictCommand, CloseCommand, OpenCommand, PauseCommand, RePauseCommand, \
    ExtendCommand, SuspectsCommand, HelloCommand
from typing import Optional, Tuple
from sqlmodel import select
from triada.schemas.table_models import Battles, BattlesPlayers, Users
from triada.api.db_api import get_sessionmaker

#TODO: Написать адекватные описания для функций, вместе с типизацией


async def handle_message(message: dict) -> dict:
    """
    Функция, принимающая сообщение и определяющая, в какой обработчик его отправить.
    """
    #TODO: Заменить работу с словарём на работу с моделью Message
    if message["text"].startswith("."):
        logger.info(f"Received message: {message}")

        if pattern := await parse_message(message):
            command, link, text = pattern
            command, text = command.strip().lower(), text.strip()

            if message["peer_id"] == JUDGE_CHAT_ID:
                await handle_battle_commands(command, link, text, message)
                return {'response': 'ok', 'status': 200, 'message': 'Message from judges',
                        'peer_id': message['peer_id'], 'command': command}

            elif message["peer_id"] == FLOOD_CHAT_ID:
                await handle_user_commands(command, text, message)
                return {'response': 'ok', 'status': 200, 'message': 'Message from users', 'peer_id': message['peer_id'],
                        'command': command}

            elif message["peer_id"] == message['from_id']:
                await handle_user_commands(command, text, message)
                return {'response': 'ok', 'status': 200, 'message': 'Message from admin', 'peer_id': message['peer_id'],}

            else:
                return {'response': 'ok', 'status': 200, 'message': 'Message from ?', 'peer_id': message['peer_id'],
                        'command': command}

    return {'response': 'ok', 'status': 200, 'message': 'Not a command', 'peer_id': message['peer_id']}


async def handle_battle_commands(command: str, link: int, text: str, message: dict) -> None:
    """
    Обрабатывает команды, связанные с боями
    """
    commands = {
        'вердикт': lambda: VerdictCommand(link, text, message['peer_id']), #TODO: Добавить обработчик вложений
        'закрыть': lambda: CloseCommand(link, text, message['peer_id']),
        'открыть': lambda: OpenCommand(link, text, message['peer_id']),
        'пауза': lambda: PauseCommand(link, text, message['peer_id']),
        'возобновить': lambda: RePauseCommand(link, text, message['peer_id']),
        'продление': lambda: ExtendCommand(link, text, message['peer_id']),
        'подсудимые': lambda: SuspectsCommand(link=message['from_id'], text='', peer_id=message['peer_id']),
        'привет': lambda: HelloCommand(message['peer_id'])
    }

    if command_creator := commands.get(command.lower()):
        logger.info(f"Received command: {command}")
        try:
            await command_creator().execute()
            logger.debug(f"Command executed: {command}")
        except Exception as e:
            logger.error(f"Error executing command: {e}")
    return


async def parse_message(msg: dict) -> Optional[Tuple[str, str, str]]:
    """
    Разбирает сообщение на команду, ссылку и текст

    Returns:
        Tuple[команда, ссылка, текст] или None если сообщение не соответствует паттерну
    """
    if pattern := MESSAGE_PATTERN.match(msg['text']):
        return pattern.groups()
    return None


async def handle_user_commands(command: str, text: str, msg: dict) -> None:
    # commands = {
    #     'мои бои': lambda: MyBattlesCommand(link, text, message['peer_id']),  # TODO: Добавить обработчик вложений
    #     'бои': lambda: BattlesCommand(link, text, message['peer_id']),
    #     'команды': lambda: CommandsCommand(link, text, message['peer_id']),
    #     'моя стата': lambda: MyStatCommand(link, text, message['peer_id']),
    # }
    #
    # if command_creator := commands.get(command.lower()):
    #     logger.info(f"Executing command: {command}")
    #     try:
    #         text = await command_creator().execute()
    #         logger.debug(f"Command executed: {text}")
    #         return
    #     except Exception as e:
    #         logger.error(f"Error executing command: {e}")
    #         return

    match command:
        case 'мои бои':
            async_session = get_sessionmaker()
            async with async_session() as session:
                query = select(BattlesPlayers).where(BattlesPlayers.user_id == msg['from_id'])
                users_battles = (await session.exec(query)).all()
                if not users_battles:
                    text = """Ваши бои:\n\nУ вас нет активных боёв"""
                else:
                    text = "Ваши бои:\n\n" + "\n".join(f"https://vk.com/wall-{GROUP_ID}_{links.link}" for links in users_battles)
                await send_message(peer_id=msg['peer_id'],text= 'f')

        case 'бои':
            async_session = get_sessionmaker()
            async with async_session() as session:
                query = select(Battles).where(Battles.status == 'active')
                link = (await session.exec(query)).all()
                if not link:
                    text = """Активных боёв нет"""
                else:
                    links = "\n".join(f"https://vk.com/wall-{GROUP_ID}_{links.link}" for links in link)
                    text = f"Активные бои:\n\n{links}"
                await send_message(msg['peer_id'], text)

        case 'команды':
            text = "Команды:\n- мои бои\n- бои\n- команды"
            await send_message(msg['peer_id'], text)

        case 'моя стата':
            async_session = get_sessionmaker()
            async with async_session() as session:
                query = select(Users).where(Users.user_id == msg['from_id'])
                user = (session.exec(query)).first()
                if not user:
                    await send_message(msg['peer_id'], "Вы ещё не играли бои")

                else:
                    text = f"""Ваша статистика:

Количество боев: {sum([user.wins, user.technical_wins, user.loses, user.technical_loses])}
Количество побед: {user.wins}
Количество технических побед: {user.technical_wins}
Количество поражений: {user.loses}
Количество технических поражений: {user.technical_loses}
Ваш ММР: {user.mmr}
Фрагменты побед: {user.fragments_of_victories}
Фрагменты величия: {user.fragments_of_greatness}
Место в рейтинге: [В РАЗРАБОТКЕ]"""
            await send_message(msg['peer_id'], text)
    return