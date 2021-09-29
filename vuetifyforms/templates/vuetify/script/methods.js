methods: {
    resetForm: function (){
        Object.assign(this.$data, initialState());
        this.$refs.form.reset();
        {{ form.vue_extra_init_rules|safe }}
    },
{% for method in form.vue_methods %}
    {{ method|safe }},
{% endfor %}
},
