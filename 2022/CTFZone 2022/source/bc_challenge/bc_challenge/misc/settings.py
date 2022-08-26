from typing import Type
from pydantic import BaseModel
from returns.result import safe
import yaml


@safe
def load_settings(model_type: Type[BaseModel], file_name: str) -> BaseModel:
    with open(file_name) as f:
        obj = yaml.safe_load(f)
    return model_type(**obj)



@safe
def dump_settings(model: BaseModel, file_name: str) -> None:
    with open(file_name, 'w') as f:
        yaml.safe_dump(
            model.dict(), 
            stream=f, 
            allow_unicode=True, 
            sort_keys=False
        )
