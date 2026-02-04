import uuid
from datetime import datetime
from typing import Any


class UnifiedMessage:
    """
    Canonical message object shared by ALL engines.
    Phase 1: In-memory, synchronous.
    Phase 2: Network-serializable.
    """

    def __init__(
        self,
        engine_source: str,
        input_type: str,           # "text" | "audio" | "event" | "signal"
        raw_payload: Any,
        timestamp: str | None = None,
        source_device: str = "unknown",
        confidence: float = 1.0,
        privacy_flag: bool = False,
        session_id: str | None = None,
        payload_type: str = "string"  # "string" | "binary" | "dict"
    ):
        self.engine_source = engine_source
        self.input_type = input_type
        self.raw_payload = raw_payload
        self.timestamp = timestamp or datetime.utcnow().isoformat()
        self.source_device = source_device
        self.confidence = confidence
        self.privacy_flag = privacy_flag
        self.session_id = session_id or str(uuid.uuid4())
        self.payload_type = payload_type

    @classmethod
    def create(
        cls,
        input_type: str,
        raw_payload: Any,
        source_device: str = "unknown",
        engine_source: str = "ENGINE_001"
    ):
        """
        Convenience factory for Phase 1 engines.
        Automatically infers payload_type.
        """
        if input_type == "audio":
            payload_type = "binary"
        elif input_type in ("event", "signal"):
            payload_type = "dict"
        else:
            payload_type = "string"

        return cls(
            engine_source=engine_source,
            input_type=input_type,
            raw_payload=raw_payload,
            source_device=source_device,
            payload_type=payload_type
        )

    def __repr__(self) -> str:
        payload_preview = (
            "<binary>"
            if self.payload_type == "binary"
            else self.raw_payload
        )

        return (
            f"UnifiedMessage("
            f"engine_source={self.engine_source}, "
            f"input_type={self.input_type}, "
            f"source_device={self.source_device}, "
            f"timestamp={self.timestamp}, "
            f"session_id={self.session_id}, "
            f"confidence={self.confidence}, "
            f"privacy_flag={self.privacy_flag}, "
            f"payload_type={self.payload_type}, "
            f"raw_payload={payload_preview})"
        )
