{% load crispy_forms_vuetify %}
{% include "vuetify/script/imports.js" %}

function initialState (){
  return {% make_data_object form %}
}

export default {
    name: '{{ form.form_title }}',

    data() {
        return initialState();
    },
{% include "vuetify/script/methods.js" %}
};
