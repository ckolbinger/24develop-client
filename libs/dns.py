from libs.basic import *


class Dns(Basic):
    domain_id = None
    record_id = None
    domain_records = {}

    def __init__(self, config):
        super().__init__(config)
        if 'domain_id' not in config or not config['domain_id']:
            print(" get domains")
            self.get_domain_id()
        else:
            self.domain_id = config['domain_id']
        if 'record_id' in config and config['record_id']:
            self.record_id = config['record_id']

    def create_send_data(self):
        data = {}
        for k, v in self.config.items():
            if k.startswith("record_"):
                data[k[7:]] = v
        if 'auto_commit' in self.config and self.config['auto_commit']:
            data['commit'] = True
        else:
            data['commit'] = False

        return data

    def get_domain_id(self):
        url = self.url + '/api/domain/list/'
        data = self.send_get(url)
        if data and 'domains' in data:
            for domain in data['domains']:
                if domain['name'] == self.config['domain']:
                    self.domain_id = domain['id']
                    return True
        return False

    def add(self):
        xx = self.create_send_data()
        url = self.url + '/api/record/' + self.domain_id + '/add/'
        data = self.send_post(url, xx)
        return data['success']

    def add_record(self, record):
        url = self.url + '/api/record/' + self.domain_id + '/add/'
        data = self.send_post(url, record)
        return data['success']

    def list(self):
        url = self.url + '/api/record/' + self.domain_id + '/'
        data = self.send_get(url)

        if data and 'records' in data:
            for record in data['records']:
                print(record['id'], record['name'], record['type'], record['content'], record['ttl'],
                      record['disabled'])
                print(record['prio'], record['weight'], record['port'], record['description'])
                my_record_key = self.create_record_key(record)
                self.domain_records[my_record_key] = record

    def create_record_key(self, record):
        if record['name'] == '@' or record['name'] == '':
            record['name'] = self.config['domain']
        if not record['name'].endswith(self.config['domain']):
            record['name'] = record['name'] + '.' + self.config['domain']
        key = str(record['name']) + '-' + str(record['type']) + '-' + str(record['content'])
        return key

    def delete(self):
        data = self.send_get(self.url + '/api/record/' + self.domain_id + '/delete/' + self.record_id + '/')
        return data['success']

    def update(self):
        xx = self.create_send_data()
        url = self.url + '/api/record/' + self.domain_id + '/set/' + self.record_id + '/'
        data = self.send_post(url, xx)
        pprint(data)
        return data['success']

    def commit(self):
        url = self.url + '/api/domain/commit/' + self.domain_id + '/'
        data = self.send_get(url)
        return data['success']


class Domain(Basic):
    domain_list = {}

    def __init__(self, config):
        super().__init__(config)
        self.selector()

    def list(self):
        url = self.url + '/api/domain/list/'
        data = self.send_get(url)
        if data and 'domains' in data:
            for domain in data['domains']:
                print(domain['id'], domain['name'])
                self.domain_list[domain['name']] = domain['id']

    def add(self):
        if 'team_id' not in self.config or not self.config['team_id']:
            self.get_team_id()
        url = self.url + '/api/domain/create/' + self.config['team_id'] + '/'
        data = {'name': self.config['domain']}
        return_data = self.send_post(url, data)
        if return_data['success']:
            return return_data['domain']['id']
        return False

    def get_team_id(self):
        url = self.url + '/api/team/list/'
        data = self.send_get(url)
        if data and 'teams' in data:
            for team in data['teams']:
                if 'team' not in self.config or team['name'].lower() == self.config['team'].lower():
                    self.config['team_id'] = team['id']
                    return

    def check_domain_exists(self, domain_name):
        if domain_name in self.domain_list:
            return True
        return False

    def get_domain_id(self, domain_name):
        if domain_name in self.domain_list:
            return self.domain_list[domain_name]

        return False

    def get_or_create_domain(self, domain_name):
        if self.check_domain_exists(domain_name):
            return self.get_domain_id(domain_name)
        else:
            self.get_team_id()
            self.config['domain'] = domain_name
            return self.add()


class Team(Basic):
    def __init__(self, config):
        super().__init__(config)
        self.selector()

    def list(self):
        url = self.url + '/api/team/list/'
        data = self.send_get(url)
        if data and 'teams' in data:
            for team in data['teams']:
                print(team['id'], team['name'])

    def add(self):
        url = self.url + '/api/team/list/'
        data = self.send_get(url)
        if data and 'teams' in data:
            for team in data['teams']:
                print(team['id'], team['name'])
