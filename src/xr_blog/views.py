from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from django.utils.feedgenerator import Atom1Feed
from django.utils.timezone import datetime

from .models import BlogEntryPage, BlogListPage


class RssFeed(Feed):
    def get_object(self, request, feed_id: int):
        blog_list = get_object_or_404(BlogListPage, page_ptr_id=feed_id)
        return blog_list

    def title(self, blog_list: BlogListPage):
        return blog_list.title

    def link(self, blog_list: BlogListPage):
        return blog_list.get_absolute_url()

    def description(self, blog_list: BlogListPage):
        return blog_list.description

    def items(self, blog_list: BlogListPage):
        return blog_list.entries().live().order_by("-date")

    def item_title(self, item: BlogEntryPage):
        return item.title

    def item_description(self, item: BlogEntryPage):
        #  return item.content
        return item.description

    def item_author_name(self, item: BlogEntryPage):
        return item.author

    def item_pubdate(self, item: BlogEntryPage):
        return datetime(year=item.date.year, month=item.date.month, day=item.date.day)


class AtomFeed(RssFeed):
    feed_type = Atom1Feed
    subtitle = RssFeed.description
