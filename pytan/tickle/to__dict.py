import json
import logging

from pytan import PytanError
from pytan.tanium_ng import BaseType
from pytan.excelwriter import ExcelWriter
from pytan.tickle.tools import jsonify
from pytan.tickle.constants import (
    TAG_NAME, LIST_NAME, EXPLODE_NAME, FLAT_WARN, FLAT_SEP, INCLUDE_EMPTY, SKIPS, FIRSTS, LASTS
)

MYLOG = logging.getLogger(__name__)


class DictSerializeError(PytanError):
    pass


class ToDict(object):
    """Convert either a single or list of tanium_ng BaseType objects into a python
    dict object

    x = ToDict(obj)
     ..or..
    x = ToDict([obj])

    Get RESULT:
    x.RESULT
    """

    FLAT = False
    """
    bool that controls if all nested objects of OBJ will be flattened out when creating RESULT
    """

    OBJ = None
    """tanium_ng object to convert to RESULT"""

    RESULT = {}
    """dict created from OBJ"""

    _PROP_PRE = ''
    """str that holds FLAT_PRE + _FLAT_SEP IF FLAT=True"""

    _PARENT = True
    """bool to indicate if this is the first spawn of this object"""

    _FLAT_PRE = ''
    """str to prefix property names if FLAT=True"""

    def __init__(self, obj, **kwargs):
        self.KWARGS = kwargs
        self.OBJ = obj

        self.INCLUDE_EMPTY = kwargs.get('include_empty', INCLUDE_EMPTY)
        self.FLAT = kwargs.get('flat', False)
        self.FLAT_PRE = kwargs.get('flat_pre', '')
        self.FLAT_SEP = kwargs.get('flat_sep', FLAT_SEP)
        self.PARENT = kwargs.get('parent', True)

        if self.FLAT and self.FLAT_PRE and not self.PARENT:
            self._PROP_PRE = '{}{}'.format(self.FLAT_PRE, self.FLAT_SEP)
        else:
            self._PROP_PRE = ''

        self.RESULT = {}

        if isinstance(self.OBJ, list):
            self.do_list()
        elif isinstance(self.OBJ, BaseType):
            if self.OBJ._IS_LIST and self.FLAT and self.PARENT:
                self.do_list()
            else:
                self.do_obj()
        else:
            err = "obj is type {!r}, must be a tanium_ng.BaseType object or a list"
            err = err.format(type(obj).__name__)
            raise DictSerializeError(err)

    def do_obj(self):
        if self.FLAT:
            self.RESULT.update(FLAT_WARN)
        self.RESULT[TAG_NAME] = self.OBJ._SOAP_TAG
        self.base_simple()
        self.base_complex()
        self.base_list()
        self.RESULT[TAG_NAME] = self.OBJ._SOAP_TAG

        m = "Converted tanium_ng object {!r} into dict with keys:: {}"
        m = m.format(type(self.OBJ), ', '.join(self.RESULT.keys()))
        MYLOG.debug(m)

    def do_list(self):
        if self.FLAT:
            self.RESULT.update(FLAT_WARN)

        try:
            self.RESULT[TAG_NAME] = self.OBJ._SOAP_TAG
        except:
            pass

        self.RESULT[LIST_NAME] = []
        for val in self.OBJ:
            child_args = self.get_child_args()
            child_val = to_dict(val, **child_args)
            self.RESULT[LIST_NAME].append(child_val)

        m = "Converted list of {} Tanium NG objects into a dict with keys:: {}"
        m = m.format(len(self.OBJ), ', '.join(self.RESULT.keys()))
        MYLOG.debug(m)

    def base_simple(self):
        """Process the simple properties from the tanium_ng object"""
        for prop in self.OBJ._SIMPLE_PROPS:
            val = getattr(self.OBJ, prop)
            if val is None and not self.INCLUDE_EMPTY:
                continue

            prop_name = '{}{}'.format(self._PROP_PRE, prop)

            val_json = explode_json(val)
            if val_json:
                if self.FLAT:
                    val = flatten_pyobj(val_json, prefix=prop_name, sep=self.FLAT_SEP)
                    self.RESULT.update(val)
                else:
                    self.RESULT[EXPLODE_NAME] = val_json
            else:
                self.RESULT[prop_name] = val

    def base_complex(self):
        """Process the complex properties from the tanium_ng object"""
        for prop in self.OBJ._COMPLEX_PROPS:
            val = getattr(self.OBJ, prop)
            if val is None and not self.INCLUDE_EMPTY:
                continue

            prop_name = '{}{}'.format(self._PROP_PRE, prop)

            if val is not None:
                child_args = self.get_child_args(flat_pre=prop_name)
                child_val = to_dict(val, **child_args)
                if self.FLAT:
                    self.RESULT.update(child_val)
                else:
                    self.RESULT[prop_name] = child_val
            else:
                self.RESULT[prop_name] = val

    def base_list(self):
        """Process the list properties from the tanium_ng object"""
        for prop, prop_type in self.OBJ._LIST_PROPS.items():
            vals = getattr(self.OBJ, prop)
            if not vals and not self.INCLUDE_EMPTY:
                continue

            new_vals = []
            for idx, val in enumerate(vals):
                prop_name = '{}{}{}{}'.format(self._PROP_PRE, prop, self.FLAT_SEP, idx)

                if issubclass(prop_type, BaseType):
                    child_args = self.get_child_args(flat_pre=prop_name)
                    child_val = to_dict(val, **child_args)
                    new_vals.append(child_val)
                else:
                    if self.FLAT:
                        new_vals.append({prop_name: val})
                    else:
                        new_vals.append(val)

            if self.FLAT and not self.PARENT:
                [self.RESULT.update(v) for v in new_vals]
            else:
                self.RESULT[prop] = new_vals

    def get_child_args(self, **kwargs):
        child_args = {}
        child_args.update(self.KWARGS)
        child_args.update(kwargs)
        child_args['parent'] = False
        return child_args


