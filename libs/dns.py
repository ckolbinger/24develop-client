from libs.basic import *


class Dns(Basic):
    domain_id = None
    record_id = None
    domain_records = {}
    domain_is_needed = True

    def __init__(self, config):
        super().__init__(config)
        if 'domain_id' not in config or not config['domain_id']:
            print("get domains")
            if not self.get_domain_id():
                print("domain not found")
                return

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
        print("list records")
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


