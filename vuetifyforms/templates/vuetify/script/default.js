{% load crispy_forms_vuetify %}
{% include "vuetify/script/imports.js" %}

export default {
    name: '{{ form.form_title }}',

    data() {
        return {% make_data_object form %};
    },
{% include "vuetify/script/methods.js" %}
};
