class VuetifyFormMixin(object):
    field_css_classes = "form-group has-feedback"
    widget_css_classes = "form-control"
    form_error_css_classes = "djng-form-errors"
    field_error_css_classes = "djng-form-control-feedback djng-field-errors"
    label_css_classes = "control-label"

    @classmethod
    def get_subclasses(cls):
        for subclass in cls.__subclasses__():
            yield from subclass.get_subclasses()
            yield subclass
