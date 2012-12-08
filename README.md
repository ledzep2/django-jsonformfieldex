Django JSON Form Field Ex
=========================

Want to take advantage of json-field or hstore, but tired of managing plain json strings?
This is where **django-jsonformfieldex** comes in.

This form field can render any json-valid dict as a form. So you can just sit back and manage your fields INSIDE jsonfield as easily as any other fields.

How it works?
-------------

Basically, you define a dict of fields for your json data, and it will take care of the rest. Just like this:

    class MyCustomer(Form):
        slug = SlugField()
        store = JSONFormFieldEx({
            "profile": {
                "name": CharField(max_length=10),
    			"email": EmailField,
            },
            "account1": {
    			"number": IntegerField,
    			"balance": DecimalField(max_digits=10, decimal_places=2),
            },
    		"date_joined": DateTimeField,
        })

And this is what it looks like after rendered without style:

![screenshot1](http://ledzep2.github.com/django-jsonformfieldex/screenshot1.jpg)

It looks and works just like an ordinary form, with validation enabled. When you clean the form, you will have `cleaned_data['store']` as a dict. So you can directly save that to your json field.

**And even better, it also works with ModelForm**! (requires a slightly patched version of django-jsonfield, please see my repo)

Usage
------

`JSONFormFieldEx` constructor takes two arguments itself, along with **kwargs to pass to its parent class `forms.Field`:

* `fields`: a dict of fields  
You can provide either field type or field instance for each field. `Fields` also supports SortedDict or [(k,v)...] to preserve ordering of fields.

* `allow_json_input`: True|False  
If True, it will render an additional textarea allowing user to enter arbitary json string (just like jsonfield)

Note: when `fields` is empty, `allow_json_input` will be automatically set to True
