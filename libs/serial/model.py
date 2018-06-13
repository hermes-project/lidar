# region Backwards Compatibility
from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, \
    with_statement

from decimal import Decimal
from urllib.parse import urljoin

from future import standard_library

standard_library.install_aliases()
from builtins import *
from future.utils import native_str
# endregion


from urllib.request import Request
from urllib.response import addinfourl, addbase
from http.client import HTTPResponse

import collections
import json
from base64 import b64encode
from collections import OrderedDict, Callable, Set, Sequence
from copy import deepcopy
from io import IOBase, UnsupportedOperation
from itertools import chain

import re
import sys

from numbers import Number

import serial
from serial.utilities import qualified_name, properties_values, read

try:
    import typing
    from typing import Union, Dict, Any, AnyStr
except ImportError:
    typing = Union = Any = AnyStr = None

import yaml

if hasattr(collections, 'Generator'):
    Generator = collections.Generator
else:
    Generator = type(n for n in (1, 2, 3))


def marshal(
    data,  # type: Any
    types=None,  # type: Optional[typing.Sequence[Union[type, serial.properties.Property]]]
    value_types=None,  # type: Optional[typing.Sequence[Union[type, serial.properties.Property]]]
    item_types=None,  # type: Optional[typing.Sequence[Union[type, serial.properties.Property]]]
):
    # type: (...) -> Any
    """
    Recursively converts instances of ``serial.model.Object`` into JSON/YAML serializable objects.
    """
    if hasattr(data, '_marshal'):
        return data._marshal()
    elif data is None:
        return data
    if isinstance(types, Callable):
        types = types(data)
    if (types is not None) or (item_types is not None) or (value_types is not None):
        if types is not None:
            if (str in types) and (native_str is not str) and (native_str not in types):
                types = tuple(chain(*(
                    ((t, native_str) if (t is str) else (t,))
                    for t in types
                )))
            matched = False
            for t in types:
                if isinstance(t, serial.properties.Property):
                    try:
                        data = t.marshal(data)
                        matched = True
                        break
                    except TypeError:
                        pass
                elif isinstance(t, type) and isinstance(data, t):
                    matched = True
                    break
            if not matched:
                raise TypeError(
                    '%s cannot be interpreted as any of the designated types: %s' % (
                        repr(data),
                        repr(types)
                    )
                )
        if value_types is not None:
            for k, v in data.items():
                data[k] = serial.marshal(v, types=value_types)
        if item_types is not None:
            for i in range(len(data)):
                data[i] = serial.marshal(data[i], types=item_types)
    if isinstance(data, Decimal):
        return float(data)
    elif isinstance(data, native_str):
        return data
    elif isinstance(data, (bytes, bytearray)):
        return str(b64encode(data), 'ascii')
    elif hasattr(data, '__bytes__'):
        return str(b64encode(bytes(data)), 'ascii')
    else:
        return data


def unmarshal(
    data,  # type: Any
    types=None,  # type: Optional[typing.Sequence[Union[type, serial.properties.Property]]]
    value_types=None,  # type: Optional[typing.Sequence[Union[type, serial.properties.Property]]]
    item_types=None,  # type: Optional[typing.Sequence[Union[type, serial.properties.Property]]]
):
    # type: (...) -> typing.Any
    """
    Convert ``data`` into ``serial.model`` representations of same.
    """
    if (data is None) or (data is serial.properties.NULL):
        return data
    if isinstance(types, Callable):
        types = types(data)
    if isinstance(data, Generator):
        data = tuple(data)
    if types is None:
        if isinstance(data, (dict, OrderedDict)) and not isinstance(data, Dictionary):
            data = Dictionary(data, value_types=value_types)
        elif isinstance(data, (Set, Sequence)) and (not isinstance(data, (str, bytes, native_str, Array))):
            data = Array(data, item_types=item_types)
        return data
    elif (str in types) and (native_str is not str) and (native_str not in types):
        types = tuple(chain(*(
            ((t, native_str)  if (t is str) else (t,))
            for t in types
        )))
    matched = False
    error = None
    if isinstance(data, Model):
        metadata = serial.meta.read(data)
    else:
        metadata = None
    for t in types:
        if isinstance(
            t,
            serial.properties.Property
        ):
            try:
                data = t.unmarshal(data)
                matched = True
                break
            except (AttributeError, KeyError, TypeError, ValueError) as e:
                error = e
                continue
        elif isinstance(t, type):
            if issubclass(t, Object) and isinstance(data, (dict, OrderedDict)):
                try:
                    data = t(data)
                    matched = True
                    break
                except (AttributeError, KeyError, TypeError, ValueError) as e:
                    error = e
                    pass
            elif isinstance(data, (dict, OrderedDict, Dictionary)) and issubclass(t, (dict, OrderedDict, Dictionary)):
                if issubclass(t, Dictionary):
                    data = t(data, value_types=value_types)
                else:
                    data = Dictionary(data, value_types=value_types)
                matched = True
                break
            elif (
                isinstance(data, (Set, Sequence, Generator)) and
                (not isinstance(data, (str, bytes, native_str))) and
                issubclass(t, (Set, Sequence)) and
                (not issubclass(t, (str, bytes, native_str)))
            ):
                if issubclass(t, Array):
                    data = t(data, item_types=item_types)
                else:
                    data = Array(data, item_types=item_types)
                matched = True
                break
            elif isinstance(data, t):
                matched = True
                if isinstance(data, Decimal):
                    data = float(data)
                break
    if not matched:
        if not matched:
            if len(types) == 1 and (error is not None):
                raise error
            else:
                data_lines = []
                lines = repr(data).split('\n')
                if len(lines) == 1:
                    data_lines.append(lines[0].lstrip())
                else:
                    data_lines.append('')
                    for line in lines:
                        data_lines.append(
                            '       ' + line
                        )
                types_lines = ['(']
                for t in types:
                    if isinstance(t, type):
                        lines = (qualified_name(t),)
                    else:
                        lines = repr(t).split('\n')
                    for line in lines:
                        types_lines.append(
                            '           ' + line
                        )
                    types_lines[-1] += ','
                types_lines.append('       )')
                raise TypeError(
                    '\n   The data provided does not match any of the expected types and/or property definitions:\n' +
                    '     - data: %s\n' % '\n'.join(data_lines) +
                    '     - types: %s' % '\n'.join(types_lines)
                )
    if metadata is not None:
        new_metadata = serial.meta.read(data)
        if new_metadata is not None:
            if metadata is not new_metadata:
                writable = False
                for a, v in properties_values(metadata):
                    try:
                        if getattr(new_metadata, a) != v:
                            if not writable:
                                new_metadata = serial.meta.writable(data)
                            setattr(new_metadata, a, v)
                    except AttributeError:
                        pass
    return data


