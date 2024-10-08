from dotenvplus import DotEnv

env = DotEnv(".env.example")

print(env)
print(env["STRING_VALUE"])
print(env["VAR_VALUE"])

for k, v in env.items():
    print(f"{k}: {v}")
