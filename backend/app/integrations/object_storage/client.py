"""The ObjectStore port and its S3 implementation.

`put_if_absent` is the content-addressed store's primitive: snapshot blobs
are keyed by their SHA-256, so identical content is stored exactly once and
a key, once written, is never overwritten (immutability by construction).
"""

from typing import Any, Protocol


class ObjectStoreError(Exception):
    """The object store could not complete the operation."""


class ObjectStore(Protocol):
    def put_if_absent(self, key: str, data: bytes, *, content_type: str) -> None: ...

    def get(self, key: str) -> bytes: ...

    def exists(self, key: str) -> bool: ...


class S3ObjectStore:
    def __init__(self, *, endpoint_url: str, access_key: str, secret_key: str, bucket: str) -> None:
        # The vendor dialect is contained in this module (ADR-004); boto3 ships untyped.
        import boto3  # type: ignore[import-untyped]  # noqa: PLC0415

        self._bucket = bucket
        self._client: Any = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )

    def put_if_absent(self, key: str, data: bytes, *, content_type: str) -> None:
        if self.exists(key):
            return
        try:
            self._client.put_object(
                Bucket=self._bucket, Key=key, Body=data, ContentType=content_type
            )
        except Exception as exc:
            raise ObjectStoreError(f"put failed for {key}") from exc

    def get(self, key: str) -> bytes:
        try:
            response = self._client.get_object(Bucket=self._bucket, Key=key)
            return bytes(response["Body"].read())
        except Exception as exc:
            raise ObjectStoreError(f"get failed for {key}") from exc

    def exists(self, key: str) -> bool:
        try:
            self._client.head_object(Bucket=self._bucket, Key=key)
            return True
        except self._client.exceptions.ClientError:
            return False

    def ensure_bucket(self) -> None:
        """Create the bucket when absent — local/dev convenience (MinIO)."""
        try:
            self._client.head_bucket(Bucket=self._bucket)
        except self._client.exceptions.ClientError:
            self._client.create_bucket(Bucket=self._bucket)
