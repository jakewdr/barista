from typing import Any

from simplejson import load


def unpack(
    cfgFile: str,
) -> dict[str, Any]:
    with open(cfgFile, "r") as cfgContents:
        return dict(load(cfgContents))
