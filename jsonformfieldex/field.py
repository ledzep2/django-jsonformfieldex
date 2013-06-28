from django.forms.fields import Field
from django.forms.widgets import *
from django.forms.util import ValidationError as FormValidationError, ErrorList
from django.utils.datastructures import SortedDict as D
from django.utils.simplejson import loads
from django.utils.translation import ugettext_lazy as _

from .widget import JSONWidget, iterhelper, merge_dict


class JSONFormFieldEx(Field):
    """ A form field which hosts a tree of other fields providing validation and can serialize to json string """
    def clean(self, value):
        """ Take a tuple of fields_valie(dict) and json_value(str) from JSONWidget """
        fields_value, json_value = value

        errors = ErrorList()
        # Clear json value
        if isinstance(json_value, basestring):
            try:
                json_value = loads(json_value)
            except ValueError:
                json_value = None
                errors.append(_(u"JSON Field: Enter valid JSON"))

        if json_value != None and not isinstance(json_value, dict):
            errors.append(_(u"JSON Field: Must be a dict"))

        # Clear fields
        assert(isinstance(fields_value, dict))

        if json_value:
            merge_dict(fields_value, json_value)

        def _clean(f, _values):
            for k, v in iterhelper(f):
                if isinstance(v, (dict, tuple, list)):
                    _clean(v, _values.get(k, {}))
                    if not self.allow_empty and not _values.get(k):
                        _values.pop(k)
                else:
                    try:
                        tmp = _values.get(k, None)
                        v.clean(tmp)
                        tmp = v.to_python(tmp)
                        if self.allow_empty:
                            _values[k] = tmp
                        elif not tmp:
                            _values.pop(k)

                    except FormValidationError, e:
                        errors.extend(map(lambda x,y:x+y, [u'%s %s: ' % (_("Field"), k)] * len(e.messages), e.messages))

        _clean(self.fields, fields_value)

        if errors:
            raise FormValidationError(errors)

        return fields_value

    def __init__(self, fields={}, allow_json_input=True, allow_empty = True, **kwargs):
        self.fields, self.widgets = self.construct_fields_and_widgets(fields)
        self.allow_empty = allow_empty
        # Don't allow other widgets, coz only JSONWidget returns what we need.
        # Namely django.contrib.admin will try to override the our widget
        kwargs['widget'] = JSONWidget(self.widgets, allow_json_input)
        super(JSONFormFieldEx, self).__init__(**kwargs)

    def construct_fields_and_widgets(self, fields):
        f = D()
        w = D()
        for k, v in iterhelper(fields):
             if isinstance(v, (dict, tuple, list)):
                f[k], w[k] = self.construct_fields_and_widgets(v)
             else:
                try:
                    v = isinstance(v, type) and v() or v
                    f[k], w[k] = v, v.widget
                except TypeError, e:
                    raise Exception("Cant construct field: %s(type:%s) with empty arguments" % (k, v))
        return f, w