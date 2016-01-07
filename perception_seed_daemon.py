from lib.get_from_core import get_network_info
from lib.ios_output_parser import local_hosts, local_connections, cdp_neighbors_detail, ios_fqdn_detail
from lib.openvas import setup_openvas
from shutil import rmtree as rmtree
from time import sleep
from sqlalchemy.exc import ProgrammingError
from models.db_tables import OpenvasAdmin
from lib.db_connector import connect

tmp_dir = '/tmp/perception'
ios_show_hosts_file = '%s/ios_show_hosts.txt' % tmp_dir
ios_show_local_conn_file = '%s/show_local_conn.txt' % tmp_dir
ios_show_cdp_detail_file = '%s/show_cdp_detail.txt' % tmp_dir
ios_show_fqdn_file = '%s/ios_show_fqdn.txt' % tmp_dir

"""Connect to the database"""
Session = connect()
session = Session()


def main():
  while True:

    # verify openvas is configured
    openvas_user = session.query(OpenvasAdmin).first()

    if not openvas_user:  # if it's not configured
      setup_openvas()     # configured it

    try:

      # get info from core, save in tmp/perception/
      get_network_info(tmp_dir,  # ssh to Cisco IOS core switch
                       ios_show_hosts_file,
                       ios_show_local_conn_file,
                       ios_show_cdp_detail_file,
                       ios_show_fqdn_file)

      # parse the local hosts file from /tmp/perception
      local_hosts(ios_show_hosts_file)  # this function also removes stale hosts from inventory

      # parse the local connections file from /tmp/perception
      local_connections(ios_show_local_conn_file)

      # parse the ios fqdn file from /tmp/perception
      ios_fqdn = ios_fqdn_detail(ios_show_fqdn_file)

      # parse the cdp detail file from /tmp/perception
      cdp_neighbors_detail(ios_show_cdp_detail_file, ios_fqdn)

      try:
        rmtree(tmp_dir)
      except FileNotFoundError as e:
        print(e)

    except ProgrammingError:
      print('database not ready')

    print('sleeping')
    sleep(300)


if __name__ == '__main__':
  try:
    main()
  except (IOError, SystemExit):
    raise
  except KeyboardInterrupt:
    print('Crtl+C Pressed. Shutting down.')
