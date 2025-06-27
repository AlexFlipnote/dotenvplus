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

# You can also automatically create a TypedDict from the .env file
# DotEnv.create_types(".env.example")
# It creates it to `./types/dotenvplus.py`

# After doing this, you can do:
env: DotEnv[DotEnvTypes] = DotEnv[DotEnvTypes](".env.example")
env_types = env.as_typed()
print(env_types["STRING_VALUE"])

# You can also one-line it:
# env: DotEnv[DotEnvTypes] = DotEnv[DotEnvTypes](".env.example").as_typed()
