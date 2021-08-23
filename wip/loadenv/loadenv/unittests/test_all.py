from pathlib import Path
import sys

root_dir = Path.cwd() / ".." if (Path.cwd() / "conftest.py").exists() else Path.cwd()
sys.path.append(str(root_dir))
from loadenv.EnvKeywordParser import EnvKeywordParser
from load_env import LoadEnv


#  Docstrings  #
################
def test_docstrings_exist_for_methods():
    class_list = [
        EnvKeywordParser,
        LoadEnv,
    ]

    for class_module in class_list:
        method_list = [
            func for func in dir(class_module)
            if callable(getattr(class_module, func))
            and not func.startswith("__")
        ]

        for method in method_list:
            doc_exists = True
            if getattr(class_module, method).__doc__ is None:
                doc_exists = False

            print(f"doc_exists({class_module.__name__}.{method}): "
                  f"{doc_exists}")
            assert doc_exists
