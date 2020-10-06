"""File class"""

from py.path import local
from functools import cached_property
from dataclasses import dataclass
from subprocess import run
from os import environ

from .flags import FLAGS

@dataclass
class File:
    """File class"""

    filename: str

    @cached_property
    def flags(self):
        """Get system flags"""
        res = run(["/bin/ls", "-ldO", self.filename], capture_output=True)

        if res.returncode != 0:
            raise Exception(f"Failed with: {res.returncode} {res.stderr.decode()}")

        props = res.stdout.decode().split()
        flags = props[4].split()
        if flags[0] == "-":
            flags.remove('-')
        return flags

    def exists(self):
        """Return True if the file exists"""
        return local(self.filename).exists()

    def has_flag(self, flag) -> bool:
        """Return True if file has flag"""
        return flag.name in self.flags

    @cached_property
    def pretty(self) -> bool:
        """Return a pretty filename"""
        path = self.filename.replace(environ.get("PWD"), ".")
        path = path.replace(environ.get("HOME"), "~")
        return path
