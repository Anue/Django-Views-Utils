from django.http import HttpResponseRedirect, HttpResponse
from django.utils import simplejson
from django.views.decorators.http import require_POST
from django.utils.translation import ugettext as _

@require_POST
def ajax_modelform_view(request, form=None, use_user=True, redirect_success=None, **kwargs):
    """Ajax Model form validator. Examples:
    Use it in a view:
    def create_profile(request):
        if request.method == "POST":
            return ajax_modelform_view(request, form=Profile, use_user=True,
                                       redirect_success=reverse('home'))

    Use it in a url conf:
    url(r^'ajax_create_profile/$', 'ajax_modelform_view',
                name="ajax_modelform",
                kwargs={'form':Profile,
                        'use_user':True,
                        'redirect_succes': reverse('home')}),
    
    """
    instance = kwargs.pop('instance', None)
    instance_id = request.POST.get('id')
    if not instance and instance_id:
        try:
            instance = form.Meta.model(pk=instance_id)
        except form.Meta.model.DoesNotExist:
            pass
    if use_user:
        form = form(request.POST, user=request.user, instance=instance, **kwargs)
    else:
        form = form(request.POST, instance=instance, **kwargs)
    if form.is_valid():
        obj = form.save()
        object_name = form.Meta.model._meta.verbose_name
        if not redirect_success:
            return HttpResponse(simplejson.dumps({
                "success": True,
                "msg": object_name + _(u" Added") if not instance else _u(" Saved"),
                "object_id": obj.id,
            }), "application/json")
        else:
            return HttpResponse(simplejson.dumps({
                "success": True,
                "redirect": redirect_success
            }), "application/json")
    else:
        error_list = []
        if form.errors.has_key('__all__'):
            for error in form.errors['__all__']:
                error_list.append("<h3>%s</h3>" % error)
            del(form.errors['__all__'])

        for field_name, errors in form.errors.items():
            msg =  "<h3>%s</h3>" % _(form.fields[field_name].label)
            msg += "<ul>"
            for error in errors:
                msg += "<li>%s</li>" % error
            msg += "</ul>"
            error_list.append(msg)

        return HttpResponse(simplejson.dumps({
            "success": False,
            "errors": error_list
        }), "application/json")


