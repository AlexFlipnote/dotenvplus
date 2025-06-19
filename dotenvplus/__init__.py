import os
import re

from typing import Any, Iterator, Optional, Tuple, List, Dict, Union

__version__ = "0.0.6"

# RegEx patterns
re_keyvar = re.compile(r"^\s*([a-zA-Z0-9_]*)\s*=\s*(.+)$")
re_isdigit = re.compile(r"^(?:-)?\d+$")
re_isfloat = re.compile(r"^(?:-)?\d+\.\d+$")
re_var_call = re.compile(r"\$\{([a-zA-Z0-9_]*)\}")

# Return types
DotEnvReturnType = Union[str, int, float, bool, None]


class ParsingError(Exception):
    pass


class DotEnv:
    """
    DotEnv is a dotenv parser for Python with additional type support.

    It supports parsing of string, integer, float, and boolean values.

    Arguments
    ---------
    path:
        The path to the .env file.
        If none are provided, it defaults to `./.env`
    update_system_env:
        If True, it will load the values to the instance's environment variables.
        Be warned that this will only support string values.
    handle_key_not_found:
        If True, it will make the object return `None` for any key that is not found.
        Essentially simulating `dict().get("Key", None)`

    Raises
    ------
    `FileNotFoundError`
        If the file_path is not a valid path.
    `ParsingError`
        If one of the values cannot be parsed.
    """
    __slots__ = (
        "_bools",
        "_env",
        "_frozen",
        "_handle_key_not_found",
        "_none",
        "_path",
        "_quotes",
        "_re_isdigit",
        "_re_isfloat",
        "_re_keyvar",
        "_re_var_call",
    )

    def __init__(
        self,
        path: Optional[str] = None,
        *,
        update_system_env: bool = False,
        handle_key_not_found: bool = False,
    ):
        # General values
        self._frozen: bool = False
        self._env: dict[str, Any] = {}

        # Defined values
        self._quotes: Tuple[str, ...] = ('"', "'")
        self._bools: Tuple[str, ...] = ("true", "false")
        self._none: Tuple[str, ...] = ("null", "none", "nil", "undefined")

        # Config for the parser
        self._path: str = path or ".env"
        self._handle_key_not_found: bool = handle_key_not_found

        # Finally, the parser
        self._parser()

        if update_system_env:
            os.environ.update({
                key: str(value)
                for key, value in self._env.items()
            })

    def __repr__(self) -> str:
        return f"<DotEnv data={self._env}>"

    def __getitem__(self, key: str) -> DotEnvReturnType:
        if self._handle_key_not_found:
            return self._env.get(key, None)
        return self._env[key]

    def __str__(self) -> str:
        return str(self._env)

    def __int__(self) -> int:
        return len(self._env)

    def __len__(self) -> int:
        return len(self._env)

    def __iter__(self) -> Iterator[Tuple[str, Any]]:
        return iter(self._env.items())

    def __contains__(self, key: str) -> bool:
        return key in self._env

    def __setitem__(self, key: str, value: Any) -> None:  # noqa: ANN401
        if self._frozen:
            raise AttributeError("This DotEnv object is read-only.")
        self._env[key] = value

    def __delitem__(self, key: str) -> None:
        if self._frozen:
            raise AttributeError("This DotEnv object is read-only.")
        del self._env[key]

    @property
    def keys(self) -> List[str]:
        """ Returns a list of the keys. """
        return list(self._env.keys())

    @property
    def values(self) -> List[DotEnvReturnType]:
        """ Returns a list of the values. """
        return list(self._env.values())

    def get(self, key: str, default: Optional[Any] = None) -> DotEnvReturnType:  # noqa: ANN401
        """ Return the value for key if key is in the dictionary, else default. """
        return self._env.get(key, default)

    def items(self) -> List[Tuple[str, DotEnvReturnType]]:
        """ Returns a list of the key-value pairs. """
        return list(self._env.items())

    def copy(self) -> Dict[str, DotEnvReturnType]:
        """ Returns a shallow copy of the parsed values. """
        return self._env.copy()

    def to_dict(self) -> Dict[str, DotEnvReturnType]:
        """ Returns a dictionary of the parsed values. """
        return self._env

    def _parser(self) -> None:
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
        with open(self._path, encoding="utf-8") as f:
            data: list[str] = f.readlines()

        for line_no, line in enumerate(data, start=1):
            line = line.strip()

            if line.startswith("#") or line == "":
                # Ignore comment or empty line
                continue

            find_kv = re_keyvar.search(line)
            if not find_kv:
                raise ParsingError(
                    f"Error at line {line_no}: "
                    f"Expected key=value format, got '{line}'"
                )

            key, value = find_kv.groups()

            # Replace any variables in the value
            value = re_var_call.sub(
                lambda m: str(self._env.get(m.group(1), "undefined")),
                str(value)
            )

            # Remove comment on the value itself too (if any)
            value = value.split("#")[0].strip()

            if (
                value.startswith(self._quotes) and
                value.endswith(self._quotes)
            ):
                # Remove quotes and skip the parsing step
                value = value[1:-1]

            else:
                # String is not forced, go ahead and parse it
                if re_isdigit.search(value):
                    value = int(value)

                elif re_isfloat.search(value):
                    value = float(value)

                elif value.lower() in self._bools:
                    value = value.lower() == "true"

                elif value.lower() in self._none:
                    value = None

            self._env[key] = value

        self._frozen = True