def serialize(data, format_='json'):
    # type: (Any, str, Optional[str]) -> str
    """
    Serializes instances of ``serial.model.Object`` as JSON or YAML.
    """
    h = None
    if isinstance(data, (Object, Dictionary, Array)):
        h = serial.hooks.read(data)
        if (h is not None) and (h.before_serialize is not None):
            data = h.before_serialize(data)
    if format_ not in ('json', 'yaml'):
        format_ = format_.lower()
        if format_ not in ('json', 'yaml'):
            raise ValueError(
                'Supported `serial.model.serialize()` `format_` values include "json" and "yaml" (not "%s").' %
                format_
            )
    if format_ == 'json':
        data = json.dumps(marshal(data))
    elif format_ == 'yaml':
        data = yaml.dump(marshal(data))
    if (h is not None) and (h.after_serialize is not None):
        data = h.after_serialize(data)
    return data


def deserialize(data, format_):
    # type: (Optional[Union[str, IOBase, addbase]], str) -> Any
    if format_ not in ('json', 'yaml'):  # , 'xml'
        raise NotImplementedError(
            'Deserialization of data in the format %s is not currently supported.' % repr(format_)
        )
    if not isinstance(data, (str, bytes)):
        data = read(data)
    if isinstance(data, bytes):
        data = str(data, encoding='utf-8')
    if isinstance(data, str):
        if format_ == 'json':
            data = json.loads(
                data,
                object_hook=OrderedDict,
                object_pairs_hook=OrderedDict
            )
        elif format_ == 'yaml':
            data = yaml.load(data)
    return data


def detect_format(data):
    # type: (Optional[Union[str, IOBase, addbase]]) -> Tuple[Any, str]
    if not isinstance(data, str):
        try:
            data = serial.utilities.read(data)
        except TypeError:
            return data, None
    formats = ('json', 'yaml')
    format_ = None
    for f in formats:
        try:
            data = deserialize(data, f)
            format_ = f
            break
        except ValueError:
            pass
    if format is None:
        raise ValueError(
            'The data provided could not be parsed:\n' + repr(data)
        )
    return data, format_


def validate(
    data,  # type: Union[Object, Array, Dictionary]
    types=None,  # type: Optional[Union[type, serial.properties.Property, Object]]
    raise_errors=True  # type: bool
):
    # type: (...) -> typing.Sequence[str]
    errors = []
    error = None
    if types is not None:
        if isinstance(types, collections.Callable):
            types = types(data)
        if (str in types) and (native_str is not str) and (native_str not in types):
            types = tuple(chain(*(
                ((t, native_str)  if (t is str) else (t,))
                for t in types
            )))
        valid = False
        for t in types:
            if isinstance(t, type) and isinstance(data, t):
                valid = True
                break
            elif isinstance(t, serial.properties.Property):
                if t.types is None:
                    valid = True
                    break
                try:
                    validate(data, t.types, raise_errors=True)
                    valid = True
                    break
                except serial.errors.ValidationError:
                    pass
        if not valid:
            error = (
                '\n`data` is invalid:\n%s\n`data` must be one of the following types:\n%s.' % (
                    '\n'.join('   ' + l for l in repr(data).split('\n')),
                    '\n'.join(
                        repr(Array(types)).split('\n')[1:-1]
                    )
                )
            )
    if error is not None:
        if (not errors) or (error not in errors):
            errors.append(error)
    if ('_validate' in dir(data)) and isinstance(data._validate, collections.Callable):
        errors.extend(
            error for error in
            data._validate(raise_errors=False)
            if error not in errors
        )
    if raise_errors and errors:
        raise serial.errors.ValidationError('\n' + '\n'.join(errors))
    return errors


