from typing import Tuple, Union
from urllib.parse import ParseResult, urlencode, urlunparse

import botocore.session
import redis

from botocore.model import ServiceId
from botocore.signers import RequestSigner
from django.core.cache import caches


class ElastiCacheIAMProvider(redis.CredentialProvider):
    TOKEN_TTL = 900

    def __init__(self, user, cluster_name, region):
        self.user = user
        self.cluster_name = cluster_name
        self.region = region

        session = botocore.session.get_session()
        self.request_signer = RequestSigner(
            ServiceId("elasticache"),
            self.region,
            "elasticache",
            "v4",
            session.get_credentials(),
            session.get_component("event_emitter"),
        )

        self.cache_key = f"elasticache_{user}_{cluster_name}_{region}"

    def get_credentials(self) -> Union[Tuple[str], Tuple[str, str]]:
        if (signed_url := caches["memory"].get(self.cache_key)) is None:
            query_params = {"Action": "connect", "User": self.user}
            url = urlunparse(
                ParseResult(
                    scheme="https",
                    netloc=self.cluster_name,
                    path="/",
                    query=urlencode(query_params),
                    params="",
                    fragment="",
                )
            )
            signed_url = self.request_signer.generate_presigned_url(
                {"method": "GET", "url": url, "body": {}, "headers": {}, "context": {}},
                operation_name="connect",
                expires_in=self.TOKEN_TTL,
                region_name=self.region,
            )
            # RequestSigner only seems to work if the URL has a protocol, but
            # Elasticache only accepts the URL without a protocol
            # So strip it off the signed URL before returning
            signed_url = signed_url.removeprefix("https://")

            # Reduce cache TTL a few seconds to ensure the token is still valid
            # by the time it's used
            caches["memory"].set(self.cache_key, signed_url, self.TOKEN_TTL - 5)

        return self.user, signed_url
