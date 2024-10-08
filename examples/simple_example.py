from dotenvplus import DotEnv

config = DotEnv(".env.example")

print(config)
print(config.keys)
print(int(config))
print(config["var_value"])

for k, v in config.items():
    print(f"{k}: {v}")

config.get("string_value")
print(next(k for k, v in config))
