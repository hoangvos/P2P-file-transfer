from service import ServerFunctionCLI
from utils import shell_colors
import sys


print(ServerFunctionCLI.PingHostname(hostname=sys.argv[1]))