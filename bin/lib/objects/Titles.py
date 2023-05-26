#!/usr/bin/env python3
# -*-coding:UTF-8 -*

import os
import sys

from hashlib import sha256
from flask import url_for

from pymisp import MISPObject

sys.path.append(os.environ['AIL_BIN'])
##################################
# Import Project packages
##################################
from lib.ConfigLoader import ConfigLoader
from lib.objects.abstract_daterange_object import AbstractDaterangeObject, AbstractDaterangeObjects

config_loader = ConfigLoader()
r_objects = config_loader.get_db_conn("Kvrocks_Objects")
baseurl = config_loader.get_config_str("Notifications", "ail_domain")
config_loader = None


class Title(AbstractDaterangeObject):
    """
    AIL Title Object.
    """

    def __init__(self, id):
        super(Title, self).__init__('title', id)

    # def get_ail_2_ail_payload(self):
    #     payload = {'raw': self.get_gzip_content(b64=True),
    #                 'compress': 'gzip'}
    #     return payload

    # # WARNING: UNCLEAN DELETE /!\ TEST ONLY /!\
    def delete(self):
        # # TODO:
        pass

    def get_content(self, r_type='str'):
        if r_type == 'str':
            return self._get_field('content')

    def get_link(self, flask_context=False):
        if flask_context:
            url = url_for('correlation.show_correlation', type=self.type, id=self.id)
        else:
            url = f'{baseurl}/correlation/show?type={self.type}&id={self.id}'
        return url

    # TODO # CHANGE COLOR
    def get_svg_icon(self):
        return {'style': 'fas', 'icon': '\uf1dc', 'color': '#1E88E5', 'radius': 5}

    def get_misp_object(self):
        obj_attrs = []
        obj = MISPObject('tsk-web-history')
        obj.first_seen = self.get_first_seen()
        obj.last_seen = self.get_last_seen()

        obj_attrs.append(obj.add_attribute('title', value=self.get_content()))
        for obj_attr in obj_attrs:
            for tag in self.get_tags():
                obj_attr.add_tag(tag)
        return obj

    def get_meta(self, options=set()):
        meta = self._get_meta(options=options)
        meta['id'] = self.id
        meta['tags'] = self.get_tags(r_list=True)
        meta['content'] = self.get_content()
        return meta

    def add(self, date, item_id):
        self._add(date, item_id)

    def create(self, content, _first_seen=None, _last_seen=None):
        self._set_field('content', content)
        self._create()


def create_title(content):
    title_id = sha256(content.encode()).hexdigest()
    title = Title(title_id)
    if not title.exists():
        title.create(content)
    return title

class Titles(AbstractDaterangeObjects):
    """
        Titles Objects
    """
    def __init__(self):
        super().__init__('title')

    def get_metas(self, obj_ids, options=set()):
        return self._get_metas(Title, obj_ids, options=options)

    def sanitize_name_to_search(self, name_to_search):
        return name_to_search


# if __name__ == '__main__':
#     from lib import crawlers
#     from lib.objects import Items
#     for item in Items.get_all_items_objects(filters={'sources': ['crawled']}):
#         title_content = crawlers.extract_title_from_html(item.get_content())
#         if title_content:
#             print(item.id, title_content)
#             title = create_title(title_content)
#             title.add(item.get_date(), item.id)