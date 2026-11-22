"""Resolve the Hyper key legends from Hammerspoon and its documented host bindings."""

import re


def hyper_bindings(source: str) -> dict[str, str]:
    """Map each Hyper letter to what it opens or does."""
    labels: dict[str, str] = {}
    if launcher := re.search(r'"AppLauncher".*?hotkeys\s*=\s*\{(.*?)\}', source, re.DOTALL):
        for line in launcher.group(1).splitlines():
            if app := re.match(r'\s*(\w)\s*=\s*"([^"]+)"', line):
                labels[app.group(1)] = app.group(2)
            elif taken := re.match(
                r'\s*--\s*(\w)\s*=\s*"",\s*--\s*already bound to (.+?)(?: in Raycast)?\s*$',
                line,
            ):
                labels.setdefault(
                    taken.group(1), taken.group(2)[:1].upper() + taken.group(2)[1:]
                )
    for key in re.findall(
        r'hs\.hotkey\.bind\(mods\.hyper,\s*"(\w)",\s*hs\.reload\)', source
    ):
        labels[key] = "Reload"
    return labels


def hyper_keys(source, physical, base):
    labels = hyper_bindings(source)
    return [
        labels.get(key.lower(), "").replace(" ", "\n") for key in physical[:30]
    ] + base[30:]
