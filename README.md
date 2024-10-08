# dotenvplus
Reads key-value pairs from a .env file and supports multiple values with dynamic interpolation.

The values returned by the DotEnv object is treated like a dictionary, so you can use it like a normal dictionary.
Some of the usual dictionary methods are also supported like `.items()`, `.keys()`, `.values()`, etc.

Goal is to make it easy to use environment variables in your code, while also supporting multiple values.

## Installing
> You need **Python >=3.6** to use this library.

```bash
pip install dotenvplus
```

## Usage
```env
# .env

KEY=value
```

```python
# main.py

from dotenvplus import DotEnv

# Create a DotEnv object
env = DotEnv()

Call it like a dictionary
env["KEY"]
>>> "value"
```
