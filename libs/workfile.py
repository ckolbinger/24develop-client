import yaml
from libs.dns import *
from libs.ssl import *
from libs.basic import *


class Workfile(Basic):
    sub_config = {}
    dns_client = None
    domain_client = None

    def __init__(self, config):
        super().__init__(config)

        self.sub_config = {
            'token': self.config['token'],
            'url': self.config['url'],
            'auto_commit': self.config['url'] if 'auto_commit' in self.config else False,
        }

        self.domain_client = Domain(self.sub_config)

    def start_work_script(self):
        if 'domain' not in self.config:
            return False
        self.domain_client.list()
        for domain in self.config['domain']:
            domain_id = self.domain_client.get_domain_id(domain)
            if domain_id:
                self.sub_config['domain_id'] = domain_id
                self.sub_config['domain'] = domain
                self.dns_client = Dns(self.sub_config)
                # self.dns_client.domain_id = domain_id
                self.check_domain_recordset(domain)
        return True

    def check_domain_recordset(self, domain):
        self.dns_client.list()
        self.compare_recordset(domain)

    def compare_recordset(self, domain):
        for record in self.config['domain'][domain]['dns']:
            pprint(record)
            for c in record['value']:
                my_record = {'name': record['name'], 'type': record['type'], 'content': c}
                my_record['ttl'] = record['ttl'] if 'ttl' in record else 3600
                my_record['prio'] = record['prio'] if 'prio' in record else None
                my_record['weight'] = record['weight'] if 'weight' in record else None
                my_record['port'] = record['port'] if 'port' in record else None
                new_record = self.dns_client.create_record_key(my_record)
                if new_record not in self.dns_client.domain_records:
                    print("add record")
                    pprint(my_record)
                    self.dns_client.add_record(my_record)
