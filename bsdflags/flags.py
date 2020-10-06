"""BSD Flags"""

from dataclasses import dataclass
from functools import cached_property

__all__ = ["Flag", "FLAGS", "NAMES"]

@dataclass
class Flag:
    cflag: str
    desc: str
    val: int
    names: list
    allowed: list

    @cached_property
    def name(self) -> str:
        return self.names[0]

    @cached_property
    def aliases(self) -> str:
        aliases = self.names.copy()
        aliases.pop(0)
        return aliases

    @cached_property
    def needs_sudo(self) -> bool:
        return "owner" in self.allowed

flags = [
    Flag(cflag="SF_ARCHIVED",
         val=0x10000,
         names=["arch", "archived"],
         allowed=["root"],
         desc="File is archived"),
    Flag(cflag="UF_OPAQUE",
         val=0x8,
         names=["opaque"],
         allowed=["root", "owner"],
         desc="Directory is opaque when viewed through a union mount"),
    Flag(cflag="UF_NODUMP",
         val=0x1,
         names=["nodump"],
         allowed=["root", "owner"],
         desc="Do not back up the file when using the UNIX dump command"),
    Flag(cflag="SF_APPEND",
         val=0x40000,
         names=["sappend", "sappnd"],
         allowed=["root"],
         desc="Software can only append to the file, not modify the existing data"),
    Flag(cflag="SF_IMMUTABLE",
         val=0x20000,
         names=["schg", "schange", "simmutable"],
         allowed=["root", "single-user-mode"],
         desc="File cannot be moved, renamed, or deleted"),
    Flag(cflag="UF_APPEND",
         val=0x4,
         names=["uappnd", "uappend"],
         allowed=["root", "owner"],
         desc="Software can only append to the file, not modify the existing data"),
    Flag(cflag="UF_IMMUTABLE",
         val=0x2,
         names=["uchg", "uchange", "uimmutable"],
         allowed=["root", "owner"],
         desc="File cannot be moved, renamed, or deleted"),
    Flag(cflag="UF_HIDDEN",
         val=0x8000,
         names=["hidden"],
         allowed=["root", "owner"],
         desc="Hide item from GUI"),
]

FLAGS = {}
for flag in flags:
    FLAGS[flag.name] = flag

NAMES = []
for flag in flags:
    NAMES += flag.names
