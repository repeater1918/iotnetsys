from pydantic import BaseModel

class Timeframe(BaseModel):
    timeframe: int