def version(data, specification, version_number):
    # type: (Any, str, Union[str, int, typing.Sequence[int]]) -> Any
    """
    Recursively alters instances of ``serial.model.Object`` according to version_number metadata associated with that
    object's serial.properties.

    Arguments:

        - data

        - specification (str): The specification to which the ``version_number`` argument applies.

        - version_number (str|int|[int]): A version number represented as text (in the form of integers separated by
          periods), an integer, or a sequence of integers.
    """
    def version_match(p):
        if p.versions is not None:
            vm = False
            sm = False
            for v in p.versions:
                if v.specification == specification:
                    sm = True
                    if v == version_number:
                        vm = True
                        break
            if sm and (not vm):
                return False
        return True

    def version_properties(ps):
        # type: (typing.Sequence[serial.properties.Property]) -> Optional[typing.Sequence[serial.meta.Meta]]
        changed = False
        nps = []
        for p in ps:
            if isinstance(p, serial.properties.Property):
                if version_match(p):
                    np = version_property(p)
                    if np is not p:
                        changed = True
                    nps.append(np)
                else:
                    changed = True
            else:
                nps.append(p)
        if changed:
            return tuple(nps)
        else:
            return None

    def version_property(p):
        # type: (serial.properties.Property) -> serial.meta.Meta
        changed = False
        if isinstance(p, serial.properties.Array) and (p.item_types is not None):
            item_types = version_properties(p.item_types)
            if item_types is not None:
                if not changed:
                    p = deepcopy(p)
                p.item_types = item_types
                changed = True
        elif isinstance(p, serial.properties.Dictionary) and (p.value_types is not None):
            value_types = version_properties(p.value_types)
            if value_types is not None:
                if not changed:
                    p = deepcopy(p)
                p.value_types = value_types
                changed = True
        if p.types is not None:
            types = version_properties(p.types)
            if types is not None:
                if not changed:
                    p = deepcopy(p)
                p.types = types
        return p

    if isinstance(data, Model):
        im = serial.meta.read(data)
        cm = serial.meta.read(type(data))
        if isinstance(data, Object):
            for n in tuple(im.properties.keys()):
                p = im.properties[n]
                if version_match(p):
                    np = version_property(p)
                    if np is not p:
                        if im is cm:
                            im = serial.meta.writable(data)
                        im.properties[n] = np
                else:
                    if im is cm:
                        im = serial.meta.writable(data)
                    del im.properties[n]
                    v = getattr(data, n)
                    if v is not None:
                        raise serial.errors.VersionError(
                            '%s - the property `%s` is not applicable in %s version %s:\n%s' % (
                                qualified_name(type(data)),
                                n,
                                specification,
                                version_number,
                                str(data)
                            )
                        )
                version(getattr(data, n), specification, version_number)
        elif isinstance(data, Dictionary):
            if im.value_types:
                new_value_types = version_properties(im.value_types)
                if new_value_types:
                    if im is cm:
                        im = serial.meta.writable(data)
                    im.value_types = new_value_types
            for v in data.values():
                version(v, specification, version_number)
        elif isinstance(data, Array):
            if im.item_types:
                new_item_types = version_properties(im.item_types)
                if new_item_types:
                    if im is cm:
                        im = serial.meta.writable(data)
                    im.item_types = new_item_types
            for v in data:
                version(v, specification, version_number)
    elif isinstance(data, (collections.Set, collections.Sequence)) and not isinstance(data, (str, bytes)):
        # for d in data:
        #     version(d, specification, version_number)
        raise ValueError()
    elif isinstance(data, (dict, OrderedDict)):
        # for k, v in data.items():
        #     version(v, specification, version_number)
        raise ValueError()


class Model(object):

    _format = None  # type: Optional[str]
    _meta = None  # type: Optional[serial.meta.Object]
    _hooks = None  # type: Optional[serial.hooks.Object]

    def __init__(self):
        self._format = None  # type: Optional[str]
        self._meta = None  # type: Optional[serial.meta.Meta]
        self._hooks = None  # type: Optional[serial.hooks.Hooks]
        self._url = None  # type: Optional[str]
        self._xpath = None  # type: Optional[str]
        self._pointer = None  # type: Optional[str]

    def __hash__(self):
        return id(self)


