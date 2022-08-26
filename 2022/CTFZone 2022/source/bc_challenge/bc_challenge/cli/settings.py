from typing import Mapping
from pydantic import BaseModel

from bc_challenge.api.client.settings import ApiClientSettings


class ChallengeFindings(BaseModel):
    tasks_access_codes: Mapping[str, str]
    flags: Mapping[str, str]


class ClientSettings(BaseModel):
    api: ApiClientSettings
    findings: ChallengeFindings

