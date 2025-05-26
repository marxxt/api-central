from typing import Literal

from pydantic import BaseModel


SortOptionValue = Literal[
    "date_listed_newest",
    "date_listed_oldest",
    "ending_soonest",
    "ending_latest",
    "price_lowest",
    "price_highest"
]

class SortOption(BaseModel):
    value: SortOptionValue
    label: str