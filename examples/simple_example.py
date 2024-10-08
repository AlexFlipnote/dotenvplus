from dotenvplus import DotEnv

env = DotEnv(".env.example")

print(env)
print(env["string_value"])

for k, v in env.items():
    print(f"{k}: {v}")