class Object(Model):

    _format = None  # type: Optional[str]
    _meta = None  # type: Optional[serial.meta.Object]
    _hooks = None  # type: Optional[serial.hooks.Object]

    def __init__(
        self,
        _=None,  # type: Optional[Union[str, bytes, dict, typing.Sequence, IO]]
    ):
        self._meta = None  # type: Optional[serial.meta.Object]
        self._hooks = None  # type: Optional[serial.hooks.Object]
        self._url = None  # type: Optional[str]
        self._xpath = None  # type: Optional[str]
        self._pointer = None  # type: Optional[str]
        if _ is not None:
            if isinstance(_, Object):
                m = serial.meta.read(_)
                if serial.meta.read(self) is not m:
                    serial.meta.write(self, deepcopy(m))
                h = serial.hooks.read(_)
                if serial.hooks.read(self) is not h:
                    serial.hooks.write(self, deepcopy(h))
                for k in m.properties.keys():
                    try:
                        setattr(self, k, getattr(_, k))
                    except TypeError as e:
                        label = '\n - %s.%s: ' % (qualified_name(type(self)), k)
                        if e.args:
                            e.args = tuple(
                                chain(
                                    (label + e.args[0],),
                                    e.args[1:]
                                )
                            )
                        else:
                            e.args = (label + serialize(_),)
                        raise e
            else:
                if isinstance(_, IOBase):
                    if hasattr(_, 'url'):
                        serial.meta.url(self, _.url)
                    elif hasattr(_, 'name'):
                        serial.meta.url(self, urljoin('file:', _.name))
                _, f = detect_format(_)
                if isinstance(_, dict):
                    for k, v in _.items():
                        if v is None:
                            v = serial.properties.NULL
                        try:
                            self[k] = v
                        except KeyError as e:
                            if e.args and len(e.args) == 1:
                                e.args = (
                                    r'%s.%s: %s' % (qualified_name(type(self)), e.args[0], json.dumps(_)),
                                )
                            raise e
                else:
                    _dir = tuple(p for p in dir(_) if p[0] != '_')
                    for p in serial.meta.writable(self.__class__).properties.keys():
                        if p in _dir:
                            setattr(self, getattr(_, p))
                if f is not None:
                    serial.meta.format_(self, f)

    def __setattr__(self, property_name, value):
        # type: (Object, str, Any) -> properties_.NoneType
        if property_name[0] != '_':
            try:
                property_definition = serial.meta.read(self).properties[property_name]
                try:
                    value = property_definition.unmarshal(value)
                    if isinstance(value, Generator):
                        value = tuple(value)
                except (TypeError, ValueError) as e:
                    message = '\n - %s.%s: ' % (
                        qualified_name(type(self)),
                        property_name
                    )
                    if e.args and isinstance(e.args[0], str):
                        e.args = tuple(
                            chain(
                                (message + e.args[0],),
                                e.args[1:]
                            )
                        )
                    else:
                        e.args = (message + repr(value),)
                    raise e
            except KeyError as e:
                if value is not None:
                    raise e
        super().__setattr__(property_name, value)

    def __setitem__(self, key, value):
        # type: (str, str) -> None
        m = serial.meta.read(self)
        if key in m.properties:
            property_name = key
        else:
            property_name = None
            for pn, pd in m.properties.items():
                if key == pd.name:
                    property_name = pn
                    break
            if property_name is None:
                raise KeyError(
                    '`%s` has no property mapped to the name "%s"' % (
                        qualified_name(type(self)),
                        key
                    )
                )
        setattr(self, property_name, value)

    def __delattr__(self, key):
        # type: (str) -> None
        # type: (str, str) -> None
        m = serial.meta.read(self)
        if key in m.properties:
            setattr(self, key, None)
        else:
            super().__delattr__(key)


    def __getitem__(self, key):
        # type: (str, str) -> None
        m = serial.meta.read(self)
        if key in m.properties:
            property_name = key
        else:
            property_definition = None
            property_name = None
            for pn, pd in m.properties.items():
                if key == pd.name:
                    property_name = pn
                    property_definition = pd
                    break
            if property_definition is None:
                raise KeyError(
                    '`%s` has no property mapped to the name "%s"' % (
                        qualified_name(type(self)),
                        key
                    )
                )
        return getattr(self, property_name)

    def __copy__(self):
        # type: () -> Object
        return self.__class__(self)

    def __deepcopy__(self, memo=None):
        # type: (Optional[dict]) -> Object
        new_instance = self.__class__()
        im = serial.meta.read(self)
        cm = serial.meta.read(type(self))
        if im is cm:
            m = cm  # type: serial.meta.Object
        else:
            serial.meta.write(new_instance, deepcopy(im, memo=memo))
            m = im  # type: serial.meta.Object
        ih = serial.hooks.read(self)
        ch = serial.hooks.read(type(self))
        if ih is not ch:
            serial.hooks.write(new_instance, deepcopy(ih, memo=memo))
        if m is not None:
            for k in m.properties.keys():
                try:
                    v = getattr(self, k)
                    if v is not None:
                        if not isinstance(v, Callable):
                            v = deepcopy(v, memo=memo)
                            setattr(new_instance, k, v)
                except TypeError as e:
                    label = '%s.%s: ' % (qualified_name(type(self)), k)
                    if e.args:
                        e.args = tuple(
                            chain(
                                (label + e.args[0],),
                                e.args[1:]
                            )
                        )
                    else:
                        e.args = (label + serialize(self),)
                    raise e
        return new_instance

    def _marshal(self):
        o = self
        h = serial.hooks.read(o)
        if (h is not None) and (h.before_marshal is not None):
            o = h.before_marshal(o)
        data = OrderedDict()
        m = serial.meta.read(o)
        for pn, p in m.properties.items():
            v = getattr(o, pn)
            if v is not None:
                k = p.name or pn
                data[k] = p.marshal(v)
        if (h is not None) and (h.after_marshal is not None):
            data = h.after_marshal(data)
        return data

    def __str__(self):
        return serialize(self)

    def __repr__(self):
        representation = [
            '%s(' % qualified_name(type(self))
        ]
        m = serial.meta.read(self)
        for p in m.properties.keys():
            v = getattr(self, p)
            if v is not None:
                rv = (
                    qualified_name(v)
                    if isinstance(v, type) else
                    repr(v)
                )
                rvls = rv.split('\n')
                if len(rvls) > 2:
                    rvs = [rvls[0]]
                    for rvl in rvls[1:]:
                        rvs.append('    ' + rvl)
                    rv = '\n'.join(rvs)
                representation.append(
                    '    %s=%s,' % (p, rv)
                )
        representation.append(')')
        if len(representation) > 2:
            return '\n'.join(representation)
        else:
            return ''.join(representation)

    def __eq__(self, other):
        # type: (Any) -> bool
        if type(self) is not type(other):
            return False
        m = serial.meta.read(self)
        om = serial.meta.read(other)
        self_properties = set(m.properties.keys())
        other_properties = set(om.properties.keys())
        for p in self_properties|other_properties:
            v = getattr(self, p)
            ov = getattr(other, p)
            if v != ov:
                return False
        return True

    def __ne__(self, other):
        # type: (Any) -> bool
        return False if self == other else True

    def __iter__(self):
        m = serial.meta.read(self)
        for k, p in m.properties.items():
            yield p.name or k

    def _validate(self, raise_errors=True):
        # type: (Callable, bool, Optional[list]) -> None
        errors = []
        o = self
        h = serial.hooks.read(self)
        if (h is not None) and (h.before_validate is not None):
            o = h.before_validate(o)
        m = serial.meta.read(o)
        for pn, p in m.properties.items():
            v = getattr(o, pn)
            if v is None:
                if isinstance(p.required, Callable):
                    required = p.required(o)
                else:
                    required = p.required
                if required:
                    errors.append('The property `%s` is required for `%s`:\n%s' % (pn, qualified_name(type(o)), str(o)))
            else:
                if v is serial.properties.NULL:
                    types = p.types
                    if isinstance(types, collections.Callable):
                        types = types(v)
                    if types is not None:
                        if (str in types) and (native_str is not str) and (native_str not in types):
                            types = tuple(chain(*(
                                ((t, native_str) if (t is str) else (t,))
                                for t in types
                            )))
                        if serial.properties.Null not in types:
                            errors.append(
                                'Null values are not allowed in `%s.%s`, ' % (qualified_name(type(o)), pn) +
                                'permitted types include: %s.' % ', '.join(
                                    '`%s`' % qualified_name(t) for t in types
                                )
                            )
                else:
                    try:
                        errors.extend(validate(v, p.types, raise_errors=False))
                    except serial.errors.ValidationError as e:
                        message = '%s.%s:\n' % (qualified_name(type(o)), pn)
                        if e.args:
                            e.args = tuple(chain(
                                (e.args[0] + message,),
                                e.args[1:]
                            ))
                        else:
                            e.args = (
                                message,
                            )
        if (h is not None) and (h.after_validate is not None):
            o = h.after_validate(o)
        if raise_errors and errors:
            raise serial.errors.ValidationError('\n'.join(errors))
        return errors


