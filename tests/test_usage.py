import os
import unittest

from dotenvplus import DotEnv, ParsingError


class TestDotEnv(unittest.TestCase):
    def setUp(self):
        os.environ["SYSTEM_VAR"] = "system_value"

        self.env_content = (
            "# Comment line\n"
            "STRING_KEY=HelloWorld\n"
            "INT_KEY=1234\n"
            "STR_INT_KEY='1234'\n"
            "FLOAT_KEY=12.34\n"
            "BOOL_TRUE_KEY=true\n"
            "BOOL_FALSE_KEY=false\n"
            "COMMENT_KEY=comment # Comment here\n"
            "NULL_KEY=null\n"
            "NONE_KEY=none\n"
            "NIL_KEY=nil\n"
            "STRING_QUOTED_KEY='quoted_value'\n"
            "HASH_PASS=\"my#super#secret\"\n"
            "INTERPOLATED_KEY=${STRING_KEY}_appended\n"
            "SYS_INTERPOLATED_KEY=${SYSTEM_VAR}\n"
            "export EXPORTED_KEY=exported_value\n"
        )

        self.file_path = ".env"
        with open(self.file_path, "w", encoding="utf-8") as f:
            f.write(self.env_content)

    def tearDown(self):
        if os.path.exists(self.file_path):
            os.remove(self.file_path)

        if "SYSTEM_VAR" in os.environ:
            del os.environ["SYSTEM_VAR"]

    def test_parsing_exact_values(self):
        dotenv = DotEnv(self.file_path)

        self.assertEqual(dotenv["STRING_KEY"], "HelloWorld")
        self.assertEqual(dotenv["INT_KEY"], 1234)
        self.assertEqual(dotenv["STR_INT_KEY"], "1234")
        self.assertEqual(dotenv["FLOAT_KEY"], 12.34)
        self.assertTrue(dotenv["BOOL_TRUE_KEY"])
        self.assertFalse(dotenv["BOOL_FALSE_KEY"])
        self.assertIsNone(dotenv["NULL_KEY"])
        self.assertIsNone(dotenv["NONE_KEY"])
        self.assertIsNone(dotenv["NIL_KEY"])
        self.assertEqual(dotenv["STRING_QUOTED_KEY"], "quoted_value")

    def test_edge_cases_and_interpolation(self):
        dotenv = DotEnv(self.file_path)

        self.assertEqual(dotenv["COMMENT_KEY"], "comment")
        self.assertEqual(dotenv["HASH_PASS"], "my#super#secret")
        self.assertEqual(dotenv["INTERPOLATED_KEY"], "HelloWorld_appended")
        self.assertEqual(dotenv["SYS_INTERPOLATED_KEY"], "system_value")
        self.assertEqual(dotenv["EXPORTED_KEY"], "exported_value")

    def test_mismatched_quotes_not_treated_as_string(self):
        with open(self.file_path, "w", encoding="utf-8") as f:
            f.write("MISMATCHED='value\"\n")

        dotenv = DotEnv(self.file_path)
        # Mismatched quotes should NOT strip quotes or force string type
        self.assertIn("'", dotenv["MISMATCHED"])

    def test_update_system_env(self):
        DotEnv(self.file_path, update_system_env=True)
        self.assertEqual(os.environ.get("STRING_KEY"), "HelloWorld")
        self.assertEqual(os.environ.get("INT_KEY"), "1234")

        del os.environ["STRING_KEY"]
        del os.environ["INT_KEY"]

    def test_mapping_behaviors(self):
        dotenv = DotEnv(self.file_path)
        self.assertIn("STRING_KEY", dotenv)
        self.assertEqual(len(dotenv), 15)

        dotenv["NEW_KEY"] = 99
        self.assertEqual(dotenv["NEW_KEY"], 99)
        del dotenv["NEW_KEY"]
        self.assertNotIn("NEW_KEY", dotenv)

    def test_raises_error_on_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            DotEnv("missing_file.env")

    def test_raises_error_on_key_not_found(self):
        with self.assertRaises(KeyError):
            _ = DotEnv(self.file_path)["NON_EXISTENT_KEY"]

    def test_config_handle_key_not_found(self):
        dotenv_with_handling = DotEnv(self.file_path, handle_key_not_found=True)
        self.assertIsNone(dotenv_with_handling["NON_EXISTENT_KEY"])

    def test_invalid_format(self):
        with open(self.file_path, "w", encoding="utf-8") as f:
            f.write("INVALID_LINE\n")

        with self.assertRaises(ParsingError):
            DotEnv(self.file_path)

    def test_to_dict_returns_copy(self):
        dotenv = DotEnv(self.file_path)
        d = dotenv.to_dict()
        d["INJECTED"] = "bad"
        self.assertNotIn("INJECTED", dotenv)

    def test_empty_interpolation_not_consumed(self):
        with open(self.file_path, "w", encoding="utf-8") as f:
            f.write("KEY=${}\n")
        dotenv = DotEnv(self.file_path)
        self.assertEqual(dotenv["KEY"], "${}")

    def test_pathlib_path_accepted(self):
        import pathlib
        dotenv = DotEnv(pathlib.Path(self.file_path))
        self.assertEqual(dotenv["STRING_KEY"], "HelloWorld")

    def test_repr_does_not_expose_values(self):
        dotenv = DotEnv(self.file_path)
        r = repr(dotenv)
        self.assertNotIn("HelloWorld", r)
        self.assertIn("STRING_KEY", r)

    def test_setitem_rejects_invalid_type(self):
        dotenv = DotEnv(self.file_path)
        with self.assertRaises(TypeError):
            dotenv["BAD"] = [1, 2, 3]

if __name__ == "__main__":
    unittest.main()
