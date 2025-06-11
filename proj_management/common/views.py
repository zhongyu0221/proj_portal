from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, DeleteView
from django.shortcuts import render

# from haystack.generic_views import SearchView
# from haystack.query import RelatedSearchQuerySet
# from haystack.forms import HighlightedModelSearchForm, HighlightedSearchForm

#from bioinfo.models import SampleVariantInterp, OrderReport
#from orders.models import TestOrder


# class TopSearchView(LoginRequiredMixin):
#     '''
#     Search view for the top search page
#     '''
#     template_name = 'search/search.html'
#     form_class = HighlightedModelSearchForm
#     queryset = RelatedSearchQuerySet()
#
#     def form_valid(self, form):
#         """
#         get query string from user input and automatically adding
#         amino acid code to the search
#         """
#         self.queryset = form.search()
#         query = form.cleaned_data.get(self.search_field)
#
#         context = self.get_context_data(**{
#             self.form_name: form,
#             'query': query,
#             'object_list': self.queryset,
#
#         })
#         return self.render_to_response(context)
#
#     def get_queryset(self):
#         sqs = super(TopSearchView, self).get_queryset().load_all()
#
#         return sqs
#
#     def get_context_data(self, *args, **kwargs):
#         context = super(TopSearchView, self).get_context_data(*args, **kwargs)
#         # do something
#         return context
#
#
# class AjaxSearchView(LoginRequiredMixin, SearchView):
#     """For sample variant interpretation search
#     """
#     template_name = 'search/search_ajax.html'
#     form_class = HighlightedSearchForm
#     queryset = RelatedSearchQuerySet()
#
#     def form_valid(self, form):
#         """
#         get query string from user input and automatically adding
#         amino acid code to the search
#         """
#         self.queryset = form.search()
#         query = form.cleaned_data.get(self.search_field)
#         query_alt = get_protein_change(query)
#         new_query = "{0} {1}  ".format(query, query_alt)
#         context = self.get_context_data(**{
#             self.form_name: form,
#             'query': new_query,
#             'object_list': self.queryset
#         })
#         return self.render_to_response(context)
#
#     def get_queryset(self):
#         queryset = super(AjaxSearchView, self).get_queryset()
#         queryset = queryset.load_all()
#
#         return queryset
#
#     def get_context_data(self, *args, **kwargs):
#         context = super(AjaxSearchView, self).get_context_data(*args, **kwargs)
#         return context
#

class AjaxCreateView(CreateView):
    template_name = "common/ajax_form.html"

    def form_valid(self, form):
        self.object = form.save()

        return render(self.request, 'common/item_edit_form_success.html',
                      {'item': self.object, 'action': 'created'})


class AjaxUpdateView(UpdateView):
    template_name = "common/ajax_form.html"



    def form_valid(self, form):
        if form.is_valid:
            self.object = form.save()
        else:
            print('invalid form')

        return render(self.request, 'common/item_edit_form_success.html',
                      {'item': self.object, 'action': 'updated'})


class AjaxDeleteView(DeleteView):
    template_name = "common/ajax_confirm_delete.html"

    def form_valid(self, form):
        self.object.delete()
        return render(self.request, 'common/item_edit_form_success.html',
                      {'item': self.object, 'action': 'deleted'})
