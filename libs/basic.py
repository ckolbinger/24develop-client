import requests
from pprint import pprint


class Basic:
    token = ""
    url = ""
    headers = {}
    config = {}
    domain_id = None
    team_id = None
    verify_request = True
    domain_is_needed = True

    def __init__(self, config):
        self.config = config
        self.token = config['token']
        self.url = config['url']
        self.headers = {'Authorization': 'Token ' + self.token, "Content-Type": "application/json"}
        if 'disable_ssl_verify' in config and config['disable_ssl_verify']:
            self.verify_request = False
    def run(self):
        if self.domain_is_needed:
            print("no domain defined")
            if not self.domain_id:
                return False
        self.selector()

    def send_post(self, url, data):
        pprint(data)
        print(url)
        resp = requests.post(url, json=data, headers=self.headers, verify=self.verify_request)
        if resp.status_code == 200:
            data = resp.json()
            return data
        else:
            print(resp.status_code)
            print(resp.text)

    def send_get(self, url):
        print(url)
        resp = requests.get(url, headers=self.headers, verify=self.verify_request)
        if resp.status_code == 200:
            data = resp.json()
            return data
        else:
            print(resp.status_code)
            print(resp.text)
            print("record not found")

    def get_domain_id(self):
        url = self.url + '/api/domain/list/'
        data = self.send_get(url)
        if data and 'domains' in data:
            for domain in data['domains']:
                if domain['name'] == self.config['domain']:
                    self.domain_id = domain['id']
                    return True
        return False

    def config(self):
        pass

    def select_action(self):
        pass

    def selector(self):
        if 'action' not in self.config or not self.config['action']:
            return False
        if self.config['action'] == 'list':
            self.list()
        elif self.config['action'] == 'add':
            self.add()
        elif self.config['action'] == 'delete':
            self.delete()
        elif self.config['action'] == 'update':
            self.update()
        elif self.config['action'] == 'commit':
            self.commit()
        elif self.config['action'] == 'export':
            self.export()

        return True

    def list(self):
        print("list not implemented")
        pass

    def add(self):
        print("add not implemented")
        pass

    def delete(self):
        print("delete not implemented")
        pass

    def update(self):
        print("update not implemented")
        pass

    def commit(self):
        print("commit not implemented")
        pass

    def export(self):
        print("export not implemented")
        pass
