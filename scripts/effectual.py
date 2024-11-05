import os
import json
import tomllib
import pathlib
import shutil
import zipfile
import numpy as np
import python_minifier
from time import perf_counter


def pathLeaf(path) -> str:
    return str(os.path.split(path)[1]).strip()


def minification(fileName: str) -> None:
    with open(fileName, "r+") as fileRW:
        minifiedCode = python_minifier.minify(
            fileRW.read(),
            rename_locals=False,
            rename_globals=False,
            hoist_literals=False,
        )  # I don't rename vars as that could cause problems when importing between files
        # Also no hoisting literals as that causes un-needed variable assignment
        fileRW.seek(0)
        fileRW.writelines(minifiedCode)
        fileRW.truncate()


def bundle() -> None:
    """Bundles python files and dependencies into a single file"""

    shutil.rmtree(OUTPUTDIRECTORY)  # Deletes current contents of output directory
    shutil.copytree(
        SOURCEDIRECTORY, OUTPUTDIRECTORY
    )  # Copies source to output directory

    pythonFiles = np.array(
        [
            str(entry).replace(
                os.sep, "/"
            )  # Appends a string of the file path with forward slashes
            for entry in pathlib.Path(
                OUTPUTDIRECTORY
            ).iterdir()  # For all the file entries in the directory
            if ".py" in str(pathlib.Path(entry))
        ]
    )  # If it is a verified file and is a python file

    with open("./Pipfile", "rb") as file:
        packages: dict = dict((tomllib.load(file)).get("packages"))

    try:
        with open("./.effectual_cache/dependencies.json", "x") as file:
            file.write("{\n\n}")
    except FileExistsError:
        pass
    with open("./.effectual_cache/dependencies.json", "r") as jsonFileRead:
        try:
            fileContents: dict = json.load(jsonFileRead)
        except FileNotFoundError:
            fileContents: dict = {}
        for key in packages:
            if fileContents == {} or key not in packages:
                print(f"Installing {key}")
                if packages.get(key) == "*":
                    os.system(
                        f"pip install {key} --quiet --target ./.effectual_cache/cachedPackages"
                    )
                else:
                    os.system(
                        f"pip install {key}=={packages.get(key)} --quiet --target ./.effectual_cache/cachedPackages"
                    )
                fileContents.update({key: packages.get(key)})
                json.dump(
                    fileContents, open("./.effectual_cache/dependencies.json", "w")
                )

    requiredFiles = np.array(
        [
            str(file)
            for file in pathlib.Path("./.effectual_cache/cachedPackages").rglob("*")
            if (
                "__pycache__" not in str(file)
                and ".dist-info" not in str(file)
                and ".pyc" not in str(file)
                and ".pyd" not in str(file)
                and "normalizer.exe" not in str(file)
                and "py.typed" not in str(file)
            )
        ]
    )

    with zipfile.ZipFile(
        f"{OUTPUTDIRECTORY}{OUTPUTFILENAME}",
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=COMPRESSIONLEVEL,
    ) as bundler:
        print("Bundling packages")
        for file in requiredFiles:
            arcname = file.replace(os.sep, "/").replace(
                ".effectual_cache/cachedPackages", ""
            )
            bundler.write(file, arcname=arcname)

        print("Bundling python source files")
        for file in pythonFiles:
            if MINIFICATION:
                minification(str(file))
            bundler.write(
                file, arcname=pathLeaf(file)
            )  # pathleaf is needed to not maintain folder structure
            os.remove(file)  # Clean up


if "__main__" in __name__:
    with open("./effectual.config.json", "r") as file:
        configData: dict = json.load(file)

    SOURCEDIRECTORY: str = configData.get("sourceDirectory")
    OUTPUTDIRECTORY: str = configData.get("outputDirectory")
    OUTPUTFILENAME: str = configData.get("outputFileName")
    COMPRESSIONLEVEL: int = configData.get("compressionLevel")  # From 0-9
    MINIFICATION: bool = configData.get("minification")

    if not os.path.exists(OUTPUTDIRECTORY):
        os.makedirs(OUTPUTDIRECTORY)

    pathlib.Path("./.effectual_cache/cachedPackages").mkdir(parents=True, exist_ok=True)

    start = perf_counter()
    bundle()
    end = perf_counter()

    print(f"Bundled in {end - start} seconds")