class Array(list, Model):

    _format = None  # type: Optional[str]
    _hooks = None  # type: Optional[serial.hooks.Array]
    _meta = None  # type: Optional[serial.meta.Array]

    def __init__(
        self,
        items=None,  # type: Optional[Union[Sequence, Set]]
        item_types=(
            None
        ),  # type: Optional[Union[Sequence[Union[type, serial.properties.Property]], type, serial.properties.Property]]
    ):
        self._meta = None  # type: Optional[serial.meta.Array]
        self._hooks = None  # type: Optional[serial.hooks.Array]
        self._url = None  # type: Optional[str]
        self._xpath = None  # type: Optional[str]
        self._pointer = None  # type: Optional[str]
        if isinstance(items, IOBase):
            if hasattr(items, 'url'):
                serial.meta.url(self, items.url)
            elif hasattr(items, 'name'):
                serial.meta.url(self, urljoin('file:', items.name))
        items, f = detect_format(items)
        if item_types is None:
            if isinstance(items, Array):
                m = serial.meta.read(items)
                if serial.meta.read(self) is not m:
                    serial.meta.write(self, deepcopy(m))
        else:
            serial.meta.writable(self).item_types = item_types
        if items is not None:
            for item in items:
                self.append(item)
        if f is not None:
            serial.meta.format_(self, f)

    def __setitem__(
        self,
        index,  # type: int
        value,  # type: Any
    ):
        m = serial.meta.read(self)
        if m is None:
            item_types = None
        else:
            item_types = m.item_types
        super().__setitem__(index, unmarshal(value, types=item_types))

    def append(self, value):
        # type: (Any) -> None
        m = serial.meta.read(self)
        if m is None:
            item_types = None
        else:
            item_types = m.item_types
        super().append(unmarshal(value, types=item_types))

    def __copy__(self):
        # type: () -> Array
        return self.__class__(self)

    def __deepcopy__(self, memo=None):
        # type: (Optional[dict]) -> Array
        new_instance = self.__class__()
        im = serial.meta.read(self)
        cm = serial.meta.read(type(self))
        if im is not cm:
            serial.meta.write(new_instance, deepcopy(im, memo=memo))
        ih = serial.hooks.read(self)
        ch = serial.hooks.read(type(self))
        if ih is not ch:
            serial.hooks.write(new_instance, deepcopy(ih, memo=memo))
        for i in self:
            new_instance.append(deepcopy(i, memo=memo))
        return new_instance

    def _marshal(self):
        a = self
        h = serial.hooks.read(a)
        if (h is not None) and (h.before_marshal is not None):
            a = h.before_marshal(a)
        m = serial.meta.read(a)
        a = tuple(
            marshal(
                i,
                types=m.item_types
            ) for i in a
        )
        if (h is not None) and (h.after_marshal is not None):
            a = h.after_marshal(a)
        return a

    def _validate(
        self,
        raise_errors=True
    ):
        # type: (bool) -> None
        errors = []
        a = self
        h = serial.hooks.read(a)
        if (h is not None) and (h.before_validate is not None):
            a = h.before_validate(a)
        m = serial.meta.read(a)
        if m.item_types is not None:
            for i in a:
                errors.extend(validate(i, m.item_types, raise_errors=False))
        if (h is not None) and (h.after_validate is not None):
            h.after_validate(a)
        if raise_errors and errors:
            raise serial.errors.ValidationError('\n'.join(errors))
        return errors

    def __repr__(self):
        representation = [
            qualified_name(type(self)) + '('
        ]
        if len(self) > 0:
            representation.append('    [')
            for i in self:
                ri = (
                    qualified_name(i) if isinstance(i, type) else
                    repr(i)
                )
                rils = ri.split('\n')
                if len(rils) > 1:
                    ris = [rils[0]]
                    ris += [
                        '        ' + rvl
                        for rvl in rils[1:]
                    ]
                    ri = '\n'.join(ris)
                representation.append(
                    '        %s,' % ri
                )
            im = serial.meta.read(self)
            cm = serial.meta.read(type(self))
            m = None if (im is cm) else im
            representation.append(
                '    ]' + (''
                if m is None or m.item_types is None
                else ',')
            )
        im = serial.meta.read(self)
        cm = serial.meta.read(type(self))
        if im is not cm:
            if im.item_types:
                representation.append(
                    '    item_types=(',
                )
                for it in im.item_types:
                    ri = (
                        qualified_name(it) if isinstance(it, type) else
                        repr(it)
                    )
                    rils = ri.split('\n')
                    if len(rils) > 2:
                        ris = [rils[0]]
                        ris += [
                            '        ' + rvl
                            for rvl in rils[1:-1]
                        ]
                        ris.append('        ' + rils[-1])
                        ri = '\n'.join(ris)
                    representation.append('        %s,' % ri)
                m = serial.meta.read(self)
                if len(m.item_types) > 1:
                    representation[-1] = representation[-1][:-1]
                representation.append('    )')
        representation.append(')')
        if len(representation) > 2:
            return '\n'.join(representation)
        else:
            return ''.join(representation)

    def __eq__(self, other):
        # type: (Any) -> bool
        if type(self) is not type(other):
            return False
        length = len(self)
        if length != len(other):
            return False
        for i in range(length):
            if self[i] != other[i]:
                return False
        return True

    def __ne__(self, other):
        # type: (Any) -> bool
        if self == other:
            return False
        else:
            return True

    def __str__(self):
        return serialize(self)


