from libs.basic import *


class MySsl(Basic):
    domain_id = None
    cert_id = None
    certificate_records = {}

    def __init__(self, config):
        super().__init__(config)
        if 'domain_id' not in config or not config['domain_id']:
            print(" get domains")
            self.get_domain_id()
        else:
            self.domain_id = config['domain_id']
        if 'cert_id' in config and config['cert_id']:
            self.cert_id = config['cert_id']

    def list(self):
        url = self.url + '/api/cert/list/' + self.domain_id + '/'
        data = self.send_get(url)
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
            'subdomains': self.config['cert_subdomain'] if 'cert_subdomain' in self.config else []
        }
        url = self.url + '/api/cert/create/' + self.domain_id + '/'
        data = self.send_post(url, data)
        pprint(data)
        return data['success']

    def export(self):
        url = self.url + '/api/cert/get/' + self.domain_id + '/' + self.cert_id + '/'
        data = self.send_get(url)
        pprint(data)
        import os
        my_dir = 'certs/' + self.config['cert_folder_name']
        os.makedirs(my_dir, exist_ok=True)
        with open(my_dir + '/fullchain.pem', 'w') as f:
            f.write(data['certificate']['chain'])
            f.close()
        with open(my_dir + '/privkey.pem', 'w') as f:
            f.write(data['certificate']['private_key'])
            f.close()

    def create_certificate_name(self, domain_name: str, is_wildcard=False, is_production=False, subdomains=None) -> str:
        name = ''
        if is_production:
            name += 'production '
        else:
            name += 'stage '
        if is_wildcard:
            name = 'wildcard.' + domain_name
        else:
            if subdomains:
                name += ' '.join(subdomains)

        return name.strip()
