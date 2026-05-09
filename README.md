# DotEnvPlus
Reads key-value pairs from a `.env` file with automatic type conversion and variable interpolation.
Zero dependencies, native Python 3.10+.

Values are returned as a dictionary-like object, so `.items()`, `.keys()`, `.values()`, and all standard dict operations work out of the box.

## Installing
> You need **Python >=3.10** to use this library.

```bash
pip install dotenvplus
```

## Usage
```env
# .env
KEY1=value
KEY2=123
KEY3=true
```

```python
from dotenvplus import DotEnv

env = DotEnv(".env")

env["KEY1"]  # "value"
env["KEY2"]  # 123
env["KEY3"]  # True
```

## Type conversion
Values are automatically converted to the appropriate Python type:

| .env value | Python type | Example |
|---|---|---|
| `hello` | `str` | `"hello"` |
| `"123"` | `str` | `"123"` |
| `123` | `int` | `123` |
| `12.34` | `float` | `12.34` |
| `true` / `false` | `bool` | `True` / `False` |
| `null` / `none` / `nil` / `undefined` | `None` | `None` |

Quoting a value (single or double quotes) forces it to remain a string regardless of its content.

## Variable interpolation
Reference other keys or system environment variables using `${VAR}` or `$VAR`:

```env
HOST=localhost
PORT=5432
DATABASE_URL=postgres://${HOST}:${PORT}/mydb
REPLICA_URL=postgres://$HOST:$PORT/replica
```

```python
env["DATABASE_URL"]   # "postgres://localhost:5432/mydb"
env["REPLICA_URL"]    # "postgres://localhost:5432/replica"
```

## Multiline values
Wrap a value in quotes and span it across multiple lines:

```env
PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEA...
-----END RSA PRIVATE KEY-----"
```

```python
env["PRIVATE_KEY"]  # "-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA...\n-----END RSA PRIVATE KEY-----"
```

## Constructor options

```python
# Returns None instead of raising KeyError for missing keys
env = DotEnv(".env", handle_key_not_found=True)
env["MISSING"]  # None

# Loads all values into os.environ (non-strings are converted to strings)
env = DotEnv(".env", update_system_env=True)

# Don't overwrite keys already set in os.environ (useful as a dev fallback)
env = DotEnv(".env", update_system_env=True, override=False)

# Custom file encoding (defaults to utf-8)
env = DotEnv(".env", encoding="latin-1")
```

## TypedDict support
For full type hint support, define a `TypedDict` and use `as_typed()`:

```python
from typing import TypedDict
from dotenvplus import DotEnv

class MyEnv(TypedDict):
    HOST: str
    PORT: int
    DEBUG: bool

env: DotEnv[MyEnv] = DotEnv(".env")
typed = env.as_typed()
typed["PORT"]  # typed as int
```