class Dictionary(OrderedDict, Model):

    _format = None  # type: Optional[str]
    _hooks = None  # type: Optional[serial.hooks.Dictionary]
    _meta = None  # type: Optional[serial.meta.Dictionary]

    def __init__(
        self,
        items=None,  # type: Optional[typing.Mapping]
        value_types=(
            None
        ),  # type: Optional[Union[Sequence[Union[type, serial.properties.Property]], type, serial.properties.Property]]
    ):
        self._meta = None  # type: Optional[serial.meta.Dictionary]
        self._hooks = None  # type: Optional[serial.hooks.Dictionary]
        self._url = None  # type: Optional[str]
        self._xpath = None  # type: Optional[str]
        self._pointer = None  # type: Optional[str]
        if isinstance(items, IOBase):
            if hasattr(items, 'url'):
                serial.meta.url(self, items.url)
            elif hasattr(items, 'name'):
                serial.meta.url(self, urljoin('file:', items.name))
        items, f = detect_format(items)
        if value_types is None:
            if isinstance(items, Dictionary):
                m = serial.meta.read(items)
                if serial.meta.read(self) is not m:
                    serial.meta.write(self, deepcopy(m))
        else:
            serial.meta.writable(self).value_types = value_types
        super().__init__()
        if items is None:
            super().__init__()
        else:
            if isinstance(items, (OrderedDict, Dictionary)):
                items = items.items()
            elif isinstance(items, dict):
                items = sorted(items.items(), key=lambda kv: kv)
            super().__init__(items)
        if f is not None:
            serial.meta.format_(self, f)

    def __setitem__(
        self,
        key,  # type: int
        value,  # type: Any
    ):
        m = serial.meta.read(self)
        if m is None:
            value_types = None
        else:
            value_types = m.value_types
        xpath = serial.meta.xpath(self)
        pointer = serial.meta.pointer(self)
        url = serial.meta.url(self)
        if pointer is not None:
            pointer = '%s/%s' % (pointer, key.replace('~', '~0').replace('/', '~1'))
        if xpath is not None:
            xpath = '%s/%s' % (xpath, key)
        try:
            super().__setitem__(
                key,
                unmarshal(
                    value,
                    types=value_types
                )
            )
        except TypeError as e:
            message = "\n - %s['%s']: " % (
                qualified_name(type(self)),
                key
            )
            if e.args and isinstance(e.args[0], str):
                e.args = tuple(
                    chain(
                        (message + e.args[0],),
                        e.args[1:]
                    )
                )
            else:
                e.args = (message + repr(value),)
            raise e

    def __copy__(self):
        # type: (Dictionary) -> Dictionary
        new_instance = self.__class__()
        im = serial.meta.read(self)
        cm = serial.meta.read(type(self))
        if im is not cm:
            serial.meta.write(new_instance, im)
        ih = serial.hooks.read(self)
        ch = serial.hooks.read(type(self))
        if ih is not ch:
            serial.hooks.write(new_instance, ih)
        for k, v in self.items():
            new_instance[k] = v
        return new_instance

    def __deepcopy__(self, memo=None):
        # type: (dict) -> Dictionary
        new_instance = self.__class__()
        im = serial.meta.read(self)
        cm = serial.meta.read(type(self))
        if im is not cm:
            serial.meta.write(new_instance, deepcopy(im, memo=memo))
        ih = serial.hooks.read(self)
        ch = serial.hooks.read(type(self))
        if ih is not ch:
            serial.hooks.write(new_instance, deepcopy(ih, memo=memo))
        for k, v in self.items():
            new_instance[k] = deepcopy(v, memo=memo)
        return new_instance

    def _marshal(self):
        d = self
        h = serial.hooks.read(d)
        if (h is not None) and (h.before_marshal is not None):
            d = h.before_marshal(d)
        m = serial.meta.read(d)
        if m is None:
            value_types = None
        else:
            value_types = m.value_types
        d = OrderedDict(
            [
                (
                    k,
                    marshal(v, types=value_types)
                ) for k, v in d.items()
            ]
        )
        if (h is not None) and (h.after_marshal is not None):
            d = h.after_marshal(d)
        return d

    def _validate(self, raise_errors=True):
        # type: (Callable) -> None
        errors = []
        d = self
        h = d._hooks or type(d)._hooks
        if (h is not None) and (h.before_validate is not None):
            d = h.before_validate(d)
        m = serial.meta.read(d)
        if m is None:
            value_types = None
        else:
            value_types = m.value_types
        if value_types is not None:
            for k, v in d.items():
                errors.extend(validate(v, value_types, raise_errors=False))
        if (h is not None) and (h.after_validate is not None):
            h.after_validate(d)
        if raise_errors and errors:
            raise serial.errors.ValidationError('\n'.join(errors))
        return errors

    def __repr__(self):
        representation = [
            qualified_name(type(self)) + '('
        ]
        items = tuple(self.items())
        if len(items) > 0:
            representation.append('    [')
            for k, v in items:
                rv = (
                    qualified_name(v) if isinstance(v, type) else
                    repr(v)
                )
                rvls = rv.split('\n')
                if len(rvls) > 1:
                    rvs = [rvls[0]]
                    for rvl in rvls[1:]:
                        rvs.append('            ' + rvl)
                    # rvs.append('            ' + rvs[-1])
                    rv = '\n'.join(rvs)
                    representation += [
                        '        (',
                        '            %s,' % repr(k),
                        '            %s' % rv,
                        '        ),'
                    ]
                else:
                    representation.append(
                        '        (%s, %s),' % (repr(k), rv)
                    )
            representation[-1] = representation[-1][:-1]
            representation.append(
                '    ]'
                if self._meta is None or self._meta.value_types is None else
                '    ],'
            )
        cm = serial.meta.read(type(self))
        im = serial.meta.read(self)
        if cm is not im:
            if self._meta.value_types:
                representation.append(
                    '    value_types=(',
                )
                for vt in im.value_types:
                    rv = (
                        qualified_name(vt) if isinstance(vt, type) else
                        repr(vt)
                    )
                    rvls = rv.split('\n')
                    if len(rvls) > 1:
                        rvs = [rvls[0]]
                        rvs += [
                            '        ' + rvl
                            for rvl in rvls[1:]
                        ]
                        rv = '\n'.join(rvs)
                    representation.append('        %s,' % rv)
                if len(self._meta.value_types) > 1:
                    representation[-1] = representation[-1][:-1]
                representation.append('    )')
        representation.append(')')
        if len(representation) > 2:
            return '\n'.join(representation)
        else:
            return ''.join(representation)

    def __eq__(self, other):
        # type: (Any) -> bool
        if type(self) is not type(other):
            return False
        keys = tuple(self.keys())
        other_keys = tuple(other.keys())
        if keys != other_keys:
            return False
        for k in keys:
            if self[k] != other[k]:
                return False
        return True

    def __ne__(self, other):
        # type: (Any) -> bool
        if self == other:
            return False
        else:
            return True

    def __str__(self):
        return serialize(self)


