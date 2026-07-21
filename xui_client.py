api = XUI_API(
    "https://panel.com:port",
    "username",
    "password"
)
api.login()
api.get_inbounds()
api.create_vless_user(
    inbound_id=1,
    email="test@example.com",
    days=30,
    traffic_gb=50
)
