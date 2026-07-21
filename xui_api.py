import json
import uuid
import time
import requests

from config import (
    PANEL_URL,
    PANEL_USERNAME,
    PANEL_PASSWORD
)


class XUI:

    def __init__(self):

        self.url = PANEL_URL.rstrip("/")

        self.username = PANEL_USERNAME

        self.password = PANEL_PASSWORD

        self.session = requests.Session()

        self.timeout = 20

        self.logged = False


    # -----------------------------
    # Login
    # -----------------------------

    def login(self):

        if self.logged:
            return True

        r = self.session.post(

            f"{self.url}/login",

            json={

                "username": self.username,
                "password": self.password

            },

            timeout=self.timeout

        )

        if r.status_code != 200:

            raise Exception("Cannot connect to 3x-ui")

        data = r.json()

        if not data.get("success"):

            raise Exception(data.get("msg", "Login Failed"))

        self.logged = True

        return True


    # -----------------------------
    # Request Helper
    # -----------------------------

    def post(self, endpoint, data=None):

        self.login()

        r = self.session.post(

            self.url + endpoint,

            data=data,

            timeout=self.timeout

        )

        result = r.json()

        if not result.get("success"):

            raise Exception(result)

        return result


    def get(self, endpoint):

        self.login()

        r = self.session.get(

            self.url + endpoint,

            timeout=self.timeout

        )

        result = r.json()

        if not result.get("success"):

            raise Exception(result)

        return result


    # -----------------------------
    # Inbounds
    # -----------------------------

    def get_inbounds(self):

        result = self.get(

            "/panel/api/inbounds/list"

        )

        return result["obj"]


    def get_inbound(self, inbound_id):

        inbounds = self.get_inbounds()

        for inbound in inbounds:

            if inbound["id"] == inbound_id:
                return inbound

        return None


    def find_vless_inbound(self):

        inbounds = self.get_inbounds()

        for inbound in inbounds:

            if inbound["protocol"] == "vless":

                return inbound

        raise Exception("No VLESS inbound found")
    # -----------------------------
    # UUID
    # -----------------------------

    def generate_uuid(self):
        return str(uuid.uuid4())


    # -----------------------------
    # Expire Time
    # -----------------------------

    def expire_time(self, days):
        return int((time.time() + days * 86400) * 1000)


    # -----------------------------
    # Subscription
    # -----------------------------

    def subscription_link(self, sub_id):
        return f"{self.url}/sub/{sub_id}"


    # -----------------------------
    # Create VLESS User
    # -----------------------------

    def create_vless_user(
        self,
        email,
        volume_gb,
        days,
        inbound_id=None
    ):

        if inbound_id is None:
            inbound = self.find_vless_inbound()
        else:
            inbound = self.get_inbound(inbound_id)

        inbound_id = inbound["id"]

        client_uuid = self.generate_uuid()

        sub_id = uuid.uuid4().hex[:16]

        total_bytes = volume_gb * 1024 * 1024 * 1024

        expire = self.expire_time(days)

        client = {
            "id": client_uuid,
            "flow": "",
            "email": email,
            "limitIp": 0,
            "totalGB": total_bytes,
            "expiryTime": expire,
            "enable": True,
            "tgId": "",
            "subId": sub_id
        }

        payload = {
            "id":
          # -----------------------------
    # Get Client
    # -----------------------------

    def get_client(self, email):

        inbounds = self.get_inbounds()

        for inbound in inbounds:

            settings = inbound.get("settings")

            if isinstance(settings, str):
                settings = json.loads(settings)

            clients = settings.get("clients", [])

            for client in clients:

                if client.get("email") == email:

                    return {
                        "client": client,
                        "inbound": inbound
                    }

        return None


    # -----------------------------
    # Delete Client
    # -----------------------------

    def delete_client(self, email):

        client = self.get_client(email)

        if client is None:
            raise Exception("Client not found")

        inbound_id = client["inbound"]["id"]

        self.post(

            f"/panel/api/inbounds/{inbound_id}/delClient/{email}"

        )

        return True


    # -----------------------------
    # Reset Traffic
    # -----------------------------

    def reset_client_traffic(self, email):

        client = self.get_client(email)

        if client is None:
            raise Exception("Client not found")

        inbound_id = client["inbound"]["id"]

        self.post(

            f"/panel/api/inbounds/resetClientTraffic/{inbound_id}/{email}"

        )

        return True


    # -----------------------------
    # Client Traffic
    # -----------------------------

    def get_client_traffic(self, email):

        client = self.get_client(email)

        if client is None:
            raise Exception("Client not found")

        inbound = client["inbound"]

        settings = inbound.get("clientStats", [])

        for stat in settings:

            if stat.get("email") == email:

                return stat

        return {}
      
