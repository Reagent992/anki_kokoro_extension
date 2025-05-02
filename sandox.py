import requests


def health_status() -> bool:
    try:
        requests.get("http://127.0.0.1:8880/health").raise_for_status()
    except requests.ConnectionError:
        return False
    return True


if __name__ == "__main__":
    print(health_status())
