"""Visit counting for the published library: the same PostHog setup as every portfolio site
(code/portfolio-sites/src/layouts/Analytics.astro), stamped into each built page after `weft build`.

One PostHog project for the whole portfolio; every event carries `domain` and `tier`, so the domains
sweep (tools/dnsctl/domains_state.py) files Weft's numbers under weftlibrary.org with no extra wiring.
Cookieless ("always"): no cookies, no local or session storage, no consent banner. autocapture is off,
so the events are $pageview, $pageleave and cta_click (any element with data-track) and nothing typed.
Never call identify().

The loader runs only on the live host (HOSTS). A page opened from file://, a local preview, the
previews step's headless browser and the private build send nothing, so rule 7 (works from file://)
holds and the 800x600 headless renders never reach the numbers.

api_host is the relay at t.weftlibrary.org (2026-10-10): GitHub Pages cannot run the portfolio's
same-origin /relay worker, so the same worker (portfolio-sites tools/relay_worker.js) runs as its own
Pages project on a first-party subdomain (portfolio-sites tools/relay_host.sh). Ad blockers drop
requests to *.posthog.com by name; through the library's own domain they do not.
"""
from __future__ import annotations

import json
from pathlib import Path

MARK = "<!-- weft:analytics -->"
HOSTS = ["weftlibrary.org"]
# public by design (it ships in every page); the same key as sites/_shared/analytics.json in portfolio-sites
CONFIG = {"key": "phc_B5FeFvyo9BEFVAtQfXyojHpUA9LQcbw9rbNiZGB9oMZh", "api_host": "https://t.weftlibrary.org/relay",
          "ui_host": "https://us.posthog.com", "defaults": "2026-05-30", "domain": "weftlibrary.org", "tier": "library"}

# PostHog's documented loader stub (it queues calls until array.js arrives), then the portfolio's init.
SNIPPET = MARK + """<script>(function(c,h){if(h.indexOf(location.hostname)<0)return;
!function(t,e){var o,n,p,r;e.__SV||(window.posthog=e,e._i=[],e.init=function(i,s,a){function g(t,e){var o=e.split(".");2==o.length&&(t=t[o[0]],e=o[1]),t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}}(p=t.createElement("script")).type="text/javascript",p.crossOrigin="anonymous",p.async=!0,p.src=s.api_host.replace(".i.posthog.com","-assets.i.posthog.com")+"/static/array.js",(r=t.getElementsByTagName("script")[0]).parentNode.insertBefore(p,r);var u=e;for(void 0!==a?u=e[a]=[]:a="posthog",u.people=u.people||[],u.toString=function(t){var e="posthog";return"posthog"!==a&&(e+="."+a),t||(e+=" (stub)"),e},u.people.toString=function(){return u.toString(1)+".people (stub)"},o="init capture register register_once unregister opt_in_capturing opt_out_capturing has_opted_out_capturing get_distinct_id get_property set_config reset debug".split(" "),n=0;n<o.length;n++)g(u,o[n]);e._i.push([i,s,a])},e.__SV=1)}(document,window.posthog||[]);
posthog.init(c.key,{api_host:c.api_host,ui_host:c.ui_host,defaults:c.defaults,cookieless_mode:"always",
autocapture:false,disable_session_recording:true});
posthog.register({domain:c.domain,tier:c.tier});
document.addEventListener("click",function(e){var a=e.target&&e.target.closest&&e.target.closest("[data-track]");
if(a)posthog.capture("cta_click",{target:a.dataset.track,href:a.getAttribute("href")});});
})(""" + json.dumps(CONFIG) + "," + json.dumps(HOSTS) + """);</script>
"""


def stamp(html: str) -> str:
    """Insert the snippet before the first </head>; a page already stamped, or without a head, is returned as is."""
    if MARK in html or "</head>" not in html:
        return html
    return html.replace("</head>", SNIPPET + "</head>", 1)


def stamp_dir(out_dir: Path) -> int:
    """Stamp every built page in out_dir; returns how many pages changed."""
    n = 0
    for page in sorted(out_dir.glob("*.html")):
        html = page.read_text(encoding="utf-8")
        new = stamp(html)
        if new != html:
            page.write_text(new, encoding="utf-8")
            n += 1
    return n
