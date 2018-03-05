import os
from StatusCodeEnabledHandler import StatusCodeEnabledHandler
import SocketServer

PORT = 8000
DIR = "/opt/solr-multi-ping/"

Handler = StatusCodeEnabledHandler 
httpd = SocketServer.TCPServer(("", PORT), Handler)

os.chdir(DIR)
print "serving %s on port %d" % (DIR, PORT)
httpd.serve_forever()
