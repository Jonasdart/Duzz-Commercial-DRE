from typing import Tuple
from pydantic import ConfigDict, BaseModel
from pydantic.alias_generators import to_camel


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        arbitrary_types_allowed=True,
    )


class CommonHeaders(BaseModel):
    sessiontoken: str
    company: str
    
    def get_tuple(self) -> Tuple[Tuple[str, str], Tuple[str, str]]:
        return (("sessionToken", self.sessiontoken), ("company", self.company))
