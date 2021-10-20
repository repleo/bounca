from crispy_forms.layout import Field, Div, \
    LayoutObject
from crispy_forms.utils import TEMPLATE_PACK
from django.template.loader import render_to_string


class VueFlex(Div):
    """
    Layout object. It wraps fields in a div so the wrapper can be used as a flex. Example::
        Flex('form_field_1', 'form_field_2')
    Flex components will automatically fill the available space in a row or column. They will
    also shrink relative to the rest of the flex items in the flex container when a specific size
    is not designated.. Example::
        Flex('form_field_1', xs12=True, md6=True)
    """

    template = "%s/layout/flex.html"


class VueSpacer(Div):
    """
    Layout object. Spacer for button fields
    """

    template = "%s/layout/spacer.html"


class VueScriptElem(LayoutObject):
    """
    Layout object.

    Abstract class for vue elems
    """

    template = None

    def __init__(self, elems, **kwargs):
        self.elems = elems
        self.template = kwargs.pop("template", self.template)

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK, **kwargs):
        template = self.get_template_name(template_pack)
        return render_to_string(template, {"script": self})


class VueImports(VueScriptElem):
    """
    Layout object. Spacer for button fields
    """

    template = "%s/script/imports.js"


class VueMethods(VueScriptElem):
    """
    Layout object. Spacer for button fields
    """

    template = "%s/script/methods.js"


class VueField(Field):
    """
    Layout object, It contains one field name, and you can add attributes to it easily.
    For setting class attributes, you need to use `css_class`, as `class` is a Python keyword.

    Example::

        Field('field_name', style="color: #333;", css_class="whatever", id="field_name")
    """

    template = "%s/field.html"

    def __init__(self, *args, **kwargs):
        self.fields = list(args)

        if not hasattr(self, "attrs"):
            self.attrs = {}
        else:
            # Make sure shared state is not edited.
            self.attrs = self.attrs.copy()

        if "css_class" in kwargs:
            if "class" in self.attrs:
                self.attrs["class"] += " %s" % kwargs.pop("css_class")
            else:
                self.attrs["class"] = kwargs.pop("css_class")

        self.wrapper_class = kwargs.pop("wrapper_class", None)
        self.template = kwargs.pop("template", self.template)

        # We use kwargs as HTML attributes, turning data_id='test' into data-id='test'
        self.attrs.update({k.replace("_", "-"): v for k, v in kwargs.items()})
