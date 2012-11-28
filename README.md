Django JSON Form Field Ex
=========================

Want to take advantage of json-field or hstore, but tired of managing plain json strings?
This is where **django-jsonformfieldex** comes in.

This form field can render any json-valid dict as a form. So you can just sit back and manage your fields INSIDE jsonfield as easily as any other fields.

How it works?
-------------

Basically, you define a dict of fields for your json data, and it will take care of the rest. Just like this:

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
	
And this is what it looks like after rendered without any style:

<table><tr><th><label for="id_slug">Slug:</label></th><td><input type="text" name="slut" id="id_slut" /></td></tr>
<tr><th><label for="id_store_0">Store:</label></th><td><fieldset class='dictwidget'><legend>Store</legend><fieldset class='dictsubwidget'><legend>Profile</legend><p><label>Name:</label><input id="id_store__profile_name" type="text" name="store_profile_name" maxlength="10" /></p><p><label>Email:</label><input type="text" name="store_profile_email" id="id_store__profile_email" /></p></fieldset><fieldset class='dictsubwidget'><legend>Account1</legend><p><label>Balance:</label><input type="text" name="store_account1_balance" id="id_store__account1_balance" /></p><p><label>Number:</label><input type="text" name="store_account1_number" id="id_store__account1_number" /></p></fieldset><p><label>Date_joined:</label><input type="text" name="store_date_joined" id="id_store__date_joined" /></p></fieldset><fieldset class='dictwidget'><legend>Store JSON Field</legend><textarea id="id_store" rows="10" cols="40" name="store__other"></textarea></fieldset></td></tr>
</table>

It looks and works just like an ordinary form, with validation enabled. When you clean the form, you will have `cleaned_data['store']` as a dict. So you can directly save that to your json field.

**And even better, it also works with ModelForm**! (requires a slightly patched version of django-jsonfield, please see my repo)

Usage
------

`JSONFormFieldEx` constructor takes two arguments:

* `fields`: a dict of fields  
field type or field instance is ok)

* `allow_json_input`: True|False  
If True, it will render an additional textarea allowing user to enter arbitary json string (just like jsonfield)

Note: when `fields` is empty, `allow_json_input` will be automatically set to True
