"""
src/utils/documentation.py

Living research documentation for the thesis project. Three append-only
markdown documents under reports/advisor_notes/, plus helpers that mirror the
log_decision() pattern already used in the notebooks.

    findings_log.md    What we found. Chronological empirical discoveries,
                       each with: what we did, what we found (with numbers),
                       why it matters, and what (if anything) surprised us.

    open_questions.md  Things noticed but parked, so we do not forget them.
                       Each with: the question, where it came up, why we did
                       not resolve it now, and the trigger for revisiting.

    thesis_journal.md  The narrative. A high-level research diary: where the
                       project is going, what is working, what is worrying.
                       The helpers seed the first entries, but ongoing entries
                       are meant to be written by hand -- this is reflection,
                       not generated output.

Design rules:
  - Append-only. We never silently rewrite history.
  - Idempotent on ID. Re-running a seeding cell will not duplicate entries.
  - Human-readable. These are documents you read, not data you parse.
  - resolve_open_question() is the single in-place edit; it flips a Status
    line inside one uniquely-headed block and prints the change for review.

Usage from a Colab notebook (after mounting Drive and adding the repo to path):

    from src.utils.documentation import (
        init_documents, log_finding, add_open_question,
        resolve_open_question, add_journal_entry,
        view_findings, view_open_questions, view_journal,
    )
"""

from pathlib import Path
import datetime

THESIS_ROOT = Path('/content/drive/MyDrive/phd_thesis')
ADVISOR_NOTES = THESIS_ROOT / 'reports' / 'advisor_notes'

FINDINGS_LOG = ADVISOR_NOTES / 'findings_log.md'
OPEN_QUESTIONS = ADVISOR_NOTES / 'open_questions.md'
THESIS_JOURNAL = ADVISOR_NOTES / 'thesis_journal.md'

EM_DASH = '\u2014'

_HEADERS = {
    FINDINGS_LOG: (
        '# Findings Log\n\n'
        'Chronological record of empirical discoveries. Append-only. Each\n'
        'entry records what we did, what we found (with numbers), why it\n'
        'matters, and what (if anything) surprised us.\n\n'
        'Seeded and appended via `src/utils/documentation.py::log_finding`.\n'
    ),
    OPEN_QUESTIONS: (
        '# Open Questions\n\n'
        'Things noticed but deliberately parked, so we do not forget them.\n'
        'Each entry carries a Status line: OPEN or RESOLVED. Resolve via\n'
        '`resolve_open_question(...)`, or by editing the Status line by hand.\n\n'
        'Seeded and appended via `src/utils/documentation.py`.\n'
    ),
    THESIS_JOURNAL: (
        '# Thesis Journal\n\n'
        'High-level research diary: where the project is going, what is\n'
        'working, what is worrying. The helpers seed the first entries, but\n'
        'ongoing entries are meant to be written by hand at session\n'
        'boundaries -- this is reflection, not generated output.\n'
    ),
}


def _today() -> str:
    return datetime.date.today().isoformat()


