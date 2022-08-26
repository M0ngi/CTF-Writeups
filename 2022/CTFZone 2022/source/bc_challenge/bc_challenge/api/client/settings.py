from pydantic import BaseModel


class ApiClientSettings(BaseModel):
    url: str
    team_token: str
