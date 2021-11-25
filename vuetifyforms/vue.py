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

    def as_vuetify(self):
        """
        Returns this form rendered as HTML with <div class="form-group">s for each form field.
        """
        # wrap non-field-errors into <div>-element to prevent re-boxing
        error_row = '<div class="djng-line-spreader">%s</div>'
        div_element = self._html_output(
            normal_row="<div%(html_class_attr)s>%(label)s%(field)s%(help_text)s%(errors)s</div>",
            error_row=error_row,
            row_ender="</div>",
            help_text_html='<span class="help-block">%s</span>',
            errors_on_separate_row=False,
        )
        return div_element
