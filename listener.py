from database import DatabaseHandler
import os
import requests
import threading
import time


def _send_webhook_update(data):
    webhook_url = os.environ['WEBHOOK_URL']  # TODO: Support more than 1 webhook
    try:
        requests.post(webhook_url, {'content': data})
    except requests.exceptions.RequestException as error:
        print(error)


class ApiPoller(threading.Thread):
    database = None
    last_seen_id = 0  # gid
    last_seen_date = 0  # Unix time stamp
    lock = threading.Lock()
    keep_polling = True

    def __init__(self):
        super(ApiPoller, self).__init__()
        self.__stop_event = threading.Event()
        dbname = os.environ['DB_NAME']
        dbuser = os.environ['DB_USER']
        dbpass = os.environ['DB_PASS']
        dbhost = os.environ['DB_HOST']
        dbport = os.environ['DB_PORT']
        self.database = DatabaseHandler(dbname=dbname,
                                        user=dbuser,
                                        password=dbpass,
                                        host=dbhost,
                                        port=dbport)

    def start_polling_api(self):
        self.database.create_tables()
        last_seen = self.database.get_last_seen(570)
        self.last_seen_id = last_seen[1]
        self.last_seen_date = last_seen[2]
        print("Started listening for new updates")
        while self.keep_polling:
            thread = threading.Thread(target=self.request_update_info)
            thread.start()
            time.sleep(1)

    def stop_polling_api(self):
        self.__stop_event.set()
        self.keep_polling = False

    def request_update_info(self):
        response = requests.get("http://api.steampowered.com/ISteamNews/GetNewsForApp/v0002/?appid=570&count=1"
                                "&maxlength=300&format=json")
        response_as_json = response.json()
        last_update_item = response_as_json['appnews']['newsitems'][0]
        if self._should_update(last_update_item):
            self.update(last_update_item)

    def update(self, update_item):
        try:
            self.lock.acquire()
            self.last_seen_id = update_item['gid']
            self.last_seen_date = update_item['date']
            print("New last seen id: ", self.last_seen_id)
            print("New last seen date: ", self.last_seen_date)
            self.database.update_last_seen(570, self.last_seen_id, self.last_seen_date)
            _send_webhook_update(update_item['url'])
        finally:
            self.lock.release()

    def _should_update(self, latest_update_item):
        gid = latest_update_item['gid']
        date = latest_update_item['date']
        feedname = latest_update_item['feedname']
        return self.last_seen_date < date and self.last_seen_id != gid and feedname == 'steam_updates'
