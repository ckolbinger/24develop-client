from libs.basic import *


class Domain(Basic):
    domain_list = {}
    domain_is_needed = True

    def __init__(self, config):
        super().__init__(config)
        self.selector()

    def list(self):
        url = self.url + '/api/domain/list/'
        data = self.send_get(url)
        print("list domains")
        if data and 'domains' in data:
            for domain in data['domains']:
                print(domain['id'], domain['name'])
                self.domain_list[domain['name']] = domain['id'].__str__()

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
