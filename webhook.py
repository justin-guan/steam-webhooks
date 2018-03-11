from listener import ApiPoller
from shutdown import GracefulShutdown

if __name__ == '__main__':
    listener = ApiPoller()
    killer = GracefulShutdown(listener.stop_polling_api)
    killer.wait_for_stop_signals()
    listener.start_polling_api()
