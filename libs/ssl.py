import sys

from libs.basic import *
import os
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from datetime import datetime, timezone, timedelta
import time


class MySsl(Basic):
    domain_id = None
    cert_id = None
    certificate_records = {}
    domain_is_needed = True

    def __init__(self, config):
        super().__init__(config)
        if 'domain_id' not in config or not config['domain_id']:
            print("get domains")
            self.get_domain_id()
        else:
            self.domain_id = config['domain_id']
        if 'cert_id' in config and config['cert_id']:
            self.cert_id = config['cert_id']

    def list(self):
        url = self.url + '/api/cert/list/' + self.domain_id + '/'
        data = self.send_get(url)
        print("list certificates")
        if data['success']:
            for cert in data['certificates']:
                print(cert['id'], cert['name'], cert['valid_to'])
                self.certificate_records[cert['name']] = cert['id']
        else:
            print("no certificates found")

    def add(self):
        data = {
            'is_wildcard': self.config['cert_wildcard'] if 'cert_wildcard' in self.config else False,
            'is_production': self.config['cert_production'] if 'cert_production' in self.config else False,
            'is_auto_renew': self.config['cert_auto_renew'] if 'cert_auto_renew' in self.config else False,
            'subdomains': self.config['cert_subdomain'] if 'cert_subdomain' in self.config else [],
            'folder_name': self.config['cert_folder_name'] if 'cert_folder_name' in self.config else None
        }
        url = self.url + '/api/cert/create/' + self.domain_id + '/'
        data = self.send_post(url, data)
        if data['success']:
            self.cert_id = data['cert_id']
        pprint(data)
        return data['success']

    def commit(self):
        url = self.url + '/api/cert/commit/' + self.domain_id + '/' + self.cert_id + '/'
        data = self.send_get(url)
        pprint(data)

    def export(self):
        url = self.url + '/api/cert/get/' + self.domain_id + '/' + self.cert_id + '/'
        data = self.send_get(url)

        if data['success']:
            my_dir = self._build_folder_name()
            os.makedirs(my_dir, exist_ok=True)
            with open(my_dir + '/fullchain.pem', 'w') as f:
                f.write(data['certificate']['chain'])
                f.close()
            with open(my_dir + '/privkey.pem', 'w') as f:
                f.write(data['certificate']['private_key'])
                f.close()
            print("certificate exported to " + my_dir)

    def create_certificate_name(self) -> str:
        name = ''

        if self.config['cert_production']:
            name += 'production '
        else:
            name += 'stage '
        if self.config['cert_wildcard']:
            name = 'wildcard.' + self.config['domain']
        else:
            if self.config['cert_subdomain']:
                xx = sorted(self.config['cert_subdomain'])
                for d in xx:
                    if d.endswith(self.config['domain']):
                        name += d + ' '
                    else:
                        name += d + '.' + self.config['domain'] + ' '

        return name.strip()

    def check_certificate_exists_remote(self):
        cert_name = self.create_certificate_name()
        print(cert_name)

        if cert_name in self.certificate_records:
            self.cert_id = self.certificate_records[cert_name]
            return True
        return False

    def check_certificate_exists_local(self):
        path = self._build_folder_name()
        my_path = os.path.join(path, 'fullchain.pem')
        if os.path.exists(my_path):
            # validate ssl cert
            if not self.check_valid_to():
                self.init_revalidate()
            else:
                print("certificate is valid")
        else:
            self.export()

    def check_valid_to(self) -> bool:
        my_path = self._build_folder_name() + '/fullchain.pem'
        if os.path.exists(my_path):
            with open(my_path, 'r') as f:
                cert = f.read()
                f.close()
            try:
                x509_cert = x509.load_pem_x509_certificate(cert.encode('utf-8'), default_backend())
                utc_dt = datetime.now(timezone.utc)
                if x509_cert.not_valid_after_utc - timedelta(days=2) > utc_dt:
                    return True
            except Exception as e:
                print(e)
        return False

    def init_revalidate(self):
        print("revalidate certificate")
        self.commit()
        self.wait_for_new_certificate()

    def wait_for_new_certificate(self):
        count = 0
        tries = 10
        while count < tries:
            count += 1
            self.export()
            if self.check_valid_to():
                return
            print(f"{count} of {tries}")
            time.sleep(20)

    def _build_folder_name(self) -> str:
        if not self.config['cert_folder_name']:
            self.config['cert_folder_name'] = self.create_certificate_name().replace(' ', '_')
        return str(os.path.join(self.config['cert_base_folder'], self.config['cert_folder_name']))
