from django.forms.widgets import Widget, Textarea
from django.utils.safestring import mark_safe
from django.utils.simplejson import dumps, loads, JSONDecodeError
from django.utils.datastructures import SortedDict as D
from django.utils.translation import ugettext_lazy as _

import copy

iterhelper = lambda d: isinstance(d, dict) and d.iteritems() or iter(d)

def merge_dict(d1, d2):
    """ Merge two dict recursively to d1. Return value should be ignored """
    if isinstance(d2, (dict, tuple, list)):
        for k,vb in iterhelper(d2):
            va = d1.get(k)
            if not isinstance(va, dict):
                d1[k] = vb
            elif not merge_dict(va, vb):
                d1[k] = vb
        return True

    return False

class JSONWidget(Widget):
    """ Render or extract a value dict to/from a tree hierarchy of widgets """
    def __init__(self, widgets = {}, allow_json_input = True, attrs=None):
        self.widgets = self.construct_widgets(widgets)

        self.other = (not self.widgets or allow_json_input) and Textarea() or None
        if self.other:
            self.other._widget_name = '__other'

        super(JSONWidget, self).__init__(attrs)

    def construct_widgets(self, widgets, name_prefix = ''):
        """ Take a dict of widgets """
        ret = D()
        for k, v in iterhelper(widgets):
            name = name_prefix + '_%s' % k
            if isinstance(v, (dict, tuple, list)):
                tmp = self.construct_widgets(v, name)
            else:
                tmp = isinstance(v, type) and v() or v
                tmp._widget_name = name
                tmp.is_localized = self.is_localized

            ret[k] = tmp

        return ret

    def render(self, name, value, attrs=None):
        # value could be a tuple of 2 elements: fields, json (if forms.clean succeeded)
        # or a json string (if forms.clean failed)
        if isinstance(value, tuple) and len(value) == 2:
            fields_value, json_value = value
        else:
            fields_value = self.decode(value) or {}
            json_value = None

        fields_value = copy.deepcopy(fields_value)

        output = []
        final_attrs = self.build_attrs(attrs)
        id_ = final_attrs.get('id', None)

        # Render fields
        def _render_widget(w, _values):
            for k, v in iterhelper(w):
                wv = _values.pop(k, {})  # Pop fields along the way, so leftover will be json_value
                if isinstance(v, dict):
                    output.append(u"<fieldset class='dictsubwidget'><legend>%s</legend>" % k.capitalize())
                    _render_widget(v, wv)
                    output.append(u"</fieldset>")
                else:
                    a = final_attrs
                    if id_:
                        a = dict(final_attrs, id='%s_%s' % (id_, v._widget_name))
                    output.append(u"<p><label>%s:</label>" % k.capitalize())
                    output.append(v.render(name + v._widget_name, wv != {} and wv or '', a))
                    output.append(u"</p>")

        if self.widgets:
            output.append(u"<fieldset class='dictwidget'><legend>%s</legend>" % name.capitalize())
            _render_widget(self.widgets, fields_value)
            output.append(u"</fieldset>")

        # Render json_value
        if json_value == None and fields_value:
            json_value = self.encode(fields_value)

        if self.other:
            if self.widgets: output.append(u"<fieldset class='dictwidget'><legend>%s %s</legend>" % (name.capitalize(), _(u"JSON Field")))
            output.append(self.other.render(name + self.other._widget_name, json_value, final_attrs))
            if self.widgets: output.append(u"</fieldset>")

        return mark_safe(self.format_output(output))

    def id_for_label(self, id_):
        # See the comment for RadioSelect.id_for_label()
        if id_:
            id_ += '_0'
        return id_
    id_for_label = classmethod(id_for_label)

    def value_from_datadict(self, data, files, name):
        fields_value = self.widgets and self.construct_dict(self.widgets, data, files, name) or D()
        json_value = self.other and self.other.value_from_datadict(data, files, name + self.other._widget_name) or None

        return fields_value, json_value

    def construct_dict(self, w, data, files, name):
        """ Construct a value dict for fields """
        ret = D()
        for k, v in w.iteritems():
            if isinstance(v, dict):
                ret[k] = self.construct_dict(v, data, files, name)
            else:
                ret[k] = v.value_from_datadict(data, files, name + v._widget_name)
        return ret

    def _has_changed(self, initial, data):
        """
        initial: dict or json string from model field
        data: combined(dict) or separated (fields,json)
        """
        if not initial:
            initial = D()
        elif not isinstance(initial, dict):
            initial = self.decode(initial) or D()
        else:
            initial = copy.deepcopy(initial)

        if isinstance(data, tuple):
            data = self.decompress(data)

        # Compare field values
        def _changed(w, i, d):
            for k, v in w.iteritems():
                if isinstance(v, dict) and _changed(v, i.get(k, {}), d.get(k, {})):
                    return True
                elif v._has_changed(i.get(k), d.get(k)):
                    return True
                i.pop(k, None)
                d.pop(k, None)

            return False

        if _changed(self.widgets, initial, data):
            return True

        # Json values
        # If allow_json_input is false, we will simply ignore those non-field values
        if self.other and initial != data:
            return True

        return False

    def format_output(self, rendered_widgets):
        return u''.join(rendered_widgets)

    def decompress(self, value):
        """ Decompress (fields, json) to a single dict """
        v = copy.deepcopy(value[0])
        merge_dict(v, self.decode(value[1]) or {})
        return v

    def encode(self, value):
        if isinstance(value, dict):
            return dumps(value, indent=4)
        else:
            return value

    def decode(self, value):
        if isinstance(value, (str, unicode)):
            return loads(value)
        else:
            return value

    def __deepcopy__(self, memo):
        obj = super(JSONWidget, self).__deepcopy__(memo)
        obj.widgets = copy.deepcopy(self.widgets)
        return obj