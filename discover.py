from service import ServerFunctionCLI
from utils import shell_colors
import sys
import re

SERVER_COMMAND = "\n**** Invalid syntax ****\nFormat of server's commands\discover hostname\n"
DISCOVER_PATTERN = r"^discover.py\s[\w]+$"
command = " ".join(sys.argv)


if re.search(DISCOVER_PATTERN, command):    
  print(ServerFunctionCLI.DiscoverHostname(hostname=sys.argv[1]))
else:
  shell_colors.print_red(SERVER_COMMAND)