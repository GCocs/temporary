import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


def getEnv(key):
    try:
        return os.environ[key]
    except:
        print(f"KEY_ERROR({key})")
        return f"KEY_ERROR({key})"


if __name__ == "__main__":
    pass