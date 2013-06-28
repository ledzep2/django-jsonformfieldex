from widget import *
from field import *
from django.forms import Form, widgets, fields
from unittest import TestCase

import datetime
from decimal import Decimal

class MergeDictTest(TestCase):
    def test(self):
        a = {}
        b = {'qwe': 321}
        merge_dict(a, b)
        self.assertDictEqual(b, a)

        a = {1:3}
        b = None
        merge_dict(a, b)
        self.assertDictEqual({1:3}, a)

        a = {1:3, 2:{2:2}}
        b = {1:3, 2:2}
        merge_dict(a, b)
        self.assertDictEqual({1:3, 2:2}, a)

        a = {1:1}
        b = {2:2}
        merge_dict(a, b)
        self.assertDictContainsSubset(b, a)

        b = {3:4, 2: {1:4}}
        merge_dict(a, b)
        self.assertDictEqual({1:1, 2:{1:4}, 3:4}, a)

        a = {1:1, 2: {2:3}}
        b = {3:4, 2: {1:4}}
        merge_dict(a, b)
        self.assertDictEqual({1:1, 2:{1:4, 2:3}, 3:4}, a)


        a = {1:1, 2: {2:3, 3: {4:4}}}
        b = {3:4, 2: {1:4, 3: {5:5}, 5:{7:7}}}
        merge_dict(a, b)
        self.assertDictEqual({1:1, 2:{1:4, 2:3, 3:{4:4, 5:5}, 5:{7:7}}, 3:4}, a)

