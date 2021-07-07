vee-validate3 does not implement all the rules offered by vee-validate2.
You can add these rules after importing ValidationProvider:

```angular2html
/* vee-validate config */
setInteractionMode('eager');
Vue.component('extend', extend);
Vue.component('ValidationObserver', ValidationObserver);
Vue.component('ValidationProvider', ValidationProvider);

// install rules and localization
Object.keys(rules).forEach((rule) => {
  extend(rule, rules[rule]);
});
extend('url', {
  validate(value) {
    const pattern = new RegExp('^(https?:\\/\\/)?' + // protocol
      '((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.)+[a-z]{2,}|' + // domain name
      '((\\d{1,3}\\.){3}\\d{1,3}))' + // OR ip (v4) address
      '(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*' + // port and path
      '(\\?[;&a-z\\d%_.~+=-]*)?' + // query string
      '(\\#[-a-z\\d_]*)?$', 'i'); // fragment locator
    return pattern.test(value);
  },
  message: 'Please enter a valid URL',
});
localize('en', en);
/* vee-validate config */
```
