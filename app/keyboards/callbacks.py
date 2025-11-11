import hmac
import hashlib
import re
from dataclasses import dataclass
from typing import Optional
from app.config import Config

# Формат: cf:<v>:<t>:...:sig
# v — версия, сейчас "1"
# t — тип: v (vote), s (save), n (new), p (page), noop
# Для краткости и лимита в 64 байта используем короткие теги.

PREFIX = "cf"
VERSION = "1"

# Максимальные значения — базовая валидация
MAX_ID = 2_147_483_647
MAX_PAGE = 10_000

@dataclass
class VotePayload:
    cid: int
    val: int  # 1 | -1

@dataclass
class SavePayload:
    cid: int

@dataclass
class PagePayload:
    list_id: str  # "my" | "top"
    page: int

# --- подпись ---
def _sign(raw: str) -> str:
    if not Config.CALLBACK_SECRET:
        return ""  # режим без подписи
    mac = hmac.new(Config.CALLBACK_SECRET.encode("utf-8"), raw.encode("utf-8"), hashlib.sha1).hexdigest()
    return mac[:6]  # короткая подпись

def _pack(parts: list[str], sign: bool = True) -> str:
    raw = ":".join(parts)
    if sign and Config.CALLBACK_SECRET:
        sig = _sign(raw)
        return f"{raw}:{sig}"
    return raw

def _verify(full: str) -> bool:
    if not Config.CALLBACK_SECRET:
        return True
    try:
        head, sig = full.rsplit(":", 1)
    except ValueError:
        return False
    return hmac.compare_digest(_sign(head), sig)

# --- encode ---
def encode_vote(challenge_id: int, value: int) -> str:
    # cf:1:v:<cid>:<val>[:sig]
    return _pack([PREFIX, VERSION, "v", str(challenge_id), str(value)])

def encode_save(challenge_id: int) -> str:
    # cf:1:s:<cid>[:sig]
    return _pack([PREFIX, VERSION, "s", str(challenge_id)])

def encode_new() -> str:
    # cf:1:n[:sig]
    return _pack([PREFIX, VERSION, "n"])

def encode_page(list_id: str, page: int) -> str:
    # cf:1:p:<list_id>:<page>[:sig]
    return _pack([PREFIX, VERSION, "p", list_id, str(page)])

def encode_noop() -> str:
    # без подписи, чтобы было максимально коротко
    return "cf:noop"

# --- decode ---
# Разрешаем как подписанные, так и неподписанные (на случай, если SECRET пуст)
VOTE_RE = re.compile(r"^cf:1:v:(-?\d+):(-?1)$")
SAVE_RE = re.compile(r"^cf:1:s:(-?\d+)$")
NEW_RE  = re.compile(r"^cf:1:n$")
PAGE_RE = re.compile(r"^cf:1:p:([a-z]+):(\d+)$")

def decode(data: str):
    # быстрый путь для noop
    if data == "cf:noop":
        return {"type": "noop"}

    # проверка подписи, если есть SECRET
    if Config.CALLBACK_SECRET:
        try:
            head, sig = data.rsplit(":", 1)
        except ValueError:
            return None
        if not _verify(data):
            return None
        payload = head
    else:
        payload = data

    # vote
    m = VOTE_RE.match(payload)
    if m:
        cid = int(m.group(1))
        val = int(m.group(2))
        if not (-MAX_ID <= cid <= MAX_ID):
            return None
        # val уже в {-1, 1} благодаря RE
        return {"type": "vote", "data": VotePayload(cid=cid, val=val)}

    # save
    m = SAVE_RE.match(payload)
    if m:
        cid = int(m.group(1))
        if not (-MAX_ID <= cid <= MAX_ID):
            return None
        return {"type": "save", "data": SavePayload(cid=cid)}

    # new
    if NEW_RE.match(payload):
        return {"type": "new"}

    # page
    m = PAGE_RE.match(payload)
    if m:
        list_id = m.group(1)
        page = int(m.group(2))
        if page < 1 or page > MAX_PAGE:
            return None
        if list_id not in ("my", "top"):
            return None
        return {"type": "page", "data": PagePayload(list_id=list_id, page=page)}

    return None
