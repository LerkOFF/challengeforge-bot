import random
from dataclasses import dataclass
from typing import Tuple
from app.storage.repositories.challenge_repo import ChallengeRepo

# Наборы кусочков — можно легко расширять
TOPICS = [
    "Telegram-бот для уведомлений",
    "парсер новостей",
    "CLI-утилита для разработчика",
    "мини-сервис мониторинга",
    "планировщик задач",
    "бот для отслеживания цен",
    "генератор отчётов",
    "инструмент резервного копирования",
]

STACKS = [
    "Python + aiogram",
    "Python + aiohttp",
    "Node.js + Telegraf",
    "Python + FastAPI",
    "C# + WPF (для клиента) + Python (для сервера)",
]

CONSTRAINTS = [
    "без внешней БД (только файл/SQLite)",
    "с кэшем на диске",
    "с ретраями при ошибках сети",
    "с логированием и простым конфигом .env",
    "c ограничением частоты запросов",
]

EXTRAS = [
    "экспорт результата в CSV/JSON",
    "уведомления в Telegram",
    "простая пагинация списка",
    "настройки через команды",
]

TAGS = ["bot", "parser", "cli", "monitoring", "report", "backup", "devtools"]


@dataclass
class GeneratedChallenge:
    title: str
    body: str
    tags: str  # csv


def _compose() -> GeneratedChallenge:
    topic = random.choice(TOPICS)
    stack = random.choice(STACKS)
    constraint = random.choice(CONSTRAINTS)
    extra = random.choice(EXTRAS)
    tag_sample = random.sample(TAGS, k=3)
    tags = ",".join(tag_sample)

    title = f"{topic} ({stack})"
    body = (
        f"Сделай {topic.lower()} на {stack}. "
        f"Требования: {constraint}; {extra}. "
        f"Оформи запуск и настройки максимально простыми."
    )

    return GeneratedChallenge(title=title, body=body, tags=tags)


async def ensure_challenge(repo: ChallengeRepo) -> Tuple[int, str, str, str]:
    """
    Генерирует челлендж, проверяет — есть ли уже такой (title+body) в БД.
    Если нет — создаёт. Возвращает (id, title, body, tags).
    """
    gen = _compose()
    existing = await repo.get_by_title_body(gen.title, gen.body)
    if existing:
        return existing  # (id, title, body, tags)

    new_id = await repo.create(gen.title, gen.body, gen.tags)
    return (new_id, gen.title, gen.body, gen.tags)
