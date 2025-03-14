from libs.dns import *
from libs.ssl import *
from libs.domain import *
from libs.team import *


class Workfile(Basic):
    sub_config = {}
    dns_client = None
    ssl_client = None
    domain_client = None

    def __init__(self, config):
        super().__init__(config)

        self.sub_config = {
            'token': self.config['token'],
            'url': self.config['url'],
        }

        self.domain_client = Domain(self.sub_config)

    def start_work_script(self):
        if 'domain' not in self.config:
            return False

        self.run_worker_dns()
        self.run_worker_ssl()

    def run_worker_ssl(self):
        for domain in self.config['domain']:
            if 'ssl' not in self.config['domain'][domain]:
                continue
            domain_id = self.domain_client.get_or_create_domain(domain)
            if domain_id:
                my_data = self.config['domain'][domain]['ssl']
                self.sub_config['domain_id'] = domain_id
                self.sub_config['domain'] = domain
                self.sub_config['disable_ssl_verify'] = self.config[
                    'disable_ssl_verify'] if 'disable_ssl_verify' in self.config else False
                self.sub_config['cert_base_folder'] = self.config['cert_base_folder']
                self.sub_config['cert_folder_name'] = my_data[
                    'folder_name'] if 'folder_name' in my_data else None
                self.sub_config['cert_subdomain'] = my_data['subdomains'] if 'subdomains' in my_data else []
                self.sub_config['cert_production'] = my_data['is_production'] if 'is_production' in my_data else False
                self.sub_config['cert_wildcard'] = my_data['is_wildcard'] if 'is_wildcard' in my_data else False
                self.sub_config['cert_auto_renew'] = my_data['is_auto_renew'] if 'is_auto_renew' in my_data else False

                self.ssl_client = MySsl(self.sub_config)
                self.ssl_client.list()
                if not self.ssl_client.check_certificate_exists_remote():
                    self.ssl_client.add()
                    self.ssl_client.commit()
                    self.ssl_client.wait_for_new_certificate()
                self.ssl_client.check_certificate_exists_local()

        return True

    def run_worker_dns(self):
        self.domain_client.list()
        for domain in self.config['domain']:
            domain_id = self.domain_client.get_or_create_domain(domain)
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
