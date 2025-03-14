import argparse
import yaml
from libs.workfile import *


def main():
    # Create the ArgumentParser object
    parser = argparse.ArgumentParser(description="CLI argument parsing example using argparse.")
    parser.add_argument("--token", type=str, help="api token")  # Add arguments
    parser.add_argument("--url", type=str, help="api token")  # Add arguments
    parser.add_argument("--unit", type=str, help="unit: team,domains,dns,ssl")
    parser.add_argument("--domain", type=str, help="domain name")
    parser.add_argument("--domain-id", type=str, help="id of domain name")
    parser.add_argument("--team", type=str, help="team name")
    parser.add_argument("--team_id", type=str, help="team id to use, first team if not specified")
    parser.add_argument("--action", type=str, help="action list,add,delete,update,commit,export")
    parser.add_argument("--config", type=str, help="config file")
    parser.add_argument("--batch-mode", action="store_true", help="use the config file in batch mode")
    parser.add_argument("--record-type", type=str, help="A,AAAA,TXT,MX,SRV,NS", default="A")
    parser.add_argument("--record-name", type=str, help="subdomain name fqdn")
    parser.add_argument("--record-ttl", type=str, help="subdomain name fqdn", default=600)
    parser.add_argument("--record-content", type=str, help="destination ip or domain")
    parser.add_argument("--record-prio", type=str, help="prio MX or SRV")
    parser.add_argument("--record-weight", type=str, help="weight SRV only")
    parser.add_argument("--record-port", type=str, help="port SRV only")
    parser.add_argument("--record-id", type=str, help="for update or delete")
    parser.add_argument("--record-description", type=str, help="comment for record")
    parser.add_argument("--cert-id", type=str, help="cert id")
    parser.add_argument("--cert-production", action="store_true", help="cert acme staging or production")
    parser.add_argument("--cert-wildcard", action="store_true", help="cert wildcard or not")
    parser.add_argument("--cert-auto-renew", action="store_true", help="cert auto renew or not")
    parser.add_argument("--cert-subdomain", type=str, nargs="+",
                        help="cert subdomain must exist in the dns only if not wildcard")
    parser.add_argument("--cert-folder-name", type=str, help="cert folder name for export",default=None)
    parser.add_argument("--cert-base-folder", type=str, help="cert folder name for export", default=None)
    parser.add_argument("--disable-ssl-verify", action="store_true", help="disable ssl verify for https requests")

    # Parse the arguments
    args = parser.parse_args()
    config = {}
    work_config = {}
    if "config" in args and args.config:
        config = read_config(args.config)

    for arg in vars(args):
        if getattr(args, arg):
            config[arg] = getattr(args, arg)

    if not args.batch_mode:
        if args.unit == "team":
            my_team = Team(config)
            my_team.run()
        elif args.unit == "domain":
            my_domain = Domain(config)
            my_domain.run()
        elif args.unit == "dns":
            my_dns = Dns(config)
            my_dns.run()
        elif args.unit == "ssl":
            my_ssl = MySsl(config)
            my_ssl.run()
    else:
        work_file_client = Workfile(config)
        if work_file_client.start_work_script():
            print("work script done")


def read_config(config_file):
    with open(config_file, "r") as file:
        config = yaml.safe_load(file)  # Load safely to avoid exploits
    return config


if __name__ == "__main__":
    main()
