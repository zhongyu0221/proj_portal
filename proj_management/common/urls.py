from django.urls import path

from . import views

app_name = 'common'

urlpatterns = [
    # path('',
    #      views.TopSearchView.as_view(),
    #      name='top_search'),

    path('sampl-variant-interp/',
         views.AjaxSearchView.as_view(),
         name="sampl_variant_interp_search"),

]

