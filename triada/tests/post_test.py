import datetime
import pytest
from unittest.mock import patch, call, ANY
import pytest_asyncio
from sqlmodel import select
from triada.handlers.post import handle_post
from triada.schemas.table_models import Battles, Judges, BattlesPlayers


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

@pytest.mark.usefixtures('clear_db')
class TestPost:
    @pytest.mark.asyncio
    async def test_post(self, mock_vk_client, db_session):
        new_judges = [Judges(judge_id=456507851), Judges(judge_id=2, active_battles=1)]
        db_session.add_all(new_judges)
        await db_session.commit()
        post = await post_test({
            "text": """「 [id456507851|Gene Takovic] в роли «Дейдара» из «Наруто» 」
「 [id736580398|Roman Borsalinovich] в роли «Киллер Би» из «Наруто» 」

Время на пост: 24 часа""",
            "id": 1
        }, called=True, mock_vk_client=mock_vk_client)


        assert post == [call('https://api.vk.com/method/messages.send', params={
            'access_token': ANY,
            'peer_id': 2000000002,
            'message': 'Пост под судейством @id2(этого судьи)',
            'random_id': ANY, 'v': '5.199', 'attachment': None})]
        assert ((await db_session.exec(select(Battles).where(Battles.link == 1))).one() ==
                Battles(date=ANY, judge_id=2, time_out=datetime.timedelta(days=1), link=1, turn=0, status='active'))
        assert ((await db_session.exec(select(BattlesPlayers).where(BattlesPlayers.link == 1))).all() ==
                [BattlesPlayers(id=2,
                                turn=1,
                                universe='Наруто',
                                time_out=None,
                                hidden_action=None,
                                user_id=736580398,
                                character='Киллер Би',
                                result=None,
                                user_name='Roman Borsalinovich',
                                link=1),
                BattlesPlayers(id=1,
                               turn=0,
                               universe='Наруто',
                               time_out=ANY,
                               hidden_action=None,
                               user_id=456507851,
                               character='Дейдара',
                               result=None,
                               user_name='Gene Takovic',
                               link=1)])

