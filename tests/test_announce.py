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
    url = "https://giantravens.github.io/weft/secret-history-mongols.html"
    assert announce.x_length("New in Weft: Völuspá.\n" + url) == len("New in Weft: Völuspá.\n") + 23
    assert announce.x_length("孫子") == 4


def test_url_regex_leaves_the_sentence_punctuation():
    url = "https://giantravens.github.io/weft/x.html"
    for text in (f"See {url}.", f"({url})", f"{url}, and more", f"{url}\nnext", url):
        assert announce.URL_RE.search(text).group() == url, text
