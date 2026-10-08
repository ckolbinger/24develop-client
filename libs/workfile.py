import hashlib
import json
import os

from libs.dns import *
from libs.ssl import *
from libs.domain import *
from libs.team import *


class Workfile(Basic):
    sub_config = {}
    dns_client = None
    ssl_client = None
    domain_client = None
    zone_state = None

    def __init__(self, config):
        super().__init__(config)

        self.sub_config = {
            'token': self.config['token'],
            'secret': self.config.get('secret'),
            'url': self.config['url'],
            'disable_ssl_verify': self.config.get('disable_ssl_verify', False),
        }

        self.domain_client = Domain(self.sub_config)

    def start_work_script(self):
        if 'domain' not in self.config:
            return False

        self.run_worker_dns()
        self.run_worker_ssl()
        return True

    def run_worker_ssl(self):
        for domain in self.config['domain']:
            if 'ssl' not in (self.config['domain'][domain] or {}):
                continue
            domain_id = self.domain_client.get_or_create_domain(domain)
            if domain_id:
                my_data = self.config['domain'][domain]['ssl']
                self.sub_config['domain_id'] = domain_id
                self.sub_config['domain'] = domain
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
                    # create already queues the issuing, no commit needed
                    if self.ssl_client.add():
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
                # import the zone first, so its records are not added again by the dns compare
                self.import_zone_file(domain)
                self.dns_client = Dns(self.sub_config)
                # self.dns_client.domain_id = domain_id
                self.check_domain_recordset(domain)
        return True

    def import_zone_file(self, domain):
        my_data = self.config['domain'][domain] or {}
        if not my_data.get('zone_file'):
            return True
        # copy, the domain client shares sub_config
        zone_config = dict(self.sub_config)
        zone_config['zone_file'] = self.resolve_path(my_data['zone_file'])
        zone_config['auto_commit'] = my_data.get('auto_commit', True)

        # skip the import if the zone file did not change since the last successful import
        state = {'domain_id': self.sub_config['domain_id'], 'sha256': self.hash_file(zone_config['zone_file'])}
        if self.load_zone_state().get(domain) == state:
            print("zone file unchanged, skip import " + zone_config['zone_file'])
            return True

        print("import zone file " + zone_config['zone_file'])
        if not Domain(zone_config).import_zone():
            return False
        self.zone_state[domain] = state
        self.save_zone_state()
        return True

    @staticmethod
    def hash_file(path):
        with open(path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()

    def zone_state_file(self):
        return self.resolve_path(self.config.get('zone_state_file') or 'zone_state.json')

    def load_zone_state(self):
        if self.zone_state is None:
            self.zone_state = {}
            try:
                with open(self.zone_state_file(), 'r') as f:
                    self.zone_state = json.load(f)
            except FileNotFoundError:
                pass
            except (OSError, ValueError) as e:
                print("could not read zone state file, import all zones: " + str(e))
        return self.zone_state

    def save_zone_state(self):
        try:
            with open(self.zone_state_file(), 'w') as f:
                json.dump(self.zone_state, f, indent=2)
        except OSError as e:
            print("could not write zone state file, zones are imported again next run: " + str(e))

    def resolve_path(self, path):
        # relative paths are relative to the config file
        if os.path.isabs(path) or not self.config.get('config'):
            return path
        return os.path.join(os.path.dirname(self.config['config']), path)

    def check_domain_recordset(self, domain):
        self.dns_client.list()
        self.compare_recordset(domain)

    def compare_recordset(self, domain):
        changed = False
        for record in (self.config['domain'][domain] or {}).get('dns') or []:
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
                    if self.dns_client.add_record(my_record):
                        changed = True
        if changed:
            # push the new records to the dns servers
            self.dns_client.commit()
