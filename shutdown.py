import signal


class GracefulShutdown:
    waiting_for_signals = False
    kill_now = False
    clean_up_function = None

    def __init__(self, clean_up_function):
        self.clean_up_function = clean_up_function

    def wait_for_stop_signals(self):
        if not self.waiting_for_signals:
            signal.signal(signal.SIGINT, self.clean_up_and_exit)
            signal.signal(signal.SIGTERM, self.clean_up_and_exit)
            self.waiting_for_signals = True

    def clean_up_and_exit(self, signum, frame):
        self.kill_now = True
        self.clean_up_function()
