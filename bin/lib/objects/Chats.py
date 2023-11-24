#!/usr/bin/env python3
# -*-coding:UTF-8 -*

import os
import sys

from datetime import datetime

from flask import url_for
# from pymisp import MISPObject

sys.path.append(os.environ['AIL_BIN'])
##################################
# Import Project packages
##################################
from lib import ail_core
from lib.ConfigLoader import ConfigLoader
from lib.objects.abstract_chat_object import AbstractChatObject, AbstractChatObjects


from lib.objects.abstract_subtype_object import AbstractSubtypeObject, get_all_id
from lib.data_retention_engine import update_obj_date
from lib.objects import ail_objects
from lib.timeline_engine import Timeline

from lib.correlations_engine import get_correlation_by_correl_type

config_loader = ConfigLoader()
baseurl = config_loader.get_config_str("Notifications", "ail_domain")
r_object = config_loader.get_db_conn("Kvrocks_Objects")
r_cache = config_loader.get_redis_conn("Redis_Cache")
config_loader = None


################################################################################
################################################################################
################################################################################

class Chat(AbstractChatObject):
    """
    AIL Chat Object.
    """

    def __init__(self, id, subtype):
        super(Chat, self).__init__('chat', id, subtype)

    # # WARNING: UNCLEAN DELETE /!\ TEST ONLY /!\
    def delete(self):
        # # TODO:
        pass

    def get_link(self, flask_context=False):
        if flask_context:
            url = url_for('correlation.show_correlation', type=self.type, subtype=self.subtype, id=self.id)
        else:
            url = f'{baseurl}/correlation/show?type={self.type}&subtype={self.subtype}&id={self.id}'
        return url

    def get_svg_icon(self):  # TODO
        # if self.subtype == 'telegram':
        #     style = 'fab'
        #     icon = '\uf2c6'
        # elif self.subtype == 'discord':
        #     style = 'fab'
        #     icon = '\uf099'
        # else:
        #     style = 'fas'
        #     icon = '\uf007'
        style = 'fas'
        icon = '\uf086'
        return {'style': style, 'icon': icon, 'color': '#4dffff', 'radius': 5}

    def get_meta(self, options=set()):
        meta = self._get_meta(options=options)
        meta['name'] = self.get_name()
        meta['tags'] = self.get_tags(r_list=True)
        if 'icon':
            meta['icon'] = self.get_icon()
        if 'info':
            meta['info'] = self.get_info()
        if 'username' in options:
            meta['username'] = self.get_username()
        if 'subchannels' in options:
            meta['subchannels'] = self.get_subchannels()
        if 'nb_subchannels':
            meta['nb_subchannels'] = self.get_nb_subchannels()
        if 'created_at':
            meta['created_at'] = self.get_created_at(date=True)
        return meta

    def get_misp_object(self):
        # obj_attrs = []
        # if self.subtype == 'telegram':
        #     obj = MISPObject('telegram-account', standalone=True)
        #     obj_attrs.append(obj.add_attribute('username', value=self.id))
        #
        # elif self.subtype == 'twitter':
        #     obj = MISPObject('twitter-account', standalone=True)
        #     obj_attrs.append(obj.add_attribute('name', value=self.id))
        #
        # else:
        #     obj = MISPObject('user-account', standalone=True)
        #     obj_attrs.append(obj.add_attribute('username', value=self.id))
        #
        # first_seen = self.get_first_seen()
        # last_seen = self.get_last_seen()
        # if first_seen:
        #     obj.first_seen = first_seen
        # if last_seen:
        #     obj.last_seen = last_seen
        # if not first_seen or not last_seen:
        #     self.logger.warning(
        #         f'Export error, None seen {self.type}:{self.subtype}:{self.id}, first={first_seen}, last={last_seen}')
        #
        # for obj_attr in obj_attrs:
        #     for tag in self.get_tags():
        #         obj_attr.add_tag(tag)
        # return obj
        return

    ############################################################################
    ############################################################################

    # users that send at least a message else participants/spectator
    # correlation created by messages
    def get_users(self):
        users = set()
        accounts = self.get_correlation('user-account').get('user-account', [])
        for account in accounts:
            users.add(account[1:])
        return users

    def _get_timeline_username(self):
        return Timeline(self.get_global_id(), 'username')

    def get_username(self):
        return self._get_timeline_username().get_last_obj_id()

    def get_usernames(self):
        return self._get_timeline_username().get_objs_ids()

    def update_username_timeline(self, username_global_id, timestamp):
        self._get_timeline_username().add_timestamp(timestamp, username_global_id)

    #### ChatSubChannels ####


    #### Categories ####

    #### Threads ####

    #### Messages #### TODO set parents

    # def get_last_message_id(self):
    #
    #     return r_object.hget(f'meta:{self.type}:{self.subtype}:{self.id}', 'last:message:id')

    # def add(self, timestamp, obj_id, mess_id=0, username=None, user_id=None):
    #     date = # TODO get date from object
    #     self.update_daterange(date)
    #     update_obj_date(date, self.type, self.subtype)
    #
    #
    #     # daily
    #     r_object.hincrby(f'{self.type}:{self.subtype}:{date}', self.id, 1)
    #     # all subtypes
    #     r_object.zincrby(f'{self.type}_all:{self.subtype}', 1, self.id)
    #
    #     #######################################################################
    #     #######################################################################
    #
    #     # Correlations
    #     self.add_correlation('item', '', item_id)
    #     # domain
    #     if is_crawled(item_id):
    #         domain = get_item_domain(item_id)
    #         self.add_correlation('domain', '', domain)

    # importer -> use cache for previous reply SET to_add_id: previously_imported : expire SET key -> 30 mn


class Chats(AbstractChatObjects):
    def __init__(self):
        super().__init__('chat')

# TODO factorize
def get_all_subtypes():
    return ail_core.get_object_all_subtypes('chat')

def get_all():
    objs = {}
    for subtype in get_all_subtypes():
        objs[subtype] = get_all_by_subtype(subtype)
    return objs

def get_all_by_subtype(subtype):
    return get_all_id('chat', subtype)


if __name__ == '__main__':
    chat = Chat('test', 'telegram')
    r = chat.get_messages()
    print(r)
