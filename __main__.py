import importlib
import os


def import_and_execute_functions(directory):
    for folder_name in os.listdir(directory):
        folder_path = os.path.join(directory, folder_name)
        if os.path.isdir(folder_path):
            module_names = [
                file_name[:-3]
                for file_name in os.listdir(folder_path)
                if file_name.endswith(".py")
                and file_name != "__init__.py"
                and folder_name != "modules"
            ]
            for module_name in module_names:
                module = importlib.import_module(f"{folder_name}.{module_name}")
                for func_name in dir(module):
                    if callable(getattr(module, func_name)):
                        getattr(module, func_name)()


if __name__ == "__main__":
    import_and_execute_functions(".")
