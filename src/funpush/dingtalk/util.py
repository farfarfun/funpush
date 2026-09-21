import base64
import hashlib
import hmac
import time
import urllib.parse

from urllib.parse import quote


def dingtalk_url_decode(url: str, pc_slide: bool = True) -> str:
    """将普通 URL 转换为钉钉客户端链接。"""
    url = quote(url, "utf-8")
    return f"dingtalk://dingtalkclient/page/link?url={url}&pc_slide={pc_slide}"


def get_sign(secret: str) -> tuple[str, str]:
    """根据钉钉机器人密钥生成时间戳和签名。"""
    timestamp = str(round(time.time() * 1000))
    secret_enc = secret.encode("utf-8")
    string_to_sign = "{}\n{}".format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode("utf-8")
    hmac_code = hmac.new(
        secret_enc, string_to_sign_enc, digestmod=hashlib.sha256
    ).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    return timestamp, sign
