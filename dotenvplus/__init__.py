import os
import re

from collections.abc import Iterator, MutableMapping
from typing import Any, Generic, TypeVar, cast

__version__ = "0.2.0"
__all__ = (
    "DotEnv",
    "ParsingError",
)

# RegEx patterns
re_keyvar = re.compile(r"^\s*(?:export\s+)?([a-zA-Z0-9_]+)\s*=\s*(.*)$")
re_isdigit = re.compile(r"^(?:-)?\d+$")
re_isfloat = re.compile(r"^(?:-)?\d+\.\d+$")
re_var_call = re.compile(r"\$\{([a-zA-Z0-9_]+)\}|\$([a-zA-Z_][a-zA-Z0-9_]*)")

# Return types
DotT = TypeVar("DotT")


class ParsingError(Exception):
    pass


class DotEnv(MutableMapping, Generic[DotT]):
    """
    DotEnv is a dotenv parser for Python with additional type support.

    It supports parsing of string, integer, float, none, and boolean values.

    Arguments
    ---------
    path:
        The path to the .env file.
        If none are provided, it defaults to `./.env`
    update_system_env:
        If True, it will load the values to the instance's environment variables.
        Be warned that this will only support string values, so any other types will be converted to strings.
    override:
        Only relevant when `update_system_env=True`.
        If False, keys already present in `os.environ` will not be overwritten.
        Defaults to True.
    handle_key_not_found:
        If True, it will make the object return `None` for any key that is not found.
        Essentially simulating `dict().get("Key", None)`
    encoding:
        The encoding used to read the .env file. Defaults to `utf-8`.

    Returns
    -------
        A DotEnv object that can be used to access the parsed values, just like dict.
        The object is a dictionary-like object, so you can do `DotEnv()["KEY"]` to access the value.

        It also supports type hints via TypedDict. Define a TypedDict subclass with your keys,
        then do `env: DotEnv[MyTypes] = DotEnv(".env")` and call `env.as_typed()` to get
        a typed view. See `as_typed()` for a full example.

    Raises
    ------
    FileNotFoundError
        If the file_path is not a valid path.
    ParsingError
        If one of the values cannot be parsed.
    """

    _QUOTES: tuple[str, ...] = ('"', "'")
    _BOOLS: tuple[str, ...] = ("true", "false")
    _NONE_VALUES: tuple[str, ...] = ("null", "none", "nil", "undefined")

    def __init__(
        self,
        path: str | os.PathLike[str] | None = None,
        *,
        update_system_env: bool = False,
        override: bool = True,
        handle_key_not_found: bool = False,
        encoding: str = "utf-8",
    ):
        self.__env: dict[str, Any] = {}
        self.__path: str | os.PathLike[str] = path or ".env"
        self.__handle_key_not_found: bool = handle_key_not_found

        self.__parser(encoding)

        if update_system_env:
            for key, value in self.__env.items():
                if override or key not in os.environ:
                    os.environ[key] = str(value)

    def __repr__(self) -> str:
        return f"<DotEnv path={self.__path!r} keys={list(self.__env.keys())}>"

    def __getitem__(self, key: str) -> Any:  # noqa: ANN401
        if self.__handle_key_not_found:
            return self.__env.get(key, None)
        return self.__env[key]

    def __setitem__(self, key: str, value: Any) -> None:  # noqa: ANN401
        if not isinstance(value, (str, int, float, bool, type(None))):
            raise TypeError(f"Value must be a string, int, float, bool, or None, got {type(value)}")
        self.__env[key] = value

    def __delitem__(self, key: str) -> None:
        del self.__env[key]

    def __str__(self) -> str:
        return repr(self)

    def __len__(self) -> int:
        return len(self.__env)

    def __iter__(self) -> Iterator[str]:
        return iter(self.__env)

    def to_dict(self) -> dict[str, Any]:
        """ Returns a shallow copy of the parsed values. """
        return self.__env.copy()

    def as_typed(self) -> DotT:
        """
        Returns the parsed values as a typed dictionary.

        Helpful if you want to have TypedDict support.
        Otherwise doing `DotEnv[...]` is fine, but you lose types.

        Example
        -------
        .. code-block:: python
            from dotenvplus import DotEnv
            from typing import TypedDict

            class MyTypes(TypedDict):
                STRING_VALUE: str

            env: DotEnv[MyTypes] = DotEnv(".env")
            env_types = env.as_typed()
            print(env_types["STRING_VALUE"])
        """
        return cast("DotT", self.__env)

    def __parser(self, encoding: str) -> None:
        """
        Parse the .env file and store the values in a dictionary.

        The keys are accessible later by using the square bracket notation
        directly on the DotEnv object.

        Raises
        ------
        FileNotFoundError
            If the file_path is not a valid path.
        ParsingError
            If one of the values cannot be parsed.
        """
        with open(self.__path, encoding=encoding) as f:
            data: list[str] = f.readlines()

        lines = iter(enumerate(data, start=1))
        for line_no, line in lines:
            line = line.strip()

            if line.startswith("#") or line == "":
                continue

            find_kv = re_keyvar.search(line)
            if not find_kv:
                raise ParsingError(
                    f"Error at line {line_no}: "
                    f"Expected key=value format, got '{line}'"
                )

            key, value = find_kv.groups()
            is_string_forced = False

            if value and value[0] in self._QUOTES:
                quote_char = value[0]
                if len(value) >= 2 and value[-1] == quote_char:
                    # Same-line quoted string
                    value = value[1:-1]
                    is_string_forced = True
                elif len(value) == 1 or value[-1] not in self._QUOTES:
                    # Multiline: opening quote with no closing quote on this line
                    parts = [value[1:]]
                    for _, next_line in lines:
                        next_line = next_line.rstrip("\n\r")
                        if next_line.endswith(quote_char):
                            parts.append(next_line[:-1])
                            break
                        parts.append(next_line)
                    value = "\n".join(parts)
                    is_string_forced = True
                else:
                    # Mismatched quotes, treat as unquoted
                    value = value.split("#")[0].strip()
            else:
                value = value.split("#")[0].strip()

            value = re_var_call.sub(
                lambda m: str(self.__env.get(
                    m.group(1) or m.group(2),
                    os.environ.get(m.group(1) or m.group(2), ""),
                )),
                str(value),
            )

            if not is_string_forced:
                if re_isdigit.search(value):
                    value = int(value)

                elif re_isfloat.search(value):
                    value = float(value)

                elif value.lower() in self._BOOLS:
                    value = value.lower() == "true"

                elif value.lower() in self._NONE_VALUES:
                    value = None

            self.__env[key] = value
