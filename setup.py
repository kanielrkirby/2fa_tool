from cx_Freeze import setup, Executable

setup(
    name="2fa_tool",
    version="0.1",
    description="2FA Tool",
    executables=[Executable("2fa_tool.py", base="console", target_name="tfa_tool")],
)