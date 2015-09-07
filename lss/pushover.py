"""
LSS Pushover backend
"""
import httplib
import urllib


class PushoverBackend(object):
    """LSS Pushover backend"""
    def __init__(self, logger, enabled, user_token, app_token):
        super(PushoverBackend, self).__init__()
        self._enabled = enabled
        self._user_token = user_token
        self._app_token = app_token
        self._logger = logger

    def send_message(self, title, message, priority=-1, sound=None, html=1):
        if not self._enabled:
            return True

        self._logger.debug("Sending pushover message")
        conn = httplib.HTTPSConnection("api.pushover.net:443")
        conn.request(
            "POST", "/1/messages.json",
            urllib.urlencode({
                "token": self._app_token,
                "user": self._user_token,
                "title": title,
                "message": message.encode("utf-8"),
                "html": html,
                "priority": priority,
            }),
            {
                "Content-type": "application/x-www-form-urlencoded"
            }
        )
        res = conn.getresponse()
        if res.status != 200:
            self._logger.error(
                "Sending pushover message failed: %s",
                res.read())
            return False

        return True
