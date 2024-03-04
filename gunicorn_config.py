bind = "unix:/python/panipat-deploy/ecomproj.sock"
workers = 3
chdir = "/python/panipat-deploy/"
module = "ecomproj.wsgi:application"
user = "root"
group = "root"