def from_meta(name, metadata, module=None, docstring=None):
    # type: (serial.meta.Meta, str, Optional[str]) -> type
    """
    Constructs an `Object`, `Array`, or `Dictionary` sub-class from an instance of `serial.meta.Meta`.

    Arguments:

        - name (str): The name of the class.

        - class_meta (serial.meta.Meta)

        - module (str): Specify the value for the class definition's `__module__` property. The invoking module will be
          used if this is not specified (if possible).

        - docstring (str): A docstring to associate with the class definition.
    """

    def typing_from_property(p):
        # type: (serial.properties.Property) -> str
        if isinstance(p, type):
            type_hint = p.__name__
        elif isinstance(p, serial.properties.DateTime):
            type_hint = 'datetime'
        elif isinstance(p, serial.properties.Date):
            type_hint = 'date'
        elif isinstance(p, serial.properties.Bytes):
            type_hint = 'bytes'
        elif isinstance(p, serial.properties.Integer):
            type_hint = 'int'
        elif isinstance(p, serial.properties.Number):
            type_hint = Number.__name__
        elif isinstance(p, serial.properties.Boolean):
            type_hint = 'bool'
        elif isinstance(p, serial.properties.String):
            type_hint = 'str'
        elif isinstance(p, serial.properties.Array):
            item_types = None
            if p.item_types:
                if len(p.item_types) > 1:
                    item_types = 'Union[%s]' % (
                        ', '.join(
                           typing_from_property(it)
                           for it in p.item_types
                        )
                    )
                else:
                    item_types = typing_from_property(p.item_types[0])
            type_hint = 'typing.Sequence' + (
                '[%s]' % item_types
                if item_types else
                ''
            )
        elif isinstance(p, serial.properties.Dictionary):
            value_types = None
            if p.value_types:
                if len(p.value_types) > 1:
                    value_types = 'Union[%s]' % (
                        ', '.join(
                           typing_from_property(vt)
                           for vt in p.value_types
                        )
                    )
                else:
                    value_types = typing_from_property(p.value_types[0])
            type_hint = (
                'Dict[str, %s]' % value_types
                if value_types else
                'dict'
            )
        elif p.types:
            if len(p.types) > 1:
                type_hint = 'Union[%s]' % ', '.join(
                    typing_from_property(t) for t in p.types
                )
            else:
                type_hint = typing_from_property(p.types[0])
        else:
            type_hint = 'Any'
        return type_hint
    if docstring is not None:
        if '\t' in docstring:
            docstring = docstring.replace('\t', '    ')
        lines = docstring.split('\n')
        indentation_length = float('inf')
        for line in lines:
            match = re.match(r'^[ ]+', line)
            if match:
                indentation_length = min(
                    indentation_length,
                    len(match.group())
                )
            else:
                indentation_length = 0
                break
        wrapped_lines = []
        for line in lines:
            line = '    ' + line[indentation_length:]
            if len(line) > 120:
                indent = re.match(r'^[ ]*', line).group()
                li = len(indent)
                words = re.split(r'([\w]*[\w,/"\',.;\-?`])', line[li:])
                wrapped_line = ''
                for word in words:
                    if (len(wrapped_line) + len(word) + li) <= 120:
                        wrapped_line += word
                    else:
                        wrapped_lines.append(indent + wrapped_line)
                        wrapped_line = '' if not word.strip() else word
                if wrapped_line:
                    wrapped_lines.append(indent + wrapped_line)
            else:
                wrapped_lines.append(line)
        docstring = '\n'.join(
            ['    """'] +
            wrapped_lines +
            ['    """']
        )
    if isinstance(metadata, serial.meta.Dictionary):
        out = [
            'class %s(serial.model.Dictionary):' % name
        ]
        if docstring is not None:
            out.append(docstring)
        out.append('\n    pass')
    elif isinstance(metadata, serial.meta.Array):
        out = [
            'class %s(serial.model.Array):' % name
        ]
        if docstring is not None:
            out.append(docstring)
        out.append('\n    pass')
    elif isinstance(metadata, serial.meta.Object):
        out = [
            'class %s(serial.model.Object):' % name
        ]
        if docstring is not None:
            out.append(docstring)
        out += [
            '',
            '    def __init__(',
            '        self,',
            '        _=None,  # type: Optional[Union[str, bytes, dict, typing.Sequence, IO]]'
        ]
        for n, p in metadata.properties.items():
            out.append(
                '        %s=None,  # type: Optional[%s]' % (n, typing_from_property(p))
            )
        out.append(
            '    ):'
        )
        for n in metadata.properties.keys():
            out.append(
                '        self.%s = %s' % (n, n)
            )
        out.append('        super().__init__(_)\n\n')
    else:
        raise ValueError(metadata)
    class_definition = '\n'.join(out)
    namespace = dict(__name__='from_meta_%s' % name)
    imports = '\n'.join([
        'from __future__ import nested_scopes, generators, division, absolute_import, with_statement, \\',
        'print_function, unicode_literals',
        'from future import standard_library',
        'standard_library.install_aliases()',
        'from builtins import *',
        'try:',
        '    import typing',
        '    from typing import Union, Dict, Any',
        'except ImportError:',
        '    typing = Union = Any = None',
        'import serial\n'
    ])
    exec('%s\n\n%s' % (imports, class_definition), namespace)
    result = namespace[name]
    result._source = class_definition
    if module is None:
        try:
            module = sys._getframe(1).f_globals.get('__name__', '__main__')
        except (AttributeError, ValueError):
            pass
    if module is not None:
        result.__module__ = module
    result._meta = metadata
    return result