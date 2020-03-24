"""
OPTIMADE

AiiDA Lab App that implements an OPTIMADE client
"""
import json
from pathlib import Path

from .query import OptimadeQueryWidget
from .summary import OptimadeSummaryWidget


__all__ = ("OptimadeQueryWidget", "OptimadeSummaryWidget")


PATH_TO_METADATA = Path(__file__).parent.parent.joinpath("metadata.json").resolve()
with open(PATH_TO_METADATA, "r") as fp:
    METADATA = json.load(fp)

# In order to update version, change it in `metadata.json`
__version__ = METADATA["version"]
