from libs.basic import *

class Team(Basic):
    domain_is_needed = False
    def __init__(self, config):
        super().__init__(config)
        self.selector()

    def list(self):
        url = self.url + '/api/team/list/'
        data = self.send_get(url)
        print("list teams")
        if data and 'teams' in data:
            for team in data['teams']:
                print(team['id'], team['name'])

    def add(self):
        url = self.url + '/api/team/list/'
        data = self.send_get(url)
        if data and 'teams' in data:
            for team in data['teams']:
                print(team['id'], team['name'])
