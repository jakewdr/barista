from pathlib import Path
from time import perf_counter

import PyInstaller.__main__
from python_minifier import minify


def executable() -> None:
    PyInstaller.__main__.run([
        "--noconfirm",
        "--onedir",
        "--windowed",
        '--add-data=./.venv/Lib/site-packages/customtkinter;customtkinter', 
        '--add-data=./.venv/Lib/site-packages/simplejson;simplejson',
        '--add-data=./.venv/Lib/site-packages/chlorophyll;chlorophyll', 
        '--add-data=./src/config;config',
        '--optimize=2',
        '--name=barista',
        '--python-option=OO', 
        "./src/__main__.py"
    ])

def minifyFile(filePath: Path) -> None:
    """Minifies a file from a certain path

    Args:
        filePath (Path): Path to the file to minify

    Raises:
        RuntimeError: In the event the file cannot be found or an error has occurred
    """
    try:
        with filePath.open("r+", encoding="utf-8") as fileRW:
            minifiedCode = minify(
                fileRW.read(),
                hoist_literals=False,
                remove_literal_statements=True,
                remove_debug=True,
            )

            fileRW.seek(0)
            fileRW.write(minifiedCode)
            fileRW.truncate()
    
    except Exception as e:
        raise RuntimeError(f"Failed to minify {filePath}: {e}")

if __name__ == "__main__":
    startTime = perf_counter()
    executable()
    for file in Path("./dist/barista/_internal").rglob("*"):
        if "tests" in str(file):
            print(f"Skipped {file}")
            continue
        elif file.suffix == ".py":
            print(f"Minifying {file}")
            minifyFile(file)
    endTime = perf_counter()
    
    print(f"\nCompleted in {endTime - startTime:.4f}s")