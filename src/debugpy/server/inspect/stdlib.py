# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root
# for license information.

"""Object inspection for builtin Python types."""

from itertools import count
from typing import Iterable

from debugpy.common import log
from debugpy.server.inspect import ChildObject, ObjectInspector, inspect
from debugpy.server.safe_repr import SafeRepr


class ChildLen(ChildObject):
    name = "len()"

    def __init__(self, parent: object):
        super().__init__(len(parent))

    def expr(self, obj_expr: str) -> str:
        return f"len({obj_expr})"


class ChildItem(ChildObject):
    key: object

    def __init__(self, key: object, value: object):
        super().__init__(value)
        self.key = key

    @property
    def name(self) -> str:
        key_repr = "".join(inspect(self.key).repr())
        return f"[{key_repr}]"

    def expr(self, obj_expr: str) -> str:
        return f"({obj_expr}){self.name}"


class SequenceInspector(ObjectInspector):
    def children(self) -> Iterable[ChildObject]:
        yield from super().children()
        yield ChildLen(self.obj)
        try:
            it = iter(self.obj)
        except:
            return
        for i in count():
            try:
                item = next(it)
            except StopIteration:
                break
            except:
                log.exception("Error retrieving next item.")
                break
            yield ChildItem(i, item)


class MappingInspector(ObjectInspector):
    def children(self) -> Iterable["ChildObject"]:
        yield from super().children()
        yield ChildLen(self.obj)
        try:
            keys = self.obj.keys()
        except:
            return
        it = iter(keys)
        while True:
            try:
                key = next(it)
            except StopIteration:
                break
            except:
                break
            try:
                value = self.obj[key]
            except BaseException as exc:
                value = exc
            yield ChildItem(key, value)

            
class ListInspector(SequenceInspector):
    def repr(self) -> Iterable[str]:
        # TODO: move logic from SafeRepr here
        yield SafeRepr()(self.obj)