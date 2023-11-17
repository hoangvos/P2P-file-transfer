from service import ServerFunctionCLI
from utils import shell_colors
import sys


print(ServerFunctionCLI.DiscoverHostname(hostname=sys.argv[1]))