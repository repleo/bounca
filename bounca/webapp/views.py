from django.shortcuts import render


import json
from django.http import HttpResponse
from django.views.generic.edit import FormView
from django.utils.encoding import force_text
from django.core.urlresolvers import reverse_lazy

from .forms import AddRootCAForm

class AddRootCAFormView(FormView):
    template_name = 'bounca/dashboard/forms/add-root-ca.html'
    form_class = AddRootCAForm
    success_url = reverse_lazy('bounca:index') 

    def ajax(self, request):
        form = self.form_class(data=json.loads(request.body))
        response_data = {'errors': form.errors, 'success_url': force_text(self.success_url)}
        return HttpResponse(json.dumps(response_data), content_type="application/json")

