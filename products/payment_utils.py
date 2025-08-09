from cinetpay_sdk.s_d_k import Cinetpay
from django.conf import settings

def get_client():
    return Cinetpay(
        apikey=settings.CINETPAY_APIKEY,
        site_id=settings.CINETPAY_SITE_ID
    )
