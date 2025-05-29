from pydantic import BaseModel
from typing import Optional

class Reputation(BaseModel):
    """
    Represents a user's reputation summary.
    """
    score: Optional[float] = None
    rank: Optional[str] = None
    ranking_percentile: Optional[str] = None
    last_updated: Optional[str] = None
    adjusted_staking_yield: Optional[str] = None
    forecast_access_level: Optional[str] = None