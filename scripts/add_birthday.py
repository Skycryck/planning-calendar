"""
Ajoute une nouvelle entrée d'anniversaire dans Anniversaires.ics.

Usage : python scripts/add_birthday.py "Prénom Nom" "YYYY-MM-DD"
"""

import hashlib
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path


def generate_uid(name: str, birthdate: str) -> str:
    """Génère un UID déterministe basé sur le nom et la date."""
    raw = f"{name.lower().strip()}-{birthdate}"
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


def format_vevent(name: str, birthdate: str) -> str:
    dt = datetime.strptime(birthdate, "%Y-%m-%d")
    dt_end = dt + timedelta(days=1)
    now = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    uid = generate_uid(name, birthdate)

    return (
        "BEGIN:VEVENT\n"
        f"DTSTART;VALUE=DATE:{dt.strftime('%Y%m%d')}\n"
        f"DTEND;VALUE=DATE:{dt_end.strftime('%Y%m%d')}\n"
        "RRULE:FREQ=YEARLY\n"
        f"DTSTAMP:{now}\n"
        f"UID:{uid}@anniversaires.ics\n"
        "CLASS:PRIVATE\n"
        f"CREATED:{now}\n"
        f"LAST-MODIFIED:{now}\n"
        "SEQUENCE:0\n"
        "STATUS:CONFIRMED\n"
        f"SUMMARY:{name} - Anniversaire\n"
        "TRANSP:TRANSPARENT\n"
        "END:VEVENT"
    )


def add_to_ics(ics_path: Path, name: str, birthdate: str) -> None:
    content = ics_path.read_text(encoding="utf-8").rstrip()

    if not content.endswith("END:VCALENDAR"):
        print("✗ Format ICS invalide : END:VCALENDAR introuvable", file=sys.stderr)
        sys.exit(1)

    vevent = format_vevent(name, birthdate)

    # Insère le VEVENT juste avant END:VCALENDAR
    new_content = content.replace(
        "END:VCALENDAR",
        vevent + "\nEND:VCALENDAR"
    )

    ics_path.write_text(new_content + "\n", encoding="utf-8")
    print(f"✓ Ajouté : {name} (né·e le {birthdate})")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage : python add_birthday.py \"Prénom Nom\" \"YYYY-MM-DD\"", file=sys.stderr)
        sys.exit(1)

    name = sys.argv[1]
    birthdate = sys.argv[2]

    # Validation basique de la date
    try:
        datetime.strptime(birthdate, "%Y-%m-%d")
    except ValueError:
        print(f"✗ Date invalide : {birthdate} (format attendu : YYYY-MM-DD)", file=sys.stderr)
        sys.exit(1)

    repo_root = Path(__file__).resolve().parent.parent
    ics_path = repo_root / "Anniversaires.ics"

    if not ics_path.exists():
        print(f"✗ Fichier introuvable : {ics_path}", file=sys.stderr)
        sys.exit(1)

    add_to_ics(ics_path, name, birthdate)
