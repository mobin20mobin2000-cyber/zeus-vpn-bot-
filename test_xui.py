from xui_client import XUI_API

api = XUI_API(
    "https://YOUR_PANEL:PORT",
    "USERNAME",
    "PASSWORD"
)

print(api.login())

print(api.get_inbounds())
