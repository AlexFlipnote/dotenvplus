import re

from typing import Any, Iterator, Optional, Tuple, List, Dict

__version__ = "0.0.1"


class ParsingError(Exception):
    pass


class DotEnv:
    """
    DotEnv is a dotenv parser for Python with additional type support.
    It supports parsing of string, integer, float, and boolean values.

    Arguments
    ---------
    path: `str` | `None`
        The path to the .env file.
        If none are provided, it defaults to `./.env`
    handle_key_not_found: `bool`
        If True, it will make the object return `None` for any key that is not found.
        Essentially simulating `dict().get("Key", None)`

    Raises
    ------
    `FileNotFoundError`
        If the file_path is not a valid path.
    `ParsingError`
        If one of the values cannot be parsed.
    """
    def __init__(
        self,
        path: Optional[str] = None,
        *,
        handle_key_not_found: bool = False,
    ):
        # RegEx patterns
        self.__re_keyvar = re.compile(r"^\s*([a-zA-Z0-9_]*)\s*=\s*(.+)$")
        self.__re_isdigit = re.compile(r"^(?:-)?\d+$")
        self.__re_isfloat = re.compile(r"^(?:-)?\d+\.\d+$")
        self.__re_var_call = re.compile(r"\$\{([a-zA-Z0-9_]*)\}")

        # General values
        self.__env: Dict[str, Any] = {}
        self.__quotes: Tuple[str, ...] = ("\"", "'")

        # Config for the parser
        self.__path: str = path or ".env"
        self.__handle_key_not_found: bool = handle_key_not_found

        # Finally, the parser
        self.__parser()

    def __repr__(self) -> str:
        return f"<DotEnv data={self.__env}>"

    def __getitem__(self, key: str) -> Any:
        if self.__handle_key_not_found:
            return self.__env.get(key, None)
        return self.__env[key]

    def __str__(self) -> str:
        return str(self.__env)

    def __int__(self) -> int:
        return len(self.__env)

    def __len__(self) -> int:
        return len(self.__env)

    def __iter__(self) -> Iterator[Tuple[str, Any]]:
        return iter(self.__env.items())

    @property
    def keys(self) -> List[str]:
        """ `list[str]`: Returns a list of the keys. """
        return list(self.__env.keys())

    @property
    def values(self) -> List[Any]:
        """ `list[Any]`: Returns a list of the values. """
        return list(self.__env.values())

    def get(self, key: str, default: Any = None) -> Any:
        """ `Any`: Return the value for key if key is in the dictionary, else default. """
        return self.__env.get(key, default)

    def items(self) -> List[Tuple[str, Any]]:
        """ `list[tuple[str, Any]]`: Returns a list of the key-value pairs. """
        return list(self.__env.items())

    def copy(self) -> Dict[str, Any]:
        """ `dict[str, Any]`: Returns a shallow copy of the parsed values. """
        return self.__env.copy()

    def to_dict(self) -> Dict[str, Any]:
        """ `dict`: Returns a dictionary of the parsed values. """
        return self.__env

    def __parser(self) -> None:
        """
        Parse the .env file and store the values in a dictionary.
        The keys are accessible later by using the square bracket notation
        directly on the DotEnv object.

        Raises
        ------
        `FileNotFoundError`
            If the file_path is not a valid path.
        `ParsingError`
            If one of the values cannot be parsed.
        """
        with open(self.__path, "r", encoding="utf-8") as f:
            data: List[str] = f.readlines()

        for line in data:
            line = line.strip()

            if line.startswith("#") or line == "":
                # Ignore comment or empty line
                continue

            _find_kv = self.__re_keyvar.search(line)
            if not _find_kv:
                raise ParsingError(f"Expected key=value format, got '{line}'")

            key, value = _find_kv.groups()
            _force_string = False

            # Replace any variables in the value
            value = self.__re_var_call.sub(
                lambda m: str(self.__env.get(m.group(1), "undefined")),
                str(value)
            )

            # Remove quotes, but mark it as forced string from now
            if (
                value.startswith(self.__quotes) and
                value.endswith(self.__quotes)
            ):
                value = value[1:-1]
                _force_string = True

            if not _force_string:

                if self.__re_isdigit.search(value):
                    value = int(value)

                elif self.__re_isfloat.search(value):
                    value = float(value)

                elif value.lower() in ("true", "false"):
                    value = value.lower() == "true"

                elif value.lower() in ("null", "none", "nil", "undefined"):
                    value = None

                else:
                    value = value

            self.__env[key] = value
