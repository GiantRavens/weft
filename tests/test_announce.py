"""The announce script's X leg: the OAuth 1.0a signature and X's weighted length."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("announce", Path(__file__).parents[1] / ".github" / "scripts" / "announce.py")
announce = importlib.util.module_from_spec(spec)
spec.loader.exec_module(announce)


def test_oauth1_signature_matches_x_worked_example():
    """X's own worked example ('Creating a signature'): same keys, nonce and time -> the published signature."""
    keys = {"X_API_KEY": "xvz1evFS4wEEPTGEFPHBog", "X_API_SECRET": "kAcSOqF21Fu85e7zjz7ZN2U4ZRhfV3WpwPAoE3Z7kBw",
            "X_ACCESS_TOKEN": "370773112-GmHxMAgYyLbNEtIKZeRNFsMKPR9EyMZeS9weJAEb",
            "X_ACCESS_SECRET": "LswwdoUaIvS8ltyTt5jkRh4J50vUPVVHtR2YPi5kE"}
    h = announce.oauth1_header("POST", "https://api.twitter.com/1.1/statuses/update.json", keys,
                               {"include_entities": "true", "status": "Hello Ladies + Gentlemen, a signed OAuth request!"},
                               nonce="kYjzVBB8Y0ZFabxSWbWovY3uYSQ2pTgmZeNu2VS4cg", timestamp="1318622958")
    assert 'oauth_signature="hCtSmYh%2BiHYCEqBWrE7C7hYmtUk%3D"' in h


def test_x_length_counts_links_as_23_and_cjk_as_2():
    url = "https://weftlibrary.org/secret-history-mongols.html"
    assert announce.x_length("New in Weft: Völuspá.\n" + url) == len("New in Weft: Völuspá.\n") + 23
    assert announce.x_length("孫子") == 4


def test_url_regex_leaves_the_sentence_punctuation():
    url = "https://weftlibrary.org/x.html"
    for text in (f"See {url}.", f"({url})", f"{url}, and more", f"{url}\nnext", url):
        assert announce.URL_RE.search(text).group() == url, text


def test_a_split_work_is_not_announced_as_new(monkeypatch):
    """A work split from an older page (manifest split_from) is added in git but is not a new text."""
    def git(*args):
        if args[0] == "diff" and "--diff-filter=A" in args:
            return "texts/kant-aufklaerung/manifest.yaml\ntexts/grettis-new/manifest.yaml\n"
        if args[0] == "diff":
            return ""
        if args[0] == "show":
            return "work: kant-aufklaerung\nsplit_from: kant            # comment\n" if "kant-aufklaerung" in args[1] else "work: grettis-new\n"
        raise AssertionError(args)
    monkeypatch.setattr(announce, "git", git)
    works = {w: {"work": w, "title": w} for w in ("kant-aufklaerung", "grettis-new")}
    new, _ = announce.classify("a", "b", works)
    assert [x["work"] for x in new] == ["grettis-new"]
