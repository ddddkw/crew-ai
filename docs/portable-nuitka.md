# Nuitka portable build

This project can be distributed as a portable Windows folder:

```text
CrewAI-Studio-Portable/
  CrewAI Studio.exe
  Stop CrewAI Studio.exe
  app/
  img/
  .streamlit/
  .env
  crewai.db
  knowledge/
  logs/
  python-runtime/
    python.exe
    Lib/
    DLLs/
    Lib/site-packages/
  *.dll / *.pyd / runtime files from Nuitka
```

Users open `CrewAI Studio.exe`. The launcher starts the Streamlit app on a local
address, opens the default browser, and stores user data next to the executable.
Closing the browser tab does not stop the local server; use
`Stop CrewAI Studio.exe` from the same folder to stop it.

## Build

From the repository root:

```powershell
.\scripts\build_portable_nuitka.ps1 -InstallBuildDeps -Clean
```

For later builds, after Nuitka is already installed:

```powershell
.\scripts\build_portable_nuitka.ps1 -Clean
```

The output folder is:

```text
dist/CrewAI-Studio-Portable/
```

## Runtime behavior

- `.env` is copied from `.env_example` during packaging. The real repository
  `.env` is not copied, so API keys are not leaked into the release folder.
- If `DB_URL` is not set, the launcher uses `sqlite:///crewai.db` inside the
  portable folder.
- Uploaded knowledge files are stored in `knowledge/` inside the portable
  folder.
- Python dependencies are copied into `python-runtime/` instead of being fully
  compiled by Nuitka. This keeps the build practical for large dependencies such
  as Torch, Transformers, Docling, and ChromaDB while preserving the one-exe
  launch experience.
- The launcher prepares the environment, then runs
  `python-runtime/python.exe -m streamlit run app/app.py`.
- The launcher writes `logs/portable-processes.json` with the launcher and
  Streamlit child process IDs.
- `Stop CrewAI Studio.exe` reads that state file, verifies that the recorded
  processes are still running from this portable folder, then stops them.
- Launcher failures are written to `logs/launcher.log` and
  `logs/launcher-crash.log`; Streamlit child-process output is written to
  `logs/streamlit.stdout.log` and `logs/streamlit.stderr.log`.
- If port `8501` is busy, the launcher searches the next few local ports.
- Set `CREWAI_STUDIO_PORT` before launching to request a specific port.

## Debug build

Use a console window when diagnosing startup errors:

```powershell
.\scripts\build_portable_nuitka.ps1 -Clean -ShowConsole
```

## Important limitation

The first portable target keeps `app/*.py` and third-party package sources
visible in the output folder. That is intentional: Streamlit runs the page from
a script path, and the project's ML/AI dependencies are too large and dynamic
for a pleasant full-source Nuitka compile. If source hiding becomes a hard
requirement, the next step is to refactor `app/` into an importable package and
create a separate full-compile build profile for only the code that must be
hidden.

## Troubleshooting

- If Nuitka is missing, run the build with `-InstallBuildDeps`.
- If the first Windows build needs a compiler, install Microsoft Visual Studio
  Build Tools or allow Nuitka to download its supported compiler toolchain.
- The build disables GCC link-time optimization with `--lto=no`; in this
  environment the default MinGW LTO link step can fail before producing the
  executable.
- The package can be large because it carries the Python runtime and installed
  packages.
- If the executable opens and closes immediately, rebuild with `-ShowConsole`
  and check `logs/launcher.log` plus `logs/streamlit.stderr.log`.
- If the browser tab is closed but the app is still running, run
  `Stop CrewAI Studio.exe` from the portable folder.
- If an application dependency is missing only in the portable folder, install
  it into the source virtual environment and rebuild. Use
  `--include-package=...` only for modules imported by the compiled launcher
  itself.
