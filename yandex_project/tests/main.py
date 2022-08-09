from functional.utils import wait_for_es, wait_for_redis


if __name__ == '__main__':
    wait_for_es()
    wait_for_redis()