class WidgetTest(TestCase):
    def test(self):
        # JSON value
        w = JSONWidget()
        self.assertTrue(w.other)
        html = w.render('test', {1:1, 2:2})
        self.assertTrue(html.find('name="test__other"') > -1)

        f, j = w.value_from_datadict({'__other': '{1:1, 2:2}'}, {}, '')
        self.assertFalse(f)
        self.assertEqual('{1:1, 2:2}', j)

        self.assertFalse(w._has_changed({1:1, 2:2}, {1:1, 2:2}))
        self.assertTrue(w._has_changed({1:1, 2:2}, {1:1, 2:3}))
        self.assertFalse(w._has_changed('{"1":1, "2":2}', ({}, '{"1":1, "2":2}')))
        self.assertTrue(w._has_changed('{"1":1, "2":2}', ({}, '{"1":1, "2":3}')))

        # Fields
        w = JSONWidget({
            "1": widgets.TextInput,
        }, allow_json_input=False)
        self.assertFalse(w.other)

        html = w.render('test', {1:1, 2:2})
        self.assertTrue(html.find('<input type="text" name="test_1" /></p></fieldset>') > -1)
        self.assertFalse(html.find('name="test__other"') > -1)

        html = w.render('test', {"1":1, 2:2})
        self.assertTrue(html.find('<input type="text" name="test_1" value="1" /></p></fieldset>') > -1)

        f, j = w.value_from_datadict({'__other': '{1:1, 2:2}'}, {}, '')
        self.assertDictEqual({"1":None}, f)
        self.assertFalse(j)

        self.assertFalse(w._has_changed({"1":1, 2:2}, {"1":1, 2:2}))
        self.assertFalse(w._has_changed({"1":1, 2:2}, {"1":1, 2:3}))
        self.assertTrue(w._has_changed({"1":1, 2:2}, {"1":2, 2:2}))
        self.assertFalse(w._has_changed('{"1":1, "2":2}', ({}, '{"1":1, "2":2}')))
        self.assertFalse(w._has_changed('{"1":1, "2":2}', ({}, '{"1":1, "2":3}')))


    def testForm(self):
        class F(Form):
            settings = JSONFormFieldEx({
                "name": fields.CharField(max_length=10),
                "email": fields.EmailField(),
                "age": fields.IntegerField(),
            })
            username = fields.CharField(max_length=10)

        f = F()
        html = unicode(f)
        self.assertTrue(html.find('name="settings_name"') > -1)
        self.assertTrue(html.find('name="settings_email"') > -1)
        self.assertTrue(html.find('name="settings_age"') > -1)
        self.assertTrue(html.find('name="username"') > -1)

        initial = {
            "settings": '{"name":"Peter", "email":"a@a.com", "age":13}',
            "username": "peter123",
        }
        f = F(initial=initial)
        self.assertFalse(f.is_valid())
        html = unicode(f)
        self.assertTrue(html.find('name="settings_name" value="Peter"') > -1)
        self.assertTrue(html.find('name="settings_email" value="a@a.com"') > -1)
        self.assertTrue(html.find('name="settings_age" value="13"') > -1)
        self.assertTrue(html.find('name="username" value="peter123"') > -1)

        f = F({
            "settings_name": "Jack",
            "settings_email": "b@b.com",
            "settings_age": "16",
            "username": "jack123",
            "settings__other": '{"random1": {"a":1, "b":2}}',
        }, initial=initial)
        self.assertTrue(f.is_valid())
        html = unicode(f)
        self.assertTrue(html.find('name="settings_name" value="Jack"') > -1)
        self.assertTrue(html.find('name="settings_email" value="b@b.com"') > -1)
        self.assertTrue(html.find('name="settings_age" value="16"') > -1)
        self.assertTrue(html.find('name="username" value="jack123"') > -1)
        self.assertDictEqual({
            "username": "jack123",
            "settings": {
                "name": "Jack",
                "email": "b@b.com",
                "age": 16,
                "random1" : {
                    "a": 1,
                    "b": 2
                },
            },
        }, f.cleaned_data)

        class F(Form):
            settings = JSONFormFieldEx({
                "name": fields.CharField(max_length=10),
                "email": fields.EmailField(),
                "age": fields.IntegerField(),
            }, allow_json_input=False)
            username = fields.CharField(max_length=10)

        f = F({
            "settings_name": "Jack",
            "settings_email": "b@b.com",
            "settings_age": "16",
            "username": "jack123",
            "settings__other": '{"random1": {"a":1, "b":2}}',
        }, initial=initial)
        self.assertTrue(f.is_valid())
        html = unicode(f)
        self.assertTrue(html.find('name="settings_name" value="Jack"') > -1)
        self.assertTrue(html.find('name="settings_email" value="b@b.com"') > -1)
        self.assertTrue(html.find('name="settings_age" value="16"') > -1)
        self.assertTrue(html.find('name="username" value="jack123"') > -1)
        self.assertDictEqual({
            "username": "jack123",
            "settings": {
                "name": "Jack",
                "email": "b@b.com",
                "age": 16,
            },
        }, f.cleaned_data)

    def testFields(self):
        target = {
            "char": u"asdf",
            "email": u"a@a.com",
            "int": 98981,
            "float": 3123.41234,
            "decimal": Decimal('3213.123'),
            "date": datetime.date(2012,1,10),
            "time": datetime.time(23,49,49),
            "datetime": datetime.datetime(2012,1,10,23,49,49),
            "regex": u"312qwe",
            "url": u"http://google.com/",
            "bool": True,
            "choice": u"a",
        }
        d = dict(('settings_' + k, str(v)) for k, v in target.iteritems())

        class F(Form):
            settings = JSONFormFieldEx({
                "char": fields.CharField,
                "email": fields.EmailField,
                "int": fields.IntegerField,
                "float": fields.FloatField,
                "decimal": fields.DecimalField(max_digits=10, decimal_places=3),
                "date": fields.DateField,
                "time": fields.TimeField,
                "datetime": fields.DateTimeField,
                "regex": fields.RegexField('\d{3}\w{3}'),
                "url": fields.URLField,
                "bool": fields.BooleanField,
                "choice": fields.ChoiceField(choices=(("a", "A"), ("b", "B"))),
            }, allow_json_input=False)

        f = F()
        html = unicode(f)
        for i in d:
            self.assertTrue(html.find('name="%s"' % i) > -1)


        f = F(d)
        self.assertTrue(f.is_valid())
        self.assertDictEqual({
            "settings": target
        }, f.cleaned_data)

    def test_empty(self):
        target = {
            "a": u"asdf",
            "b": u"",
            "c": None
        }
        d = dict(('settings_' + k, str(v)) for k, v in target.iteritems())
        d.pop('settings_c')

        class F(Form):
            settings = JSONFormFieldEx({
                "a": fields.CharField,
                "b": fields.CharField(required=False),
                "c": fields.IntegerField(required=False),
            }, allow_empty=True, allow_json_input=False)

        f = F()
        html = unicode(f)
        for i in d:
            self.assertTrue(html.find('name="%s"' % i) > -1)

        f = F(d)
        self.assertTrue(f.is_valid())
        self.assertDictEqual({
            "settings": target
        }, f.cleaned_data)

        ######
        class F(Form):
            settings = JSONFormFieldEx({
                "a": fields.CharField,
                "b": fields.CharField(required=False),
                "c": fields.IntegerField(required=False),
            }, allow_empty=False, allow_json_input=False)

        f = F()
        html = unicode(f)
        for i in d:
            self.assertTrue(html.find('name="%s"' % i) > -1)

        f = F(d)
        self.assertTrue(f.is_valid())
        self.assertDictEqual({
            "settings": {'a': u'asdf'}
        }, f.cleaned_data)


    def testx(self):
        class MyCustomer(Form):
            slug = fields.SlugField()
            store = JSONFormFieldEx({
                "profile": {
                    "name": fields.CharField(max_length=10),
        			"email": fields.EmailField,
                },
                "account1": {
        			"number": fields.IntegerField,
        			"balance": fields.DecimalField(max_digits=10, decimal_places=2),
                },
        		"date_joined": fields.DateTimeField,
            })

        f = MyCustomer()
        #f1=open('1.html', 'w')
        #print f