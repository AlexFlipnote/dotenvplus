from dotenvplus import DotEnv

env = DotEnv(".env.example")
# env value now is a dictionary-like object
# You can do `env["KEY"]` to access the value

print(env)
print(env["STRING_VALUE"])
print("STRING_VALUE" in env)

for k, v in env.items():
    print(f"{k}: {v} (type: {type(v)})")