def explode_json(val):
    """pass."""
    try:
        result = json.loads(val)
        # only explode non str/int types
        if not isinstance(result, (list, tuple, dict)):
            result = None
    except:
        result = None
    return result


def flatten_pyobj(pyobj, prefix='', sep='_'):
    """pass."""
    result = {}
    if isinstance(pyobj, (list, tuple)):
        for idx, val in enumerate(pyobj):
            mypre = '{}{}{}'.format(prefix, sep, idx)
            result.update(flatten_pyobj(val, mypre, sep))
    elif isinstance(pyobj, dict):
        for k, v in pyobj.items():
            mypre = '{}{}{}'.format(prefix, sep, k)
            result.update(flatten_pyobj(v, mypre, sep))
    else:
        if not prefix:
            prefix = type(pyobj).__name__
        result[prefix] = pyobj
    return result


def to_dict(obj, **kwargs):
    converter = ToDict(obj, **kwargs)
    result = converter.RESULT
    return result


def to_json(obj, **kwargs):
    obj_dict = to_dict(obj, **kwargs)
    result = jsonify(obj_dict, **kwargs)
    return result


def to_csv(obj, **kwargs):
    kwargs['flat'] = kwargs.get('flat', True)  # TODO CONSTANT
    obj_dict = to_dict(obj, **kwargs)

    if LIST_NAME in obj_dict:
        kwargs['rows'] = obj_dict[LIST_NAME]
    else:
        kwargs['rows'] = [obj_dict]

    kwargs['skips'] = kwargs.get('skips', []) + SKIPS
    kwargs['firsts'] = kwargs.get('firsts', []) + FIRSTS
    kwargs['lasts'] = kwargs.get('lasts', []) + LASTS

    writer = ExcelWriter()
    result = writer.run(**kwargs)
    return result