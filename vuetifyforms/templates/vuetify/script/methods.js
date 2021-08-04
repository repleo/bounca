methods: {
    resetForm: function (){
        Object.assign(this.$data, initialState());
        this.$refs.form.reset();
    },
{% for method in form.vue_methods %}
    {{ method|safe }},
{% endfor %}
},
