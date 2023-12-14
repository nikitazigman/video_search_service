import typing as tp

import pydantic


class AccessToken(pydantic.BaseModel):
    token_string: tp.Annotated[str, pydantic.constr(pattern=r"^(?:[\w-]*\.){2}[\w-]*$")]