def _ensure_file(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(_HEADERS[path])


def _already_has(path: Path, marker: str) -> bool:
    return path.exists() and marker in path.read_text()


def init_documents() -> None:
    """Create the three documents with headers if they do not already exist."""
    for path in (FINDINGS_LOG, OPEN_QUESTIONS, THESIS_JOURNAL):
        existed = path.exists()
        _ensure_file(path)
        print(f'  {"exists " if existed else "created"}: {path}')


def log_finding(finding_id: str, title: str, what_we_did: str,
                what_we_found: str, why_it_matters: str,
                surprised: str = '', context: str = '') -> None:
    """Append an empirical finding. Idempotent on finding_id."""
    _ensure_file(FINDINGS_LOG)
    marker = f'## {finding_id} {EM_DASH}'
    if _already_has(FINDINGS_LOG, marker):
        print(f'[FINDING SKIPPED] {finding_id} already logged.')
        return
    entry = (
        f'\n## {finding_id} {EM_DASH} {title}\n'
        f'*Logged {_today()}'
        + (f' | context: `{context}`' if context else '')
        + '*\n\n'
        f'**What we did.** {what_we_did}\n\n'
        f'**What we found.** {what_we_found}\n\n'
        f'**Why it matters.** {why_it_matters}\n\n'
    )
    if surprised:
        entry += f'**What surprised us.** {surprised}\n\n'
    with open(FINDINGS_LOG, 'a') as f:
        f.write(entry)
    print(f'[FINDING LOGGED] {finding_id}: {title}')


def add_open_question(question_id: str, question: str, context: str,
                      why_parked: str, revisit_when: str) -> None:
    """Append a parked question with status OPEN. Idempotent on question_id."""
    _ensure_file(OPEN_QUESTIONS)
    marker = f'## {question_id} {EM_DASH}'
    if _already_has(OPEN_QUESTIONS, marker):
        print(f'[QUESTION SKIPPED] {question_id} already logged.')
        return
    entry = (
        f'\n## {question_id} {EM_DASH} {question}\n'
        f'*Raised {_today()} | context: `{context}`*\n\n'
        f'**Status:** OPEN\n\n'
        f'**Why parked.** {why_parked}\n\n'
        f'**Revisit when.** {revisit_when}\n\n'
    )
    with open(OPEN_QUESTIONS, 'a') as f:
        f.write(entry)
    print(f'[QUESTION LOGGED] {question_id}: {question[:70]}...')


def resolve_open_question(question_id: str, resolution: str) -> None:
    """Flip a question's Status from OPEN to RESOLVED, in place.

    Matches the unique '## {question_id} --' block and replaces the first
    '**Status:** OPEN' that follows it. Prints the change for review. This is
    the one place we edit history; everything else is append-only.
    """
    if not OPEN_QUESTIONS.exists():
        print('[RESOLVE FAILED] open_questions.md does not exist yet.')
        return
    text = OPEN_QUESTIONS.read_text()
    header = f'## {question_id} {EM_DASH}'
    start = text.find(header)
    if start == -1:
        print(f'[RESOLVE FAILED] {question_id} not found.')
        return
    next_hdr = text.find('\n## ', start + 1)
    end = next_hdr if next_hdr != -1 else len(text)
    block = text[start:end]
    if '**Status:** OPEN' not in block:
        print(f'[RESOLVE SKIPPED] {question_id} is not OPEN (already resolved?).')
        return
    new_block = block.replace(
        '**Status:** OPEN',
        f'**Status:** RESOLVED ({_today()}) {EM_DASH} {resolution}',
        1,
    )
    OPEN_QUESTIONS.write_text(text[:start] + new_block + text[end:])
    print(f'[QUESTION RESOLVED] {question_id}')
    print(f'  -> {resolution}')


def add_journal_entry(title: str, body: str, entry_id: str = None) -> None:
    """Append a dated journal entry. If entry_id is given, idempotent on it.

    Pass entry_id only for seeded entries you want protected against
    double-logging. Hand-written entries can omit it and will always append.
    """
    _ensure_file(THESIS_JOURNAL)
    tag = ''
    if entry_id is not None:
        marker = f'<!-- {entry_id} -->'
        if _already_has(THESIS_JOURNAL, marker):
            print(f'[JOURNAL SKIPPED] {entry_id} already logged.')
            return
        tag = f' {marker}'
    entry = f'\n## {_today()} {EM_DASH} {title}{tag}\n\n{body}\n\n'
    with open(THESIS_JOURNAL, 'a') as f:
        f.write(entry)
    print(f'[JOURNAL ENTRY] {title}')


def _view(path: Path) -> None:
    if not path.exists():
        print(f'(not created yet: {path.name})')
        return
    print(path.read_text())


def view_findings() -> None:
    _view(FINDINGS_LOG)


def view_open_questions() -> None:
    _view(OPEN_QUESTIONS)


def view_journal() -> None:
    _view(THESIS_JOURNAL)
