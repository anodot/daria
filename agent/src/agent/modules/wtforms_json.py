# Copyright (c) 2012-2014, Konsta Vesterinen
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * The names of the contributors may not be used to endorse or promote products
#   derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import collections
import six

from wtforms import Form
from wtforms.validators import DataRequired, Optional
from wtforms_sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms.fields import (
    _unset_value,
    BooleanField,
    Field,
    FieldList,
    FileField,
    FormField,
    StringField
)


class InvalidData(Exception):
    pass


def flatten_json(
    form,
    json,
    parent_key='',
    separator='-',
    skip_unknown_keys=True
):
    """Flattens given JSON dict to cope with WTForms dict structure.

    :param form: WTForms Form object
    :param json: json to be converted into flat WTForms style dict
    :param parent_key: this argument is used internally be recursive calls
    :param separator: default separator
    :param skip_unknown_keys:
        if True unknown keys will be skipped, if False throws InvalidData
        exception whenever unknown key is encountered

    Examples::

        >>> flatten_json(MyForm, {'a': {'b': 'c'}})
        {'a-b': 'c'}
    """
    if not isinstance(json, collections.abc.Mapping):
        raise InvalidData(
            u'This function only accepts dict-like data structures.'
        )

    items = []
    for key, value in json.items():
        try:
            unbound_field = getattr(form, key)
        except AttributeError:
            if skip_unknown_keys:
                continue
            else:
                raise InvalidData(u"Unknown field name '%s'." % key)

        try:
            field_class = unbound_field.field_class
        except AttributeError:
            if skip_unknown_keys:
                continue
            else:
                raise InvalidData(u"Key '%s' is not valid field class." % key)

        new_key = parent_key + separator + key if parent_key else key
        if isinstance(value, collections.abc.MutableMapping) and issubclass(field_class, FormField):
            nested_form_class = unbound_field.bind(Form(), '').form_class
            items.extend(
                flatten_json(nested_form_class, value, new_key)
                .items()
            )
        elif (
            isinstance(value, collections.abc.MutableMapping)
            or isinstance(value, list)
            and not issubclass(field_class, FieldList)
            or not isinstance(value, list)
        ):
            items.append((new_key, value))
        else:
            nested_unbound_field = unbound_field.bind(
                Form(),
                ''
            ).unbound_field
            items.extend(
                flatten_json_list(
                    nested_unbound_field,
                    value,
                    new_key,
                    separator
                )
            )
    return dict(items)


def flatten_json_list(field, json, parent_key='', separator='-'):
    items = []
    for i, item in enumerate(json):
        new_key = parent_key + separator + str(i)
        if (
            isinstance(item, dict) and
            issubclass(getattr(field, 'field_class'), FormField)
        ):
            nested_class = field.field_class(
                *field.args,
                **field.kwargs
            ).bind(Form(), '').form_class
            items.extend(
                flatten_json(nested_class, item, new_key)
                .items()
            )
        else:
            items.append((new_key, item))
    return items


@property
def patch_data(self):
    if hasattr(self, '_patch_data'):
        return self._patch_data

    data = {}

    def is_optional(field):
        return Optional in [v.__class__ for v in field.validators]

    def is_required(field):
        return DataRequired in [v.__class__ for v in field.validators]

    for name, f in six.iteritems(self._fields):
        if f.is_missing:
            if is_optional(f):
                continue
            elif not is_required(f) and f.default is None:
                continue
            elif isinstance(f, FieldList) and f.min_entries == 0:
                continue

        if isinstance(f, FormField):
            data[name] = f.patch_data
        elif isinstance(f, FieldList):
            if issubclass(f.unbound_field.field_class, FormField):
                data[name] = [i.patch_data for i in f.entries]
            else:
                data[name] = [i.data for i in f.entries]
        else:
            data[name] = f.data
    return data


def monkey_patch_field_process(func):
    """
    Monkey patches Field.process method to better understand missing values.
    """
    def process(self, formdata, data=_unset_value, **kwargs):
        call_original_func = True
        if not isinstance(self, FormField):

            if formdata and self.name in formdata:
                if (
                    len(formdata.getlist(self.name)) == 1 and
                    formdata.getlist(self.name) == [None]
                ):
                    call_original_func = False
                    self.data = None
                self.is_missing = not bool(formdata.getlist(self.name))
            else:
                self.is_missing = True

        if call_original_func:
            func(self, formdata, data=data, **kwargs)

        if (
            formdata and self.name in formdata and
            formdata.getlist(self.name) == [None] and
            isinstance(self, FormField)
        ):
            self.form._is_missing = False
            self.form._patch_data = None

        if isinstance(self, StringField) and not isinstance(self, FileField):
            if not self.data:
                try:
                    self.data = self.default()
                except TypeError:
                    self.data = self.default
            else:
                self.data = six.text_type(self.data)

    return process


class MultiDict(dict):
    def getlist(self, key):
        val = self[key]
        if not isinstance(val, list):
            val = [val]
        return val

    def getall(self, key):
        return [self[key]]


@classmethod
def from_json(
    cls,
    formdata=None,
    obj=None,
    prefix='',
    data=None,
    meta=None,
    skip_unknown_keys=True,
    **kwargs
):
    return cls(
        formdata=MultiDict(
            flatten_json(cls, formdata, skip_unknown_keys=skip_unknown_keys)
        ) if formdata else None,
        obj=obj,
        prefix=prefix,
        data=data,
        meta=meta,
        **kwargs
    )


@property
def is_missing(self):
    if hasattr(self, '_is_missing'):
        return self._is_missing
    return any(not field.is_missing for field in self._fields.values())


@property
def field_list_is_missing(self):
    if hasattr(self, '_is_missing'):
        return self._is_missing
    return all(field.is_missing for field in self.entries)


def monkey_patch_process_formdata(func):
    def process_formdata(self, valuelist):
        valuelist = list(map(six.text_type, valuelist))

        return func(self, valuelist)
    return process_formdata


def init():
    Form.is_missing = is_missing
    FieldList.is_missing = field_list_is_missing
    Form.from_json = from_json
    Form.patch_data = patch_data
    FieldList.patch_data = patch_data
    QuerySelectField.process_formdata = monkey_patch_process_formdata(
        QuerySelectField.process_formdata
    )
    QuerySelectMultipleField.process_formdata = \
        monkey_patch_process_formdata(
            QuerySelectMultipleField.process_formdata
        )
    Field.process = monkey_patch_field_process(Field.process)
    FormField.process = monkey_patch_field_process(FormField.process)
    BooleanField.false_values += False,
