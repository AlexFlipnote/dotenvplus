from dotenvplus import DotEnv
from typing import TypedDict


class DotEnvTypes(TypedDict):
    STRING_VALUE: str
    INT_VALUE: int
    INT_STR_VALUE: str
    NONE_VALUE: None
    FLOAT_VALUE: float
    BOOL_VALUE: bool
    VAR_VALUE: str
    COMMENT_VALUE: str

env: DotEnv[DotEnvTypes] = DotEnv(".env.example")
env_types = env.as_typed()

print(env_types["STRING_VALUE"])

# You can also one-line it:
# env: DotEnv[DotEnvTypes] = DotEnv(".env.example").as_typed()
