# 24dev-client.py
cli client for 24develop.com dns and certification api

### **Available Arguments**

| Argument | Type | Description | Default |
| --- | --- | --- | --- |
| --token | str | API token for authentication. | - |
| --url | str | API base URL. | - |
| --unit | str | A unit to operate on, e.g., team, domains, dns, ssl. | - |
| --domain | str | Domain name to act on. | - |
| --domain-id | str | ID associated with the domain name. | - |
| --team | str | Name of the team. | - |
| --team_id | str | ID of the team to use (defaults to the first team if not specified). | - |
| --action | str | Action to perform: list, add, delete, update, commit, export. | - |
| --config | str | Path to the configuration file. | - |
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

download ssl certificate
```bash
python script_name.py --token your_api_token --url https://api.example.com --unit ssl --action export \
    --cert-id cert123 --cert-folder-name /path/to/export/folder
```


## batch mode config driven deployment
create a config in yaml style like this, it will only add entrys, delete is not implemented yet.
```yaml
url: "https://www.24develop.com"
token: ""
certificate_base_folder: /tmp/data
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