from typing import TypedDict


class NotifyOptional(TypedDict, total=False):
    params: dict


class Notify(NotifyOptional):
    jsonrpc: str
    method: str


def create_notify(method: str, src: dict) -> Notify:
    return {
        "jsonrpc": "2.0",
        "method": method,
        "params": src,
    }
