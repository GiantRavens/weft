"""weft about: the manifest's wikipedia field -> about.yaml, offline against recorded API replies."""
from pathlib import Path

import pytest
import yaml

from weft import about, check

REPO = Path(__file__).resolve().parents[1]

PAGE = {"query": {"pages": {"1": {
    "title": "Inter caetera", "extract": "Inter caetera was a papal bull issued by Pope Alexander VI on 4 May 1493.\nA second paragraph.",
    "revisions": [{"revid": 111}], "pageprops": {"wikibase_item": "Q1134342"}}}}}
ENTITY = {"entities": {"Q1134342": {"id": "Q1134342", "lastrevid": 222,
          "descriptions": {"en": {"value": "papal bull by Alexander VI"}},
          "claims": {"P31": [{"mainsnak": {"datavalue": {"value": {"id": "Q189867"}}}}],
                     "P921": [{"mainsnak": {"datavalue": {"value": {"id": "Q127834"}}}},
                              {"mainsnak": {"datavalue": {"value": {"id": "Q999"}}}}]}}}}
LABELS = {"entities": {"Q189867": {"labels": {"en": {"value": "papal bull"}}},
                       "Q127834": {"labels": {"en": {"value": "New World"}}}, "Q999": {"labels": {}}}}


def fake_get(replies):
    def get(url):
        for key, reply in replies:
            if key in url:
                return reply
        raise AssertionError(f"unexpected request {url}")
    return get


GET = fake_get([("wikipedia.org", PAGE), ("props=claims", ENTITY), ("props=labels", LABELS)])


def work(tmp_path, wikipedia) -> Path:
    wd = tmp_path / "inter-caetera-1493"
    wd.mkdir()
    m = {"work": "inter-caetera-1493", "title": "The bull Inter caetera", "kind": "law"}
    if wikipedia is not None:
        m["wikipedia"] = wikipedia
    (wd / "manifest.yaml").write_text(yaml.dump(m, allow_unicode=True))
    return wd


def test_lead_takes_the_first_paragraph_and_a_second_after_a_stub():
    assert about.lead_of("A full first paragraph. " * 12 + "\nSecond.") == ("A full first paragraph. " * 12).strip()
    assert about.lead_of("Short.\n\nSecond paragraph.\nThird.") == "Short.\n\nSecond paragraph."
    assert about.lead_of("") == ""


def test_found_work_writes_a_pinned_attributed_record(tmp_path):
    wd = work(tmp_path, {"title": "Inter_caetera", "match": "work"})
    r = about.run([wd], get=GET)
    assert r["outcomes"] == {"found-work": 1} and r["predicted_found"] == r["actual_found"] == 1
    rec = yaml.safe_load((wd / "about.yaml").read_text())
    assert rec["wikipedia"]["revision"] == 111 and "oldid=111" in rec["wikipedia"]["url"]
    assert "CC BY-SA 4.0" in rec["wikipedia"]["attribution"]
    assert rec["wikipedia"]["lead"].startswith("Inter caetera was a papal bull")      # verbatim
    assert rec["wikidata"]["instance_of"] == [{"id": "Q189867", "label": "papal bull"}]
    # a value with no English label keeps its id and gets no invented label
    assert rec["wikidata"]["main_subject"] == [{"id": "Q127834", "label": "New World"}, {"id": "Q999"}]


@pytest.mark.parametrize("field,outcome", [(None, "unnamed"), ({"match": "none"}, "declared-none"),
                                           ({"title": "X", "match": "maybe"}, "bad-field"), ({"match": "work"}, "bad-field")])
def test_outcomes_without_a_fetch(tmp_path, field, outcome):
    wd = work(tmp_path, field)
    assert about.run_one(wd, get=fake_get([]))[0] == outcome
    assert not (wd / "about.yaml").exists()


@pytest.mark.parametrize("page,outcome", [({"missing": ""}, "article-missing"),
                                          ({"title": "X", "pageprops": {"disambiguation": ""}}, "article-disambiguation")])
def test_failure_classes_write_nothing(tmp_path, page, outcome):
    wd = work(tmp_path, {"title": "X", "match": "work"})
    r = about.run([wd], get=fake_get([("wikipedia.org", {"query": {"pages": {"-1": page}}})]))
    assert r["not_found"] == {outcome: ["inter-caetera-1493"]} and r["actual_found"] == 0
    assert not (wd / "about.yaml").exists()


def test_check_flags_a_stale_record(tmp_path):
    wd = work(tmp_path, {"title": "Inter_caetera", "match": "work"})
    about.run([wd], get=GET)
    m = yaml.safe_load((wd / "manifest.yaml").read_text())
    found = []
    check.check_about(wd, m, lambda cls, s, warn=False: found.append((cls, warn)))
    assert found == []
    m["wikipedia"]["match"] = "author"
    check.check_about(wd, m, lambda cls, s, warn=False: found.append((cls, warn)))
    assert found == [("about-stale", False)]


def test_every_public_work_names_its_article_and_every_record_is_complete():
    """The committed library: every manifest carries a valid wikipedia field, and every work that names
    an article has a complete about.yaml. Works with match: none are the curated-about backlog."""
    for mp in sorted((REPO / "texts").glob("*/manifest.yaml")):
        m = yaml.safe_load(mp.read_text())
        found = []
        check.check_about(mp.parent, m, lambda cls, s, warn=False: found.append(cls))
        assert set(found) <= {"about-none"}, (mp.parent.name, found)


def test_split_works_keep_their_ids_and_old_addresses(tmp_path):
    """The five collection pages split on 2026-10-09: each new work names the page it came from, its line IDs
    carry that page's prefix, and the build writes a page at the old address that sends a line link on."""
    from weft import build
    ms = [m for m in build.library_order(REPO) if m.get("split_from")]
    olds = {m["split_from"] for m in ms}
    assert olds == {"runes", "science-latin", "kant", "nietzsche", "verdi-libretti"}
    assert not any((REPO / "texts" / o / "manifest.yaml").exists() for o in olds)
    for m in ms:
        assert (REPO / "texts" / m["work"] / "about.yaml").exists(), m["work"]
    # a minimal out dir: two built pages from one old page are enough to exercise the moved page
    for w in ("kant-aufklaerung", "kant-practical-reason"):
        (tmp_path / f"{w}.html").write_text("<html></html>")
    pages = build.moved_pages(REPO, tmp_path, {})
    assert [p.name for p in pages] == ["kant.html"]
    html = pages[0].read_text()
    assert "This page is now 2 works" in html and 'href="kant-aufklaerung.html"' in html
    assert '"kpv": "kant-practical-reason.html"' in html and '"auf": "kant-aufklaerung.html"' in html


def test_a_split_work_keeps_its_arrival_date():
    from weft import build
    ms = build.library_order(REPO)
    dates = build.added_dates(REPO, ms)
    for m in ms:
        if m.get("split_from") and m["split_from"] in ("kant", "runes"):
            assert dates[m["work"]] == dates[m["split_from"]], m["work"]
