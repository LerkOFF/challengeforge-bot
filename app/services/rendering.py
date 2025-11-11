def render_challenge(cid: int, title: str, body: str, tags: str, score: int) -> str:
    tags_fmt = " ".join(f"#{t.strip()}" for t in (tags or "").split(",") if t.strip())
    return (
        f"💡 <b>Челлендж #{cid}</b>\n"
        f"<b>{title}</b>\n\n"
        f"{body}\n\n"
        f"Теги: {tags_fmt}\n"
        f"Рейтинг: {score:+d}"
    )
