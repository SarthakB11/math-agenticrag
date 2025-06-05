import os
try:
    import tomllib  # Python 3.11+
    def load_toml(path):
        with open(path, "rb") as f:
            return tomllib.load(f)
except ImportError:
    import tomli
    def load_toml(path):
        with open(path, "rb") as f:
            return tomli.load(f)

CONFIG_PATH = os.getenv("APP_CONFIG_PATH", os.path.join(os.path.dirname(__file__), "..", "config.toml"))
CONFIG = load_toml(CONFIG_PATH)
