import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from pprint import pprint

# connect / read timeout in seconds
REQUEST_TIMEOUT = (10, 60)
_session = None


def get_session():
    # one shared session, reuses the tls connection instead of a new handshake per request
    global _session
    if _session is None:
        # retry only failures before the request is sent (connect, tls handshake),
        # never after it reached the server: commit / delete / disable are GET but not idempotent
        retry = Retry(total=5, connect=5, other=5, read=0, status=0, backoff_factor=1, raise_on_status=False)
        _session = requests.Session()
        _session.mount('https://', HTTPAdapter(max_retries=retry))
        _session.mount('http://', HTTPAdapter(max_retries=retry))
    return _session


class Basic:
    token = ""
    secret = None
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
        self.secret = config.get('secret')
        self.url = config['url'].rstrip('/')
        self.headers = {'Authorization': self.build_auth_header(), "Content-Type": "application/json"}
        if 'disable_ssl_verify' in config and config['disable_ssl_verify']:
            self.verify_request = False

    def build_auth_header(self):
        # scoped api token with secret, legacy drf token without
        if self.secret:
            return 'ApiToken ' + self.token + ':' + self.secret
        return 'Token ' + self.token

    def run(self):
        if self.domain_is_needed and not self.domain_id:
            print("no domain defined")
            return False
        self.selector()

    def send_post(self, url, data, log_data=True):
        if log_data:
            pprint(data)
        print(url)
        try:
            resp = get_session().post(url, json=data, headers=self.headers, verify=self.verify_request,
                                      timeout=REQUEST_TIMEOUT)
        except requests.RequestException as e:
            print("request failed: " + str(e))
            return {'success': False}
        return self.handle_response(resp)

    def send_get(self, url):
        print(url)
        try:
            resp = get_session().get(url, headers=self.headers, verify=self.verify_request, timeout=REQUEST_TIMEOUT)
        except requests.RequestException as e:
            print("request failed: " + str(e))
            return {'success': False}
        return self.handle_response(resp)

    def handle_response(self, resp):
        # always return a dict with 'success', http 200 does not mean success
        try:
            data = resp.json()
        except ValueError:
            data = {}
        if resp.status_code != 200:
            print(resp.status_code, data.get('detail', resp.text))
            return {'success': False}
        if not data.get('success'):
            self.print_errors(data)
        return data

    @staticmethod
    def print_errors(data):
        # error / errors / msg can be a string, a list or a dict field -> list
        for key in ('error', 'errors', 'msg'):
            if key not in data or not data[key]:
                continue
            value = data[key]
            if isinstance(value, dict):
                for field, messages in value.items():
                    print(field + ': ' + ', '.join(str(m) for m in messages))
            elif isinstance(value, list):
                for message in value:
                    print(message)
            else:
                print(value)

    def get_domain_id(self):
        url = self.url + '/api/domain/list/'
        data = self.send_get(url)
        if data and 'domains' in data:
            for domain in data['domains']:
                if self.config['domain'] in (domain['name'], domain.get('display_name')):
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
        elif self.config['action'] == 'import':
            self.import_zone()

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

    def import_zone(self):
        print("import not implemented")
        pass
