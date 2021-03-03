<template>
    <div class="form-group">
        <label>{{label}}</label>
        <ValidationProvider name="password" vid="password1" rules="required" v-slot="v">
            <input type="password"
                   name="password1"
                   v-model="subscription.password1"
                   class="form-control form-control-lg"
                   :class="{ 'is-invalid' : v.errors.length > 0 }"/>
            <ul class="invalid-feedback">
                <li v-for="(error, index) in v.errors" :key="index">{{ error }}</li>
            </ul>
        </ValidationProvider>
    </div>
</template>


<script>
export default {
    inheritAttrs: false,
    props: ["value", "label"],
    model: {
      prop: "value",
      event: "update"
    }
};
</script>

