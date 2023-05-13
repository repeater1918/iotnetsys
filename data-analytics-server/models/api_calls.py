from pydantic import BaseModel

class Timeframe(BaseModel):
    timeframe: int

class SessionID(BaseModel):
    sessionid: str