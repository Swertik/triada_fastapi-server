import datetime
from random import randint

import pytest
from unittest.mock import patch, call, ANY

from sqlalchemy import delete
from sqlmodel import select
from triada.handlers.post import handle_post
from triada.main import post_to_battles
from triada.schemas.table_models import Battles, Judges, BattlesPlayers, Users


@pytest.mark.asyncio
async def post_test(post: dict, called: bool = True, mock_vk_client = None):
    with patch('httpx.AsyncClient', return_value=mock_vk_client):
        response = await handle_post(post)

    if called:
        mock_vk_client.__aenter__.return_value.post.assert_called()
        call_args = mock_vk_client.__aenter__.return_value.post.call_args_list
        return call_args
    else:
        mock_vk_client.__aenter__.return_value.post.assert_not_called()
        return response


class TestPost:
    @pytest.mark.asyncio
    async def test_post(self, mock_vk_client_factory, db_session):
        db_session.add(Users(user_id=456507851,
                             technical_wins=0,
                             technical_losses=0,
                             fragments_of_victories=0,
                             skill_rating=0,
                             wins=0,
                             user_name='Gene Takovic',
                             losses=0,
                             mmr=100,
                             fragments_of_greatness=0))
        await db_session.commit()

        post = await post_test({
            "text": """🗡 • Тессеракт • 🗡
🏹 • ПТБ: Поединок • 🛡

「 [id456507851|Дейдара] [VS] [id736580398|Киллер Би] 」

I. 👤 — Участники игры — 👥:

「 [id456507851|Gene Takovic] в роли «Дейдара» из «Наруто» 」
「 [id736580398|Roman Borsalinovich] в роли «Киллер Би» из «Наруто» 」

II. 🃏 — Правила игры — ♠:

「 [id456507851|Дейдара]: Пик сил при жизни. Без С0.
Снаряжение: Каноничное. Без ранее заготовленной взрывчатки 」

「 [id736580398|Киллер Би] — Пик сил на момент ЧВВШ. В базовой форме быстрее противника в 1,5 раза, в покрове чакры Биджу в 2 раза. Биджудама только при полной манифестации Гьюки, с 3 круга постов.
Снаряжение: Каноничное 」

III. 📝 — Тонкости и детали — 📜:

• Скрытые действия: Разрешены •
• Развитость навыков: Присутствует •
• Уникальные условия: Общее количество и качество энергии приравнено и равно 100%. Любое взаимодействие исходит из разницы энергий. (Стрела с 10% энергии пробивает щит с 9% энергии и т.д.). Расстояние между оппонентами 40 метров, точку появления выбирает первый ходящий •

IV. 🏛 — Место проведения — 🌐:

• Описание локации: Под покровом ночи, когда небо усыпано бесчисленными звёздами, меж горных вершин струится серебряная лента реки. Её воды, как живые, скользят меж древних камней, обточенных веками, отражая холодный свет звёзд и создавая иллюзию магического свечения.
Тёмные силуэты гор возвышаются над долиной, их грозные пики тянутся ввысь, скрываясь в туманной дымке. Призрачный свет Млечного Пути мягко озаряет склоны, превращая их в таинственные владения древних духов. Трава и мох, укутанные ночной прохладой, дремлют, слушая вечную песнь горного ручья.
Кажется, что это место – граница миров. Здесь, в этой долине, время замедляет свой бег, растворяясь в шёпоте ветра и журчании воды. Может быть, стоит лишь на мгновение закрыть глаза, и перед тобой возникнет фигура странника, идущего по камням, или тень дракона, мелькнувшая на фоне далёких гор •
• Погодные условия: 15:00, +15°, ветер 5 м/с •

V. ⚙ — Условия сражения — 🔧 :

• Эрудиция: Каноничная •
• Тип битвы: Насмерть •
• Условия победы: Убийство оппонента •
• Время на пост: 24 часа •
• Порядок действий: [id456507851|Дейдара] -> [id736580398|Киллер Би] •""",
            "id": 124 # Не менять
        }, called=True, mock_vk_client=mock_vk_client_factory())




        assert post == [call('https://api.vk.com/method/messages.send', params={
            'access_token': ANY,
            'peer_id': 2000000002,
            'message': 'Пост под судейством @id2(этого судьи)',
            'random_id': ANY, 'v': '5.199', 'attachment': None})]
        assert ((await db_session.exec(select(Battles).where(Battles.link == 124))).first() ==
                Battles(date=ANY, judge_id=2, time_out=datetime.timedelta(days=1), link=ANY, turn=0, status='active'))
        assert ((await db_session.exec(select(BattlesPlayers).where(BattlesPlayers.link == 124))).all() ==
                [BattlesPlayers(id=ANY,
                                turn=1,
                                universe='Наруто',
                                time_out=None,
                                hidden_action=None,
                                user_id=736580398,
                                character='Киллер Би',
                                result=None,
                                user_name='Roman Borsalinovich',
                                link=124),
                BattlesPlayers(id=ANY,
                               turn=0,
                               universe='Наруто',
                               time_out=ANY,
                               hidden_action=None,
                               user_id=456507851,
                               character='Дейдара',
                               result=None,
                               user_name='Gene Takovic',
                               link=124)])
        assert ((await db_session.exec(select(Users).
                                      where((Users.user_id == 736580398) | (Users.user_id == 456507851)))).all() ==
                [Users(user_id=456507851,
                       technical_wins=0,
                       technical_losses=0,
                       fragments_of_victories=0,
                       skill_rating=0,
                       wins=0,
                       user_name='Gene Takovic',
                       losses=0,
                       mmr=100,
                       fragments_of_greatness=0),
                 Users(user_id=736580398,
                       technical_wins=0,
                       technical_losses=0,
                       fragments_of_victories=0,
                       skill_rating=0,
                       wins=0,
                       user_name='Roman Borsalinovich',
                       losses=0,
                       mmr=100,
                       fragments_of_greatness=0)])
