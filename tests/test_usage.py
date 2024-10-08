import os
import unittest

from dotenvplus import DotEnv, ParsingError


class TestDotEnv(unittest.TestCase):
    def setUp(self):
        # Create a sample .env file content
        self.env_content = (
            "# Comment line\n"
            "STRING_KEY=HelloWorld\n"
            "INT_KEY=1234\n"
            "FLOAT_KEY=12.34\n"
            "BOOL_TRUE_KEY=true\n"
            "BOOL_FALSE_KEY=false\n"
            "NULL_KEY=null\n"
            "NONE_KEY=none\n"
            "NIL_KEY=nil\n"
            "STRING_QUOTED_KEY='quoted_value'\n"
        )

        # Write the sample content to a temporary .env file
        self.file_path = ".env"
        with open(self.file_path, "w") as f:
            f.write(self.env_content)

    def tearDown(self):
        # Remove the temporary .env file after tests
        if os.path.exists(self.file_path):
            os.remove(self.file_path)

    def test_parsing_env_file(self):
        dotenv = DotEnv(self.file_path)
        self.assertIsInstance(dotenv, DotEnv)
        self.assertIsInstance(dotenv.get("STRING_KEY"), str)
        self.assertIsInstance(dotenv.get("INT_KEY"), int)
        self.assertIsInstance(dotenv.get("FLOAT_KEY"), float)
        self.assertIsInstance(dotenv.get("BOOL_TRUE_KEY"), bool)
        self.assertIsInstance(dotenv.get("BOOL_FALSE_KEY"), bool)
        self.assertIsInstance(dotenv.get("NULL_KEY"), type(None))
        self.assertIsInstance(dotenv.get("NONE_KEY"), type(None))
        self.assertIsInstance(dotenv.get("NIL_KEY"), type(None))

    def test_raises_error_on_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            DotEnv("missing_file.env")

    def test_raises_error_on_key_not_found(self):
        with self.assertRaises(KeyError):
            DotEnv(self.file_path)["NON_EXISTENT_KEY"]

    def test_config_handle_key_not_found(self):
        dotenv_with_handling = DotEnv(self.file_path, handle_key_not_found=True)
        self.assertIsNone(dotenv_with_handling["NON_EXISTENT_KEY"])

    def test_invalid_format(self):
        # Write an invalid format to the file
        with open(self.file_path, "w") as f:
            f.write("INVALID_LINE\n")

        with self.assertRaises(ParsingError):
            DotEnv(self.file_path)


if __name__ == "__main__":
    unittest.main()
