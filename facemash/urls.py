from django.conf.urls import url

from .views import (about_page, glicko2_rating_system, play, ratings_page,
                    submit)

urlpatterns = [
    url(r'^$', play, name='play'),
    url(r'^calcultor/(?P<winner_id>\d+)-(?P<loser_id>\d+)/$', glicko2_rating_system, name="calculator"),
    url(r'^ratings/$', ratings_page, name="ratings"),
    url(r'^submit/$', submit, name="submit"),
    url(r'^about/$', about_page, name="about"),
]
