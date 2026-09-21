"""
Generic wrapper around the EDMC overlay.

Handles detection of whichever overlay backend is installed and exposes a small set of primitives that no-op cleanly
when no overlay is installed or running.
"""
import inspect
from typing import Any

from .debug import Debug

class Overlay:
    """
    Class to provide a thin wrapper of safe overlay calls.
    """

    FAILURE_THRESHOLD:int = 5 # consecutive failures before giving up on this overlay for the rest of the session

    def __init__(self) -> None:
        self._overlay:Any = None
        self.available:bool = False
        self.is_modern:bool = False
        self.supports_circle:bool = False # a native "circle" send_shape -- pre-release as of this writing
        self._warned:bool = False
        self._consecutive_failures:int = 0

        self._detect()

    def _detect(self) -> None:
        """ Probe for an installed overlay backend """
        try:
            from EDMCOverlay import edmcoverlay # type: ignore
        except ImportError:
            try:
                from edmcoverlay import edmcoverlay # type: ignore
            except ImportError:
                Debug.logger.info("No overlay plugin detected")
                return

        try:
            from overlay_plugin.overlay_api import define_plugin_group # type: ignore
            self.is_modern = True
        except ImportError:
            self.is_modern = False

        try:
            self._overlay = edmcoverlay.Overlay()
            self.available = True
            self.supports_circle = self._detect_circle_support()
            Debug.logger.info(f"Overlay detected ({'modern' if self.is_modern else 'legacy'})")
        except Exception as e:
            Debug.logger.warning("Overlay plugin found but failed to initialize", exc_info=e)

    def _detect_circle_support(self) -> bool:
        """ introspect send_shape's signature for circle support """
        try:
            return "radius" in inspect.signature(self._overlay.send_shape).parameters
        except Exception:
            return False

    def send_text(self, id:str, text:str, color:str, x:int, y:int, ttl:int = 4, size:str = "normal") -> None:
        """ Send/update a text message. No-op if no overlay is available. """
        if not self.available: return
        try:
            self._overlay.send_message(id, text, color, x, y, ttl=ttl, size=size)
            self._succeed()
        except Exception as e:
            self._fail("send_text", e)

    def send_shape(self, id:str, shape:str, border_color:str, fill_color:str, x:int, y:int, w:int, h:int, ttl:int = 4) -> None:
        """ Send/update a rectangle or other filled shape. No-op if no overlay is available. """
        if not self.available: return
        try:
            self._overlay.send_shape(id, shape, border_color, fill_color, x, y, w, h, ttl=ttl)
            self._succeed()
        except Exception as e:
            self._fail("send_shape", e)

    def send_circle(self, id:str, border_color:str, fill_color:str, x:int, y:int, radius:int, thickness:int, ttl:int = 4) -> None:
        """ A native filled/outlined circle """
        if not self.available: return
        try:
            self._overlay.send_shape(
                id, "circle", color=border_color, fill=fill_color, x=x, y=y, radius=radius, thickness=thickness, ttl=ttl,
            )
            self._succeed()
        except Exception as e:
            self._fail("send_circle", e)

    def send_vect(self, id:str, vector:list[dict], color:str, ttl:int = 4, fill_color:str = "") -> None:
        """ Send/update a vector shape (e.g. a polygon or ring) """
        if not self.available: return
        try:
            self._overlay.send_raw({
                "id": id, "shape": "vect", "color": color, "fill": fill_color,
                "x": 0, "y": 0, "w": 0, "h": 0, "ttl": ttl, "vector": vector,
            })
            self._succeed()
        except Exception as e:
            self._fail("send_vect", e)

    def clear(self, id:str) -> None:
        """ Clear a previously sent message/shape by id, if the backend supports it. """
        if not self.available: return
        try:
            self._overlay.send_message(id, "", "#000000", 0, 0, ttl=1)
        except Exception as e:
            self._fail("clear", e)

    def define_group(self, **kwargs) -> bool:
        """
        Register a plugin group with EDMCModernOverlay for layout/grouping/backgrounds
        """
        if not self.is_modern:
            return False
        try:
            from overlay_plugin.overlay_api import define_plugin_group # type: ignore
            define_plugin_group(**kwargs)
            return True
        except Exception as e:
            Debug.logger.debug("EDMCModernOverlay define_plugin_group failed", exc_info=e)
            self.is_modern = False
            return False

    def _succeed(self) -> None:
        self._warned = False
        self._consecutive_failures = 0

    def _fail(self, op:str, exc:Exception) -> None:
        """ A single failure doesn't disable the overlay """
        self._consecutive_failures += 1
        if self._consecutive_failures < self.FAILURE_THRESHOLD:
            return
        if not self._warned:
            self._warned = True
            Debug.logger.warning(
                f"Overlay {op} failed {self._consecutive_failures} times in a row, disabling further overlay output this session",
                exc_info=exc,
            )
        self.available = False
