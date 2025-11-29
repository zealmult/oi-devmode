"""
title: oi-devmode
author: zealmult
author_url: https://github.com/zealmult/oi-devmode
funding_url: https://breathai.top/
version: 1.0
"""

import time
import json
from typing import Optional, Callable, Awaitable, Any
from pydantic import BaseModel, Field

# V3 - Fixed compatibility issues for stream hook between API (bytes) and frontend (dict)


class Filter:
    """
    [DevLogger V3] Developer Mode - Backend Log Printer.

    V3 Update:
    Fixed the stream hook. It now correctly distinguishes
    between dict events from the frontend and bytes events from the API,
    logging them appropriately.
    """

    # --- Configuration Valves ---
    class Valves(BaseModel):
        priority: int = Field(
            default=1,
            description="Priority is set to 1 to ensure it logs the raw request before any other filters."
        )

        enabled: bool = Field(
            default=False,
            description="IMPORTANT: Whether to enable developer logging. Turn ON during debugging, turn OFF immediately after!"
        )

        log_inlet: bool = Field(
            default=True,
            description="Whether to log [INLET] (user request) events."
        )

        log_stream: bool = Field(
            default=True,
            description="Whether to log [STREAM] (AI streaming responses) events."
        )

        log_outlet: bool = Field(
            default=True,
            description="Whether to log [OUTLET] (frontend-saved) events."
        )

        log_user_info: bool = Field(
            default=True,
            description="Whether to include the full __user__ dict inside INLET logs."
        )

        truncate_message: int = Field(
            default=0,
            description="Message truncation length. Set to 0 to print full messages."
        )

    def __init__(self):
        self.file_handler = False
        self.valves = self.Valves()

        # V3: Used to temporarily store user info for stream/outlet logs
        self.last_user_info = {}
        self.last_model_id = "N/A"

    # --- Helper Function: Format & Print Logs ---
    def _print_log(self, log_type: str, user_info: dict, model_id: str, message: dict):
        # (same as V2)
        header = f"\n{'-'*30} [DEV_LOGGER | {log_type}] {'-'*30}"

        user_str = f"USER: {user_info.get('email', 'N/A')} (Role: {user_info.get('role', 'N/A')})"
        model_str = f"MODEL: {model_id}"

        msg_content = message.get("content", "")

        truncate_len = self.valves.truncate_message
        if truncate_len > 0 and msg_content and len(msg_content) > truncate_len:
            msg_content = (
                msg_content[:truncate_len]
                + f"... [truncated, {len(msg_content) - truncate_len} chars omitted]"
            )

        message_str = f"MESSAGE (Role: {message.get('role', 'N/A')}):\n{msg_content}"

        footer = f"{'-'* (64 + len(log_type))}\n"

        print(header)
        print(user_str)
        print(model_str)
        print(message_str)

        if log_type == "INLET" and self.valves.log_user_info:
            try:
                user_details = json.dumps(user_info, indent=2, default=str)
                print(f"__USER__ dictionary details:\n{user_details}")
            except Exception as e:
                print(f"Failed to serialize __USER__ dictionary: {e}")

        print(footer)

    # --- Core: INLET Function ---
    async def inlet(
        self,
        body: dict,
        __user__: Optional[dict] = None,
        __model__: Optional[dict] = None,
        __event_emitter__: Optional[Callable[[Any], Awaitable[None]]] = None,
    ) -> dict:

        # Save for stream/outlet logs
        if __user__:
            self.last_user_info = __user__
            self.last_model_id = __model__["id"] if __model__ else "N/A"

        if not self.valves.enabled or not self.valves.log_inlet or __user__ is None:
            return body

        try:
            last_message = {}
            if "messages" in body and len(body["messages"]) > 0:
                last_message = body["messages"][-1]

            self._print_log(
                log_type="INLET",
                user_info=self.last_user_info,
                model_id=self.last_model_id,
                message=last_message,
            )
        except Exception as e:
            print(f"[DEV_LOGGER] Error while logging INLET: {e}")

        return body

    # --- V3 Key Update: Stream Hook (Type-aware) ---
    async def stream(
        self,
        event: Any,  # May be dict or bytes
        __user__: Optional[dict] = None,
        __model__: Optional[dict] = None,
        __event_emitter__: Optional[Callable[[Any], Awaitable[None]]] = None,
    ) -> Any:  # Must return same type as received

        if not self.valves.enabled or not self.valves.log_stream:
            return event

        try:
            # Distinguish frontend vs API
            if isinstance(event, dict):
                # 1. Frontend path (dict)
                chunk_content = ""
                if "choices" in event and event["choices"]:
                    delta = event["choices"][0].get("delta", {})
                    chunk_content = delta.get("content")  # Safe get

                if chunk_content:
                    print(f"[DEV_LOGGER | STREAM] (Dict) AI streaming: {chunk_content}")

            elif isinstance(event, bytes):
                # 2. API path (bytes)
                try:
                    decoded_event = event.decode("utf-8")
                    print(
                        f"[DEV_LOGGER | STREAM] (Bytes) AI streaming: {decoded_event.strip()}"
                    )
                except UnicodeDecodeError:
                    # Possibly non-text (e.g., image stream)
                    print(f"[DEV_LOGGER | STREAM] (Bytes) AI streaming (raw): {event}")

            else:
                # 3. Unknown type
                print(
                    f"[DEV_LOGGER | STREAM] (Unknown Type: {type(event)}) Data: {str(event)[:100]}"
                )

        except Exception as e:
            print(f"[DEV_LOGGER] STREAM internal error: {e}")

        # Must return the raw event unchanged
        return event

    # --- Core: OUTLET Function ---
    async def outlet(
        self,
        body: dict,
        __user__: Optional[dict] = None,
        __model__: Optional[dict] = None,
        __event_emitter__: Optional[Callable[[Any], Awaitable[None]]] = None,
    ) -> dict:

        if not self.valves.enabled or not self.valves.log_outlet or __user__ is None:
            return body

        try:
            model_id = __model__["id"] if __model__ is not None else "N/A"

            last_ai_message = {}
            if "messages" in body and len(body["messages"]) > 0:
                for msg in reversed(body["messages"]):
                    if msg.get("role") == "assistant":
                        last_ai_message = msg
                        break

            self._print_log(
                log_type="OUTLET",
                user_info=self.last_user_info,
                model_id=model_id,
                message=last_ai_message,
            )
        except Exception as e:
            print(f"[DEV_LOGGER] Error while logging OUTLET: {e}")

        return body
