from libs.basic import *


class Domain(Basic):
    domain_list = {}
    domain_is_needed = False

    def __init__(self, config):
        super().__init__(config)

    def list(self):
        url = self.url + '/api/domain/list/'
        data = self.send_get(url)
        print("list domains")
        if data and 'domains' in data:
            for domain in data['domains']:
                print(domain['id'], domain['name'])
                self.domain_list[domain['name']] = domain['id'].__str__()
                if domain.get('display_name'):
                    self.domain_list[domain['display_name']] = domain['id'].__str__()

    def add(self):
        if 'team_id' not in self.config or not self.config['team_id']:
            self.get_team_id()
        if 'team_id' not in self.config or not self.config['team_id']:
            print("no team found")
            return False
        url = self.url + '/api/domain/create/' + self.config['team_id'] + '/'
        data = {'name': self.config['domain']}
        if self.config.get('zone_file'):
            data['zone'] = self.read_zone_file()
            data['commit'] = bool(self.config.get('auto_commit'))
        return_data = self.send_post(url, data, log_data='zone' not in data)
        if return_data['success']:
            self.print_domain_status(return_data)
            return return_data['domain']['id']
        return False

    def import_zone(self):
        # soa records in the zone file are ignored by the server
        if not self.config.get('zone_file'):
            print("no zone file defined")
            return False
        domain_id = self.config.get('domain_id')
        if not domain_id and self.config.get('domain'):
            self.list()
            domain_id = self.get_domain_id()
        if not domain_id:
            print("domain not found")
            return False
        zone = self.read_zone_file()
        if not 10 <= len(zone) <= 65535:
            print("zone file must be between 10 and 65535 chars")
            return False
        url = self.url + '/api/domain/zone/' + domain_id + '/'
        data = {'zone': zone, 'commit': bool(self.config.get('auto_commit'))}
        # do not dump the whole zone file to the log
        return_data = self.send_post(url, data, log_data=False)
        if return_data['success']:
            self.print_domain_status(return_data)
        return return_data['success']

    def read_zone_file(self):
        with open(self.config['zone_file'], 'r') as f:
            return f.read()

    def print_domain_status(self, data):
        print(data['domain']['id'], data['domain']['name'], 'serial', data.get('serial'))
        for server, serial in (data.get('applied_serials') or {}).items():
            print(server, serial)
        # non fatal import problems
        self.print_errors(data)

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
            self.config['domain'] = domain_name
            return True
        return False

    def get_domain_id(self):
        if self.config['domain'] in self.domain_list:
            return self.domain_list[self.config['domain']]

        return False

    def get_or_create_domain(self, domain_name):
        if self.check_domain_exists(domain_name):
            return self.get_domain_id()
        else:
            self.get_team_id()
            self.config['domain'] = domain_name
            return self.add()
