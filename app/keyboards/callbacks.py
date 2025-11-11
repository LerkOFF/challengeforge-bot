import hmac
import hashlib
import re
from dataclasses import dataclass
from typing import Optional
from app.config import Config

# Формат: cf:1:<type>:...[:sig]
PREFIX = "cf"
VERSION = "1"

MAX_ID = 2_147_483_647
MAX_PAGE = 10_000

# --- payloads ---

@dataclass
class VotePayload:
    cid: int
    val: int  # 1 | -1

@dataclass
class SavePayload:
    cid: int

@dataclass
class SaveNoteDecisionPayload:
    cid: int
    decision: str  # 'y' | 'n'

@dataclass
class PagePayload:
    list_id: str  # "my" | "top"
    page: int

@dataclass
class NotePayload:
    cid: int  # конкретный challenge_id

# --- подпись ---

def _sign(raw: str) -> str:
    if not Config.CALLBACK_SECRET:
        return ""
    mac = hmac.new(Config.CALLBACK_SECRET.encode("utf-8"), raw.encode("utf-8"), hashlib.sha1).hexdigest()
    return mac[:6]

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

# --- encoders ---

def encode_vote(challenge_id: int, value: int) -> str:
    return _pack([PREFIX, VERSION, "v", str(challenge_id), str(value)])

def encode_save(challenge_id: int) -> str:
    return _pack([PREFIX, VERSION, "s", str(challenge_id)])

def encode_new() -> str:
    return _pack([PREFIX, VERSION, "n"])

def encode_page(list_id: str, page: int) -> str:
    return _pack([PREFIX, VERSION, "p", list_id, str(page)])

def encode_noop() -> str:
    return "cf:noop"

# --- Новые: заметки ---

def encode_save_decision(challenge_id: int, decision: str) -> str:
    # cf:1:sn:<cid>:<y|n>
    return _pack([PREFIX, VERSION, "sn", str(challenge_id), decision])

def encode_note(challenge_id: int) -> str:
    # cf:1:nt:<cid>
    return _pack([PREFIX, VERSION, "nt", str(challenge_id)])

def encode_note_list() -> str:
    # cf:1:nl
    return _pack([PREFIX, VERSION, "nl"])

# --- decoders (regex для неподписанной части) ---

VOTE_RE = re.compile(r"^cf:1:v:(-?\d+):(-?1)$")
SAVE_RE = re.compile(r"^cf:1:s:(-?\d+)$")
NEW_RE  = re.compile(r"^cf:1:n$")
PAGE_RE = re.compile(r"^cf:1:p:([a-z]+):(\d+)$")
SN_RE   = re.compile(r"^cf:1:sn:(-?\d+):(y|n)$")
NT_RE   = re.compile(r"^cf:1:nt:(-?\d+)$")
NL_RE   = re.compile(r"^cf:1:nl$")

def decode(data: str):
    if data == "cf:noop":
        return {"type": "noop"}

    # подпись
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

    m = VOTE_RE.match(payload)
    if m:
        cid = int(m.group(1))
        val = int(m.group(2))
        if not (-MAX_ID <= cid <= MAX_ID):
            return None
        return {"type": "vote", "data": VotePayload(cid=cid, val=val)}

    m = SAVE_RE.match(payload)
    if m:
        cid = int(m.group(1))
        if not (-MAX_ID <= cid <= MAX_ID):
            return None
        return {"type": "save", "data": SavePayload(cid=cid)}

    m = SN_RE.match(payload)
    if m:
        cid = int(m.group(1))
        decision = m.group(2)
        if not (-MAX_ID <= cid <= MAX_ID):
            return None
        return {"type": "save_decision", "data": SaveNoteDecisionPayload(cid=cid, decision=decision)}

    if NEW_RE.match(payload):
        return {"type": "new"}

    m = PAGE_RE.match(payload)
    if m:
        list_id = m.group(1)
        page = int(m.group(2))
        if page < 1 or page > MAX_PAGE:
            return None
        if list_id not in ("my", "top"):
            return None
        return {"type": "page", "data": PagePayload(list_id=list_id, page=page)}

    m = NT_RE.match(payload)
    if m:
        cid = int(m.group(1))
        if not (-MAX_ID <= cid <= MAX_ID):
            return None
        return {"type": "note", "data": NotePayload(cid=cid)}

    if NL_RE.match(payload):
        return {"type": "note_list"}

    return None
