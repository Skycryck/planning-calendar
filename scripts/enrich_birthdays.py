"""
Enrichit le fichier Anniversaires.ics en ajoutant l'âge dans le titre.

- Lit Anniversaires.ics (source, maintenue à la main)
- Génère Anniversaires-enriched.ics (avec âges, souscrit par les clients)
- L'âge affiché = celui que la personne atteint dans l'année en cours
  (ex: en 2026, quelqu'un né en 1998 → "28 ans")
- Les dates avant 1970 sont ramenées à 2000 pour compatibilité Proton Calendar
"""

import re
import sys
from datetime import date
from pathlib import Path

SAFE_YEAR = 2000  # Année de remplacement pour les dates < 1970


def extract_birth_year(dtstart_line: str) -> int | None:
    """Extrait l'année de naissance depuis une ligne DTSTART;VALUE=DATE:YYYYMMDD."""
    match = re.search(r":(\d{4})\d{4}$", dtstart_line)
    return int(match.group(1)) if match else None


def rewrite_date_if_needed(line: str) -> str:
    """Si l'année est < 1970, la remplace par SAFE_YEAR."""
    match = re.search(r"(.*:)(\d{4})(\d{4})$", line)
    if match:
        year = int(match.group(2))
        if year < 1970:
            return f"{match.group(1)}{SAFE_YEAR}{match.group(3)}"
    return line


def enrich_summary(summary: str, age: int) -> str:
    """Remplace 'Nom - Anniversaire' par 'Nom - XX ans'."""
    if " - Anniversaire" in summary:
        return summary.replace(" - Anniversaire", f" - {age} ans")
    # Fallback : ajoute l'âge à la fin
    return f"{summary} ({age} ans)"


def process_ics(input_path: Path, output_path: Path) -> None:
    content = input_path.read_text(encoding="utf-8")
    current_year = date.today().year
    lines = content.splitlines()
    output_lines: list[str] = []

    birth_year: int | None = None

    for line in lines:
        if line.startswith("DTSTART;VALUE=DATE:"):
            birth_year = extract_birth_year(line)
            output_lines.append(rewrite_date_if_needed(line))

        elif line.startswith("DTEND;VALUE=DATE:"):
            output_lines.append(rewrite_date_if_needed(line))

        elif line.startswith("SUMMARY:") and birth_year is not None:
            age = current_year - birth_year
            original_summary = line[len("SUMMARY:"):]
            new_summary = enrich_summary(original_summary, age)
            output_lines.append(f"SUMMARY:{new_summary}")
            birth_year = None  # Reset pour le prochain VEVENT

        elif line.startswith("CLASS:PRIVATE"):
            continue  # Supprimé : Google Agenda masque les événements privés

        else:
            output_lines.append(line)

    output_path.write_text("\n".join(output_lines) + "\n", encoding="utf-8")
    print(f"✓ {output_path.name} généré ({current_year})")


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parent.parent
    source = repo_root / "Anniversaires.ics"
    output = repo_root / "Anniversaires-enriched.ics"

    if not source.exists():
        print(f"✗ Fichier source introuvable : {source}", file=sys.stderr)
        sys.exit(1)

    process_ics(source, output)
