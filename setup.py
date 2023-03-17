from cx_Freeze import setup, Executable

setup(
    name="2fa_tool",
    version="0.1",
    description="2FA Tool",
    executables=[Executable("main.py", base="console", target_name="tfa_tool")],
    options={"build_exe": {"packages": ["os", "io", "segno", "argparse", "sys", "json", "pyotp"], "include_files": ["config.json"]}},
)
