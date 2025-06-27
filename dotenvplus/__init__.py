import os
import re

from typing import (
    Any, Iterator, Optional, Tuple, List, Dict,
    Union, Generic, TypeVar, cast, TypedDict
)

__version__ = "0.0.9"

# RegEx patterns
re_keyvar = re.compile(r"^\s*(?:export\s+)?([a-zA-Z0-9_]+)\s*=\s*(.*)$")
re_isdigit = re.compile(r"^(?:-)?\d+$")
re_isfloat = re.compile(r"^(?:-)?\d+\.\d+$")
re_var_call = re.compile(r"\$\{([a-zA-Z0-9_]*)\}")

# Return types
DotEnvReturnType = Union[str, int, float, bool, None]
DotT = TypeVar("DotT", bound=TypedDict)  # type: ignore


class ParsingError(Exception):
    pass


class DotEnv(Generic[DotT]):
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
    handle_key_not_found:
        If True, it will make the object return `None` for any key that is not found.
        Essentially simulating `dict().get("Key", None)`

    Returns
    -------
    DotEnv:
        A DotEnv object that can be used to access the parsed values, just like dict.
        The object is a dictionary-like object, so you can do `DotEnv()["KEY"]` to access the value.

        It also supports type hints, so you can do `env: DotEnv[TypedDict] = DotEnv(".env")`
        and then `env.as_typed()` to get the parsed values as a typed dictionary.
        One-line version: `env: DotEnv[TypedDict] = DotEnv[TypedDict](".env").as_typed()`

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
        update_system_env: bool = False,
        handle_key_not_found: bool = False,
    ):
        # General values
        self.__env: dict[str, DotEnvReturnType] = {}

        # Defined values
        self.__quotes: Tuple[str, ...] = ('"', "'")
        self.__bools: Tuple[str, ...] = ("true", "false")
        self.__none: Tuple[str, ...] = ("null", "none", "nil", "undefined")

        # Config for the parser
        self.__path: str = path or ".env"
        self.__handle_key_not_found: bool = handle_key_not_found

        # Finally, the parser
        self.__parser()

        if update_system_env:
            os.environ.update({
                key: str(value)
                for key, value in self.__env.items()
            })

    def __repr__(self) -> str:
        return f"<DotEnv data={self.__env}>"

    def __getitem__(self, key: str) -> DotEnvReturnType:
        if self.__handle_key_not_found:
            return self.__env.get(key, None)
        return self.__env[key]

    def __setitem__(self, key: str, value: DotEnvReturnType) -> None:
        if not isinstance(value, (str, int, float, bool, type(None))):
            raise TypeError(f"Value must be a string, int, float, bool, or None, got {type(value)}")
        self.__env[key] = value

    def __delitem__(self, key: str) -> None:
        del self.__env[key]

    def __str__(self) -> str:
        return str(self.__env)

    def __int__(self) -> int:
        return len(self.__env)

    def __len__(self) -> int:
        return len(self.__env)

    def __iter__(self) -> Iterator[Tuple[str, DotEnvReturnType]]:
        return iter(self.__env.items())

    def __contains__(self, key: str) -> bool:
        return key in self.__env

    @property
    def keys(self) -> List[str]:
        """ Returns a list of the keys. """
        return list(self.__env.keys())

    @property
    def values(self) -> List[DotEnvReturnType]:
        """ Returns a list of the values. """
        return list(self.__env.values())

    def get(
        self,
        key: str,
        default: Optional[Any] = None  # noqa: ANN401
    ) -> DotEnvReturnType:
        """
        Return the value for key if key is in the dictionary, else default.

        Parameters
        ----------
        key:
            The key to look for.
        default:
            The default value to return if the key is not found.

        Returns
        -------
        DotEnvReturnType:
            The value of the key, or the default value if the key is not found.
        """
        return self.__env.get(key, default)

    def items(self) -> List[Tuple[str, DotEnvReturnType]]:
        """ Returns a list of the key-value pairs. """
        return list(self.__env.items())

    def copy(self) -> Dict[str, DotEnvReturnType]:
        """ Returns a shallow copy of the parsed values. """
        return self.__env.copy()

    def to_dict(self) -> Dict[str, DotEnvReturnType]:
        """ Returns a dictionary of the parsed values. """
        return self.__env

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

    @classmethod
    def create_types(cls, path: Optional[str] = None) -> None:
        """
        Creates a TypedDict from the .env file to `./types/dotenvplus.py` automatically.

        Parameters
        ----------
        path:
            The path to the .env file.
            If none are provided, it defaults to `./.env`
        """
        env = cls(path)
        payload = (
            "from typing import TypedDict\n\n"
            "__all__ = (\n"
            f'    "{cls.__name__}Types",\n'
            ")\n\n\n"
            f"class {cls.__name__}Types(TypedDict):\n"
        )

        for key, value in env.items():
            payload += f"    {key}: {type(value).__name__.replace('NoneType', 'None')}\n"
        payload += "\n"

        if not os.path.exists("./utils"):
            os.mkdir("./utils")
        if not os.path.exists("./utils/types"):
            os.mkdir("./utils/types")

        if not os.path.exists("./utils/types/__init__.py"):
            with open("./utils/types/__init__.py", "w", encoding="utf-8") as f:
                f.write("from .dotenvplus import *\n")

        else:
            with open("./utils/types/__init__.py", encoding="utf-8") as f:
                content = f.read()
                if " .dotenvplus " not in content:
                    with open("./utils/types/__init__.py", "a", encoding="utf-8") as f:
                        f.write("from .dotenvplus import *\n")

        with open("./utils/types/dotenvplus.py", "w", encoding="utf-8") as f:
            f.write(payload)

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
        with open(self.__path, encoding="utf-8") as f:
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
                lambda m: str(self.__env.get(m.group(1), "undefined")),
                str(value)
            )

            # Remove comment on the value itself too (if any)
            value = value.split("#")[0].strip()

            if (
                value.startswith(self.__quotes) and
                value.endswith(self.__quotes)
            ):
                # Remove quotes and skip the parsing step
                value = value[1:-1]

            else:
                # String is not forced, go ahead and parse it
                if re_isdigit.search(value):
                    value = int(value)

                elif re_isfloat.search(value):
                    value = float(value)

                elif value.lower() in self.__bools:
                    value = value.lower() == "true"

                elif value.lower() in self.__none:
                    value = None

            self.__env[key] = value
