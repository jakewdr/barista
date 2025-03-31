import os
from pathlib import Path
from tkinter import END
from tkinter.filedialog import askopenfilename, asksaveasfilename

import customtkinter
import pygments.lexers
from chlorophyll import CodeView
from CTkMenuBar import CTkTitleMenu, CustomDropdownMenu

import cfg


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # Window creation ->
        self.title("barista ")

        w, h = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry("%dx%d+0+0" % (w, h))

        # Wait ->
        self.update_idletasks()

        # Theme configuration ->
        self._configureTheme()

        # Create code view ->
        self.codeView = CodeView(
            self, color_scheme=colourScheme, blockcursor=blockCursor, tab_width=tabWidth
        )
        self.codeView.pack(fill="both", expand=True)
        self.codeView.config(font=("Consolas", 20))

        # Menu bar ->
        self._configureMenuBar()

        self.currentFile = None  # No file loaded in the main view

    def _configureTheme(self):
        # Apply appearance mode
        appearanceMode = str(appearanceSettings.get("appearanceMode")).lower()
        if appearanceMode in ["light", "dark", "system"]:
            customtkinter.set_appearance_mode(appearanceMode)
        else:
            customtkinter.set_appearance_mode("system")

        # Apply custom themes if enabled ->
        if useCustomThemes:
            try:
                fileName = appearanceSettings.get("customThemeFileName")
                customtkinter.set_default_color_theme(f"/config/custom/{fileName}.json")
            except FileNotFoundError:
                customtkinter.set_default_color_theme("dark-blue")

    def _configureMenuBar(self):
        menu = CTkTitleMenu(master=self)
        fileMenu = menu.add_cascade(" File")  # Space added for better menu bar padding
        menu.add_cascade("Settings")
        menu.add_cascade("Run", command=self._runFile)

        fileDropdown = CustomDropdownMenu(widget=fileMenu)
        fileDropdown.add_option(option="Open", command=self._openFile)
        fileDropdown.add_option(option="Save", command=self._saveFile)
        fileDropdown.add_option(option="Save As", command=self._saveAsFile)

    def _openFile(self):
        filePath = askopenfilename(
            defaultextension=defaultExtension,
            filetypes=fileTypes,
        )
        if filePath:
            self.currentFile = filePath
            self.codeView.delete(1.0, END)
            try:
                # Dynamically determine the lexer
                lexer = pygments.lexers.get_lexer_for_filename(filePath)
                self.codeView.config(lexer=lexer)
            except pygments.lexers.ClassNotFound:
                print(f"No lexer found for file: {filePath}. Defaulting to plain text.")
                self.codeView.config(
                    lexer=pygments.lexers.TextLexer()
                )  # Fallback to plain text

            with open(filePath, "r") as file:
                self.codeView.insert(1.0, file.read())

    def _saveFile(self):
        if self.currentFile:
            with open(self.currentFile, "w") as file:
                file.write(self.codeView.get(1.0, END))
        else:
            self._saveAsFile()

    def _saveAsFile(self):
        filePath = asksaveasfilename(
            initialfile=f"{defaultFileName}{defaultExtension}",
            defaultextension=defaultExtension,
            filetypes=fileTypes,
        )
        if filePath:
            self.currentFile = filePath
            with open(filePath, "w") as file:
                file.write(self.codeView.get(1.0, END))
        try:
            # Dynamically determine the lexer
            lexer = pygments.lexers.get_lexer_for_filename(filePath)
            self.codeView.config(lexer=lexer)
        except pygments.lexers.ClassNotFound:
            print(f"No lexer found for file: {filePath}. Defaulting to plain text.")
            self.codeView.config(
                lexer=pygments.lexers.TextLexer()
            )  # Fallback to plain text view

    def _runFile(self):
        if not self.currentFile:
            print("No file to run. Please save or open a file first.")
            return

        # Determine the run command based on file extension
        fileExtension = os.path.splitext(self.currentFile)[1].lower()

        commands = {
            ".py": f"python {self.currentFile}",  # Python
            ".js": f"node {self.currentFile}",  # JavaScript
            ".ts": f"node --experimental-strip-types {self.currentFile}",  # TypeScript
            ".sh": f"bash {self.currentFile}",  # Shell script
            ".go": f"go run {self.currentFile}",  # Go
            ".rs": f"cargo run --manifest-path {os.path.dirname(self.currentFile)}/Cargo.toml",  # Rust (assumes Cargo project)
            ".java": f"javac {self.currentFile} && java {os.path.splitext(os.path.basename(self.currentFile))[0]}",  # Java
            ".c": f"gcc {self.currentFile} -o {os.path.splitext(self.currentFile)[0]} && ./{os.path.splitext(self.currentFile)[0]}",  # C
            ".cpp": f"g++ {self.currentFile} -o {os.path.splitext(self.currentFile)[0]} && ./{os.path.splitext(self.currentFile)[0]}",  # C++
        }

        command = commands.get(fileExtension, None)
        if command:
            print(f"Running: {command}")
            os.system(
                f"wt {command}"
            )  # Using Windows Terminal to execute in a new Window
        else:
            print(f"File type '{fileExtension}' is not supported for execution.")


if __name__ == "__main__":
    # Important variables ->
    scriptLocation = Path(os.path.dirname(__file__))

    fileTypes = [
        ("All Files", "*.*"),
        ("Python Files", "*.py;*.pyw"),
        ("JavaScript Files", "*.js;*.jsx;*.mjs;*.cjs;"),
        ("TypeScript Files", "*.ts;*.tsx;*.mts;*.cts;"),
        ("HTML Files", "*.html"),
        ("CSS Files", "*.css"),
        ("C Files", "*.c;*.h"),
        ("C++ Files", "*.cpp"),
        ("Java Files", "*.java"),
        ("Go Files", "*.go"),
        ("Rust Files", "*.rs"),
        ("Shell Scripts", "*.sh"),
        ("Batch Scripts", "*.bat"),
        ("Markdown Files", "*.md"),
        ("Text Files", "*.txt"),
        ("YAML Files", "*.yaml;*.yml"),
        ("JSON Files", "*.json"),
        ("XML Files", "*.xml"),
    ]

    # Load appearance settings ->
    appearanceSettings = cfg.unpack(scriptLocation / Path("config/appearance.json"))
    blockCursor = bool(appearanceSettings.get("blockCursor"))
    colourScheme = str(appearanceSettings.get("textTheme"))
    useCustomThemes = bool(appearanceSettings.get("useCustomThemes"))
    tabWidth = int(appearanceSettings.get("tabWidth"))

    # Load editor settings ->
    editorSettings = cfg.unpack(scriptLocation / Path("config/editor.json"))
    defaultFileName = str(editorSettings.get("defaultFileName"))
    defaultExtension = str(editorSettings.get("defaultExtension"))

    app = App()
    app.mainloop()
