import pytest
from app.database import requests as rq
from app.database.models import User, Topic, Role, TopicAccess
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_add_user(db_session_fixture: AsyncSession):
    user = await rq.get_user(111)
    assert user is None

    user_exists = await rq.add_user(111)
    assert not user_exists

    user = await rq.get_user(111)
    await db_session_fixture.refresh(user)
    assert user is not None
    assert user.tg_id == 111
    assert user.role == Role.STUDENT

    user_exists_again = await rq.add_user(111)
    assert user_exists_again


@pytest.mark.asyncio
async def test_edit_user(db_session_fixture: AsyncSession):
    await rq.add_user(111)

    await rq.edit_user(
        tg_id=111,
        name="Тест Тестович",
        group="ТГ-123",
        age=20,
        username="test_user",
        city="Москва",
        univercity="МГУ",
        institute="Институт Математики",
        department="Кафедра Алгебры",
        stream="Математика",
        role=Role.STUDENT
    )

    user = await rq.get_user(111)
    await db_session_fixture.refresh(user)
    assert user.name == "Тест Тестович"
    assert user.group == "ТГ-123"
    assert user.age == 20
    assert user.username == "test_user"
    assert user.city == "Москва"
    assert user.univercity == "МГУ"
    assert user.institute == "Институт Математики"
    assert user.department == "Кафедра Алгебры"
    assert user.stream == "Математика"
    assert user.role == Role.STUDENT

    await rq.edit_user(
        tg_id=111,
        name="Тест Тестович2",
        group="-",
        age=21,
        username="test_user2",
        city="-",
        univercity="-",
        institute="-",
        department="-",
        stream="-",
        role=Role.TEACHER
    )
    user = await rq.get_user(111)
    await db_session_fixture.refresh(user)
    assert user.name == "Тест Тестович2"
    assert user.group is None
    assert user.city is None
    assert user.univercity is None
    assert user.institute is None
    assert user.department is None
    assert user.stream is None
    assert user.role == Role.TEACHER


@pytest.mark.asyncio
async def test_add_topic_and_access(db_session_fixture: AsyncSession):
    await rq.add_user(222)
    await rq.edit_user(tg_id=222, name="Преп", group=None, age=30, role=Role.TEACHER)

    topic = await rq.add_topic("Тема для доступа", 10, 222)
    await db_session_fixture.refresh(topic)
    assert topic.topic_name == "Тема для доступа"
    assert topic.questions_count == 10
    assert topic.topic_creator == 222

    access_rule1 = await rq.add_topic_access(topic.id, "group", "605-01z")
    await db_session_fixture.refresh(access_rule1)
    assert access_rule1.topic_id == topic.id
    assert access_rule1.access_type == "group"
    assert access_rule1.access_value == "605-01z"

    access_rule2 = await rq.add_topic_access(topic.id, "stream", "Программная инженерия")
    await db_session_fixture.refresh(access_rule2)
    access_rule3 = await rq.add_topic_access(topic.id, "open_to_all", "true")
    await db_session_fixture.refresh(access_rule3)

    rules = await rq.get_topic_access_rules(topic.id)
    for rule in rules:
        await db_session_fixture.refresh(rule)
    assert len(rules) == 3
    assert any(r.access_value == "605-01z" for r in rules)
    assert any(r.access_value == "Программная инженерия" for r in rules)
    assert any(r.access_type == "open_to_all" for r in rules)


@pytest.mark.asyncio
async def test_get_topics_for_user(db_session_fixture: AsyncSession):
    await rq.add_user(333)
    await rq.edit_user(tg_id=333, name="Преп2", group=None, age=35, role=Role.TEACHER)

    topic1 = await rq.add_topic("Тема Группа", 5, 333)
    await db_session_fixture.refresh(topic1)
    topic2 = await rq.add_topic("Тема Направление", 7, 333)
    await db_session_fixture.refresh(topic2)
    topic3 = await rq.add_topic("Тема Открытая", 8, 333)
    await db_session_fixture.refresh(topic3)
    topic4 = await rq.add_topic("Тема Скрытая", 10, 333)
    await db_session_fixture.refresh(topic4)
    
    await rq.add_topic_access(topic1.id, "group", "ГР-101")
    await rq.add_topic_access(topic1.id, "group", "ГР-102")

    await rq.add_topic_access(topic2.id, "stream", "ИнфоТех")
    await rq.add_topic_access(topic2.id, "institute", "ИТИС")

    await rq.add_topic_access(topic3.id, "open_to_all", "true")

    await rq.add_user(101)
    await rq.edit_user(tg_id=101, name="Студент1", group="ГР-101", age=20, univercity="Универ", institute="ИТИС", stream="ИнфоТех", department="Каф1")

    await rq.add_user(102)
    await rq.edit_user(tg_id=102, name="Студент2", group="ГР-200", age=21, univercity="Универ", institute="ГИ", stream="СоцГуманитарные", department="Каф2")

    await rq.add_user(103)
    await rq.edit_user(tg_id=103, name="Студент3", group="ГР-300", age=22, univercity="Универ", institute="Медицина", stream="Лечебное дело", department="Каф3")

    user1 = await rq.get_user(101)
    await db_session_fixture.refresh(user1)
    available_topics1 = await rq.get_topics_for_user(user1)
    for t in available_topics1:
        await db_session_fixture.refresh(t)
    assert len(available_topics1) == 3
    assert topic1 in available_topics1
    assert topic2 in available_topics1
    assert topic3 in available_topics1
    assert topic4 not in available_topics1

    user2 = await rq.get_user(102)
    await db_session_fixture.refresh(user2)
    available_topics2 = await rq.get_topics_for_user(user2)
    for t in available_topics2:
        await db_session_fixture.refresh(t)
    assert len(available_topics2) == 1
    assert topic3 in available_topics2
    assert topic1 not in available_topics2
    assert topic2 not in available_topics2
    assert topic4 not in available_topics2

    user3 = await rq.get_user(103)
    await db_session_fixture.refresh(user3)
    available_topics3 = await rq.get_topics_for_user(user3)
    for t in available_topics3:
        await db_session_fixture.refresh(t)
    assert len(available_topics3) == 1
    assert topic3 in available_topics3
    assert topic1 not in available_topics3
    assert topic2 not in available_topics3
    assert topic4 not in available_topics3

    creator = await rq.get_user(333)
    await db_session_fixture.refresh(creator)
    creator_topics = await rq.get_topics_by_creator(creator.tg_id)
    for t in creator_topics:
        await db_session_fixture.refresh(t)
    assert len(creator_topics) == 4
    assert topic1 in creator_topics
    assert topic2 in creator_topics
    assert topic3 in creator_topics
    assert topic4 in creator_topics