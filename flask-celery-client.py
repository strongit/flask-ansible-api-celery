#!/usr/bin/python
#coding:utf-8
import requests
import json
import argparse
ppm={'server-1': '1.1.1.1','server-2': '2.2.2.2'}

def tolist(fn):
    ips = []
    with open(fn) as f:
       for ip in f:
           ips.append(ip.strip())
    return ips

def run(target,action,ips,users):
    p = {'ips': ips, 'users': users }
    r = requests.post('http://{0}:5000/{1}'.format(ppm[target],action), data = p)
    gto = r.json()['goto']
    while 1:
       if requests.get("http://{0}:5000/{1}/result/{2}".format(ppm[target],action,gto)).json()['state'] == "PENDING":
          print "task running please wait........."
          time.sleep(1)
          continue
       else:
          print " "
          print "===============task running result=================="
          res=requests.get("http://{0}:5000/{1}/result/{2}".format(ppm[target],action,gto)).json()['status']
          for i in res:
              print i,str(res[i]).replace("u","")
          break

if __name__ == '__main__':
   parser = argparse.ArgumentParser()
   parser.add_argument('-i', '--ips', help='ips files')
   parser.add_argument('-u', '--users', help='uses files')
   parser.add_argument('-a', '--action', help='user manage action ex: add of del')
   parser.add_argument('-t', '--target', help='PPM IDC info  ex: server-1  server-2 ....')
   args = vars(parser.parse_args())
   if args['ips'] and args['users'] and args['action'] in ['add','del'] and args['target'] in ['server-1','server-2'] :
      ips=tolist(args['ips'])
      users=tolist(args['users'])
      run(args['target'],args['action'],ips,users)
   else:
      print parser.print_help()
