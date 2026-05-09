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
