"""The audio layer's records (pipeline/weft/audio.py) and the recording page's items (pipeline/weft/record.py)."""
from weft import audio, record

IDS = {"w.1", "w.1.1", "w.1.2"}
SPEAKER = {
    "id": "s1", "kind": "speaker", "dialect": "Oklahoma",
    "reader": {"credit": "A Reader"}, "license": "rights-retained",
    "conditions": ["no-ai-training", "display-by-permission"],
    "consent": {"date": "2026-10-20", "sheet": "docs/speakers.md"},
    "files": {"w.1": "private/texts/w/audio/w.1.webm"},
}


def classes(recs, schemes=("c1828",)):
    return [c for c, _ in audio.problems(recs, list(schemes), IDS)]


def test_a_complete_speaker_record_passes():
    assert classes([SPEAKER]) == []


def test_a_speaker_reading_names_a_dialect_and_never_a_scheme():
    assert "audio-speaker-no-dialect" in classes([{**SPEAKER, "dialect": None}])
    assert "audio-speaker-has-scheme" in classes([{**SPEAKER, "scheme": "c1828"}])


def test_a_scheme_reading_names_one_of_the_works_schemes():
    rec = {**SPEAKER, "kind": "scheme", "scheme": "c1828", "dialect": None, "consent": None}
    assert classes([rec]) == []
    assert "audio-scheme" in classes([{**rec, "scheme": "erasmian"}])


def test_kept_rights_require_display_by_permission():
    assert "audio-rights-retained" in classes([{**SPEAKER, "conditions": ["no-ai-training"]}])
    assert "audio-condition" in classes([{**SPEAKER, "conditions": ["display-by-permission", "exclusive"]}])


def test_a_speaker_reading_needs_consent_and_a_reader():
    assert "audio-speaker-no-consent" in classes([{**SPEAKER, "consent": {"date": "2026-10-20"}}])
    assert "audio-reader" in classes([{**SPEAKER, "reader": {}}])
    assert classes([{**SPEAKER, "reader": {"anonymous": True}}]) == []


def test_files_hang_off_known_ids_and_leave_with_a_withdrawal():
    assert "audio-unknown-id" in classes([{**SPEAKER, "files": {"w.9": "x.webm"}}])
    assert "audio-withdrawn-has-files" in classes([{**SPEAKER, "withdrawn": True}])
    assert classes([{**SPEAKER, "withdrawn": True, "files": {}}]) == []


def test_the_recording_page_lists_lines_then_doubtful_words_once():
    data = {"lines": [
        {"id": "w.1", "text": "ᎠᏴ ᎬᏂᏉ ᎬᏂᏉ", "tokens": [
            {"id": "w.1.1", "surface": "ᎠᏴ", "lemma": "ᎠᏴ", "gloss": "we"},
            {"id": "w.1.2", "surface": "ᎬᏂᏉ", "lemma": "?", "gloss": "?"},
            {"id": "w.1.3", "surface": "ᎬᏂᏉ", "lemma": "?", "gloss": "?"}]},
        {"id": "w.2", "tokens": [
            {"id": "w.2.1", "surface": "ᏙᎯ", "lemma": "ᏙᎯ", "gloss": "peace?"},
            {"id": "w.2.2", "surface": "ᏥᏕᎬᎫᏗ", "lemma": "ᏥᏕᎬᎫᏗ", "gloss": "x", "uncertain": {"alt": "ᏥᏕᎬᎫᏗ"}}]}]}
    got = [(i["kind"], i["id"]) for i in record.items(data)]
    assert got == [("line", "w.1"), ("line", "w.2"), ("word", "w.1.2"), ("word", "w.2.2")]


def test_kept_rights_never_sit_in_the_public_tree():
    assert "audio-rights-retained-public" in classes([{**SPEAKER, "files": {"w.1": "audio/w.1.webm"}}])
    assert classes([{**SPEAKER, "files": {"w.1": "https://weftlibrary.org/a/w.1.webm"}}]) == []
    open_lic = {**SPEAKER, "license": "CC0", "conditions": ["no-ai-training"], "files": {"w.1": "audio/w.1.webm"}}
    assert classes([open_lic]) == []


def test_a_speaker_reading_carries_the_no_ai_condition():
    assert "audio-speaker-no-ai-condition" in classes([{**SPEAKER, "conditions": ["display-by-permission"]}])
