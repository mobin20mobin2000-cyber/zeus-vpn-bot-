# xui_api.py
# X-UI API Client
# Part 1: Core / Login / Session / Requests

import requests
import json
import time


class XUI_API:
    """
    Client for interacting with 3X-UI / X-UI panel API
    """

    def __init__(self, host, username, password, timeout=15):
        """
        Initialize API client

        host:
            Example:
            https://example.com:54321

        username:
            Panel username

        password:
            Panel password
        """

        self.host = host.rstrip("/")
        self.username = username
        self.password = password

        self.timeout = timeout

        self.session = requests.Session()

        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json"
        })

        self.logged_in = False
        self.login_time = None


    # -----------------------------
    # Internal URL builder
    # -----------------------------

    def _url(self, path):
        """
        Build full API URL
        """

        if not path.startswith("/"):
            path = "/" + path

        return self.host + path



    # -----------------------------
    # Login
    # -----------------------------

    def login(self):
        """
        Login into X-UI panel

        Endpoint:
        /login

        Returns:
            True / False
        """

        url = self._url("/login")

        payload = {
            "username": self.username,
            "password": self.password
        }

        try:

            response = self.session.post(
                url,
                json=payload,
                timeout=self.timeout
            )

            data = response.json()

            if data.get("success"):

                self.logged_in = True
                self.login_time = int(time.time())

                return True

            return False


        except Exception as e:

            print("Login error:", e)

            return False



    # -----------------------------
    # Logout
    # -----------------------------

    def logout(self):
        """
        Logout current session
        """

        try:

            url = self._url("/logout")

            response = self.session.get(
                url,
                timeout=self.timeout
            )

            data = response.json()

            if data.get("success"):

                self.logged_in = False

                return True


        except Exception:

            pass


        return False



    # -----------------------------
    # Generic GET request
    # -----------------------------

    def get(self, endpoint, params=None):
        """
        Generic GET request
        """

        try:

            url = self._url(endpoint)

            response = self.session.get(
                url,
                params=params,
                timeout=self.timeout
            )

            return self._parse_response(response)


    # -----------------------------
    # Inbounds
    # -----------------------------

    def get_inbounds(self):
        """
        Get all inbounds
        """

        return self.get(
            "/panel/api/inbounds/list"
        )


    def get_inbound(self, inbound_id):
        """
        Get single inbound
        """

        return self.get(
            f"/panel/api/inbounds/get/{inbound_id}"
        )


    # -----------------------------
    # Client creation
    # -----------------------------

    def add_client(
        self,
        inbound_id,
        email,
        uuid,
        total_gb=0,
        expiry_time=0,
        enable=True
    ):
        """
        Add VLESS client to inbound

        expiry_time:
            Unix timestamp in milliseconds

        total_gb:
            Traffic limit in GB
        """

        total_bytes = 0

        if total_gb > 0:
            total_bytes = total_gb * 1024 * 1024 * 1024


        client = {
            "id": uuid,
            "email": email,
            "enable": enable,
            "limitIp": 0,
            "totalGB": total_bytes,
            "expiryTime": expiry_time,
            "flow": "",
            "subId": ""
        }


        payload = {
            "id": inbound_id,
            "settings": json.dumps({
                "clients": [
                    client
                ]
            })
        }


        return self.post(
            "/panel/api/inbounds/addClient",
            payload
        )



    def add_vless_client(
        self,
        inbound_id,
        email,
        uuid,
        days=30,
        total_gb=0
    ):
        """
        Create VLESS user with expiration
        """

        expiry = 0

        if days > 0:
            expiry = int(
                (time.time() + days * 86400) * 1000
            )


        return self.add_client(
            inbound_id=inbound_id,
            email=email,
            uuid=uuid,
            total_gb=total_gb,
            expiry_time=expiry
        )



    # -----------------------------
    # Client lookup helpers
    # -----------------------------

    def find_client(
        self,
        inbound_id,
        email
    ):
        """
        Find client by email
        """

        result = self.get_inbound(
            inbound_id
        )


        if not result.get("success"):
            return None


        obj = result.get("obj")

        if not obj:
            return None


        try:

            settings = json.loads(
                obj["settings"]
            )

            clients = settings.get(
                "clients",
                []
            )


            for client in clients:

                if client.get("email") == email:
                    return client


        except Exception:
            pass


        return None



    # -----------------------------
    # Update client
    # -----------------------------

    def update_client(
        self,
        inbound_id,
        client_id,
        client_data
    ):
        """
        Update existing client
        """

        payload = {
            "id": inbound_id,
            "clientId": client_id,
            "settings": json.dumps({
                "clients": [
                    client_data
                ]
            })
        }


        return self.post(
            "/panel/api/inbounds/updateClient/" + client_id,
            payload
        )



    # -----------------------------
    # Delete client
    # -----------------------------

    def delete_client(
        self,
        inbound_id,
        client_id
    ):
        """
        Delete client from inbound
        """

        return self.post(
            f"/panel/api/inbounds/{inbound_id}/delClient/{client_id}"
                )
            # -----------------------------
    # Client management
    # -----------------------------

    def list_clients(self, inbound_id):
        """
        Return all clients from inbound
        """

        inbound = self.get_inbound(
            inbound_id
        )

        if not inbound.get("success"):
            return []


        try:

            settings = json.loads(
                inbound["obj"]["settings"]
            )

            return settings.get(
                "clients",
                []
            )


        except Exception:

            return []



    def get_client_by_email(
        self,
        inbound_id,
        email
    ):
        """
        Search client by email
        """

        clients = self.list_clients(
            inbound_id
        )


        for client in clients:

            if client.get("email") == email:
                return client


        return None



    def delete_client_by_email(
        self,
        inbound_id,
        email
    ):
        """
        Delete client using email
        """

        client = self.get_client_by_email(
            inbound_id,
            email
        )


        if not client:
            return {
                "success": False,
                "error": "Client not found"
            }


        return self.delete_client(
            inbound_id,
            client["id"]
        )



    def set_client_status(
        self,
        inbound_id,
        client_id,
        enable=True
    ):
        """
        Enable or disable client
        """

        clients = self.list_clients(
            inbound_id
        )


        for client in clients:

            if client.get("id") == client_id:

                client["enable"] = enable

                return self.update_client(
                    inbound_id,
                    client_id,
                    client
                )


        return {
            "success": False,
            "error": "Client not found"
        }



    def update_client_expiry(
        self,
        inbound_id,
        email,
        days
    ):
        """
        Extend client expiration
        """

        client = self.get_client_by_email(
            inbound_id,
            email
        )


        if not client:

            return {
                "success": False,
                "error": "Client not found"
            }


        expiry = int(
            (time.time() + days * 86400)
            * 1000
        )


        client["expiryTime"] = expiry


        return self.update_client(
            inbound_id,
            client["id"],
            client
        )



    def update_client_traffic(
        self,

            # -----------------------------
    # VLESS Link Generator
    # -----------------------------

    def build_vless_link(
        self,
        client,
        server,
        port,
        security="none",
        remark=None
    ):
        """
        Build VLESS URI
        """

        uuid = client.get("id")

        email = (
            remark
            or client.get("email", "client")
        )


        link = (
            f"vless://{uuid}@{server}:{port}"
            f"?security={security}"
            f"#"
            f"{email}"
        )


        return link



    # -----------------------------
    # Get client subscription
    # -----------------------------

    def get_subscription_info(
        self,
        inbound_id,
        email
    ):
        """
        Return subscription data
        """

        client = self.get_client_by_email(
            inbound_id,
            email
        )


        if not client:

            return {
                "success": False,
                "error": "Client not found"
            }


        return {
            "success": True,
            "client": client,
            "subId": client.get(
                "subId",
                ""
            )
        }



    def get_subscription_url(
        self,
        base_url,
        sub_id
    ):
        """
        Build subscription URL
        """

        base_url = base_url.rstrip("/")

        return (
            f"{base_url}/sub/"
            f"{sub_id}"
        )



    # -----------------------------
    # User summary
    # -----------------------------

    def client_info(
        self,
        inbound_id,
        email
    ):
        """
        Return complete client information
        """

        client = self.get_client_by_email(
            inbound_id,
            email
        )


        if not client:
            return None


        return {
            "email": client.get("email"),
            "uuid": client.get("id"),
            "enable": client.get("enable"),
            "expiry": client.get("expiryTime"),
            "traffic": client.get("totalGB"),
            "subId": client.get("subId")
        }



    # -----------------------------
    # Ping API
    # -----------------------------

    def test_connection(self):
        """
        Test panel connection
        """

        try:

            result = self.get(
                "/panel/api/server/status"
            )

            return result.get(
                "success",
                False
            )

        except Exception:

            return False



    # -----------------------------
    # Context manager support
    # -----------------------------

    def __enter__(self):

        self.login()

        return self



    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback
    ):

        self.logout()
