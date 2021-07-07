methods: {
{% for method in form.vue_methods %}
  {{ method|safe }},
{% endfor %}
},
