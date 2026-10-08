# 24dev-client.py
cli client for 24develop.com dns and certification api

### **Available Arguments**

| Argument | Type | Description | Default |
| --- | --- | --- | --- |
| --token | str | API token for authentication. | - |
| --secret | str | API token secret. If set, `ApiToken <token>:<secret>` is used, otherwise the legacy `Token <token>`. | - |
| --url | str | API base URL. | - |
| --unit | str | A unit to operate on, e.g., team, domains, dns, ssl. | - |
| --domain | str | Domain name to act on. | - |
| --domain-id | str | ID associated with the domain name. | - |
| --team | str | Name of the team. | - |
| --team_id | str | ID of the team to use (defaults to the first team if not specified). | - |
| --action | str | Action to perform: list, add, delete, update, commit, export, import. | - |
| --zone-file | str | BIND zone file for `--unit domain --action import` (or `add` to create the domain with a zone). | - |
| --auto-commit | N/A | Push the zone to the DNS servers after the change (domain add/import, dns add/update). | False |
| --config | str | Path to the configuration file. | - |
| --credentials | str | Path to the credentials file (url, token, secret). | - |
| --batch-mode | N/A | Use the configuration file in batch mode. | False |

### **DNS Record Arguments**
These arguments can be used for creating, updating, or managing DNS records.

| Argument | Type | Description | Default |
| --- | --- | --- | --- |
| --record-type | str | Record type: A, AAAA, TXT, MX, SRV, NS. | A |
| --record-name | str | Subdomain name (FQDN). | - |
| --record-ttl | str | Time to Live (TTL) for the record. | 600 |
| --record-content | str | Destination IP or domain name. | - |
| --record-prio | str | Priority for MX or SRV records. | - |
| --record-weight | str | Weight for SRV records only. | - |
| --record-port | str | Port for SRV records only. | - |
| --record-id | str | Record ID for updating or deleting records. | - |
| --record-description | str | Comment or description for the record. | - |


### **SSL Certificate Arguments**
These arguments are used for creating, exporting, or managing SSL certificates:

| Argument | Type | Description | Default |
| --- | --- | --- | --- |
| --cert-id | str | Certificate ID. | - |
| --cert-production | N/A | Use ACME production (instead of staging). | False |
| --cert-wildcard | N/A | Indicates if the certificate is a wildcard or not. | False |
| --cert-auto-renew | N/A | Enables or disables auto-renewal for the certificate. | False |
| --cert-subdomain | str | Subdomains to include in the certificate (must already exist in DNS if not a wildcard). Multiple values allowed. | - |
| --cert-folder-name | str | Folder path for exporting the certificate. | /tmp/certs |

## examples

create a dns entry
``` bash
python script_name.py --token your_api_token --url https://api.example.com --unit dns --action add \
    --domain example.com \
    --record-type A \
    --record-name sub.example.com \
    --record-ttl 300 \
    --record-content 192.168.1.1
```

import a zone file into an existing domain (SOA records in the file are ignored)
```bash
python script_name.py --credentials credentials.yml --unit domain --action import \
    --domain example.com --zone-file example.com.zone --auto-commit
```

download ssl certificate
```bash
python script_name.py --token your_api_token --url https://api.example.com --unit ssl --action export \
    --cert-id cert123 --cert-folder-name /path/to/export/folder
```


## config files
credentials and configuration are kept in two files, see `credentials.yml.dist` and `config.yml.dist`.
values are merged in this order, later ones win: credentials file, config file, cli arguments.

credentials file (keep it out of git, `credentials.yml` is in `.gitignore`)
```yaml
url: "https://www.24develop.com"
token: ""
secret: ""   # leave empty for a legacy token
```

## batch mode config driven deployment
create a config in yaml style like this, it will only add entrys, delete is not implemented yet.
```yaml
cert_base_folder: /opt/client/certs
domain:
  d.24develop.com:
    dns:
      - name: www
        type: A
        ttl: 60
        value:
          - 192.168.1.1
      - name: a
        type: CNAME
        value:
          - www.24develop.com
      - name: _sip._tcp
        type: SRV
        prio: 23
        weight: 29
        port: 5060
        value:
          - sip.24develop.com
      - name: "@"
        type: MX
        prio: 23
        value:
          - mail.24develop.com
      - name: berbel
        type: A
        ttl: 60
        value:
          - 1.2.3.4
      - name: berbel1
        type: A
        ttl: 60
        value:
          - 1.2.3.4
      - name: berbel2
        type: A
        ttl: 60
        value:
          - 1.2.3.4

    ssl:
      is_production: False
      is_auto_renew: False
      is_wildcard: False
      folder_name: 'www.24develop.de'
      subdomains:
        - www
```


### zone files in batch mode
a domain can import a BIND zone file on every run with `zone_file`. relative paths are relative to the config file.
the zone is imported before the `dns` entries are compared, so records from the zone are not added twice.
SOA records in the zone file are ignored, the SOA is managed by the server.
```yaml
domain:
  example.com:
    zone_file: zones/example.com.zone
    auto_commit: true   # push to the dns servers after the import, default true
    dns:
      - name: www
        type: A
        value:
          - 192.168.1.1
```
a zone file is only imported when it changed since the last successful import. the sha256 of each imported
zone file is stored in `zone_state.json` next to the config file, set `zone_state_file` to use another path.
delete the state file to force a new import of all zones. if the state file can not be written, a warning is
printed and the zones are imported on every run.

in docker mount the zone files next to the config, e.g. `./test/zones:/opt/client/config/zones:ro`.
the container user must be able to write the state file, see the docker compose setup.

## docker compose setup
the client runs as user and group id 33 (`www-data`) by default. it writes the certificates and the zone state file,
so the mounted folders must be writable by that id. to run as your own user set the ids in `.env`, see `.env.dist`
```bash
echo "CLIENT_UID=$(id -u)" > .env
echo "CLIENT_GID=$(id -g)" >> .env
```

```yaml
services:
  24develop-client:
    build:
      context: .
      dockerfile: docker/Dockerfile
      target: prod
    user: "${CLIENT_UID:-33}:${CLIENT_GID:-33}"
    command: python 24dev-client.py --credentials /opt/client/config/credentials.yml --config /opt/client/config/config.yml --batch-mode
    volumes:
      - ./certs:/opt/client/certs
      - ./test/credentials.yml:/opt/client/config/credentials.yml:ro
      - ./test/workconfig.yml:/opt/client/config/config.yml
    logging:
      driver: "json-file"
      options:
        max-size: "10m"    # Maximum size of a log file (10 MB in this case)
        max-file: "3"      # Maximum number of log files to keep
```