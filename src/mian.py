from src.clean_history import clean_history_data
from src.query_ips import query_ips


def main():
    query_ips()
    clean_history_data()


if __name__ == "__main__":
    main()