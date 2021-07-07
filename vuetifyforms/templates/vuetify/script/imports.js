{% for name, path in form.vue_imports %}
import {{ name|safe }} from '{{ path|safe }}';
{% endfor %}
