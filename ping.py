from service import ServerFunctionCLI
from utils import shell_colors
import sys
import re
PING_PATTERN = r"^ping.py\s[\w]+$"
SERVER_COMMAND = "\n**** Invalid syntax ****\nFormat of server's commands\nping hostname\n"
command = " ".join(sys.argv)
if re.search(PING_PATTERN, command):
  print(ServerFunctionCLI.PingHostname(hostname=sys.argv[1]))
else:
  shell_colors.print_red(SERVER_COMMAND)