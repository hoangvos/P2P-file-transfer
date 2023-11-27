from service import ServerFunctionCLI
from utils import shell_colors
from service.Server import PING_PATTERN
import sys
import re
SERVER_COMMAND = "\n**** Invalid syntax ****\nFormat of server's commands\n ping hostname\n"
command = " ".join(sys.argv)
if re.search(PING_PATTERN, command):
  print(ServerFunctionCLI.PingHostname(hostname=sys.argv[1]))
else:
  shell_colors.print_red(SERVER_COMMAND)