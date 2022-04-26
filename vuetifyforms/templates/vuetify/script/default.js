{% load crispy_forms_vuetify %}
{% include "vuetify/script/imports.js" %}

function initialState (){
  const data = {% make_data_object form %};
  {{ form.vue_extra_initial_statements|safe }}
  return data;
}

export default {
    name: '{{ form.form_component_name }}',
    props: [{% for prop in form.vue_props %}'{{ prop }}'{% if not forloop.last %},{% endif %}{% endfor %}],
    data() {
        return initialState();
    },
    watch: {
      {% for watch in form.vue_watchers %}
        {{ watch|safe }},
      {% endfor %}
    },
    mounted() {
       {{ form.vue_mounted|safe }}
    },
    {% include "vuetify/script/methods.js" %}
};
