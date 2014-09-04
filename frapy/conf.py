import os
import string
import config
import collections
import yaml

from urlparse import urlparse
from voluptuous import Schema, Invalid, Required

#import ipdb

class ConfigLoader:

    @classmethod
    def load(cls, configname, **kwargs):
        config = cls._yaml_load(configname)
        if 'base' in config:
            final_config = cls._yaml_load(config['base'])
            cls._update_config(final_config, config)
            final_config.pop('base')
            if kwargs:
                cls._update_config(final_config, kwargs)
            return final_config
        else:
            return config

    @classmethod
    def _yaml_load(cls, configname):
        with file("tpl/{0}.yml".format(configname)) as f:
            contents = f.read()
        return yaml.load(contents)

    @classmethod
    def _update_config(cls, d, u):
        for k, v in u.iteritems():
            if isinstance(v, collections.Mapping):
                r = cls._update_config(d.get(k, {}), v)
                d[k] = r
            else:
                d[k] = u[k]
        return d

class ConfigValidator:

    @classmethod
    def validate(cls, config):
        Schema({
            Required('url') : cls._validate_url,
            Required('forum') : Schema({
                Required('category') : cls._validate_extract_rule,
            }),
            Required('category') : Schema({
                Required('attributes') : Schema({
                    Required('title') : cls._validate_extract_rule,
                }),
                Required('thread') : cls._validate_extract_rule,
                'subcategory' : cls._validate_extract_rule,
                'next' : cls._validate_extract_rule,
            }),
            'thread' : Schema({
                Required('attributes') : Schema({
                    Required('title') : cls._validate_extract_rule,
                }),
                Required('post') : cls._validate_extract_rule,
                'next' : cls._validate_extract_rule,
            }),
            'post' : Schema({
                Required('attributes') : Schema({
                    Required('post_timestamp') : cls._validate_extract_rule,
                    Required('post_content') : cls._validate_extract_rule,
                    Required('user_nickname') : cls._validate_extract_rule,
                    'user_location' : cls._validate_extract_rule,
                    'user_join_date' : cls._validate_extract_rule,
                })
            }),
        })(config)

    @classmethod
    def _validate_url(cls, url):
        pieces = urlparse(url)
        if not all([
            pieces.scheme,
            pieces.netloc,
            set(pieces.netloc) <= set(string.letters + string.digits + '-.'), # and others?
            pieces.scheme in ['http', 'https', 'ftp']
        ]):
            raise Invalid("Deze URL is ongeldig")

    @classmethod
    def _validate_extract_rule(cls, rule):
        if not any([
            rule.startswith('xpath:'),
            rule.startswith('regex:')
        ]):
            raise Invalid("Ongeldige extractie regel gedefinieerd")

