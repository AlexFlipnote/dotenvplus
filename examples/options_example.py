import os
from dotenvplus import DotEnv

# handle_key_not_found: returns None instead of raising KeyError for missing keys
env = DotEnv(".env.example", handle_key_not_found=True)
print(env["MISSING_KEY"])   # None
print(env["STRING_VALUE"])  # hello world

# update_system_env: loads all values into os.environ (non-strings are converted)
DotEnv(".env.example", update_system_env=True)
print(os.environ.get("INT_VALUE"))   # 123
print(os.environ.get("BOOL_VALUE"))  # true

# override=False: skip keys already set in os.environ (useful as a dev fallback)
os.environ["STRING_VALUE"] = "from_system"
DotEnv(".env.example", update_system_env=True, override=False)
print(os.environ.get("STRING_VALUE"))  # from_system (not overwritten)

# encoding: read files with a non-default encoding
env = DotEnv(".env.example", encoding="utf-8")
