#!/usr/bin/env python3

import argparse
import requests
import json

# -----------------------------------------------------------------------------

def get_check_by_name(auth, name):
    reqcheck = requests.get("https://api.pingdom.com/api/3.1/checks", 
        headers = {
            'Authorization': auth
        }
    )

    if reqcheck.status_code != 200:
        raise Exception('Request check failed. Response code is :{}'.format(reqcheck.status_code))
        return False

    obj = json.loads(reqcheck.text)

    if (name != 'all'): 

        for check in obj["checks"]:
            if check["name"] == name:
                return check
    
    
    else : 
        
        obj_out = json.dumps(obj)
        return obj_out
        
    return None

# -----------------------------------------------------------------------------

def create_check(auth, json_check):
   
    headers = {
        'Authorization' : auth,
        'Content-type': 'application/json',
        'Accept': 'text/plain'
    }

    reqcreate = requests.post(
        'https://api.pingdom.com/api/3.1/checks', 
        headers = headers,
        data = json.dumps(json_check)
    )

    if reqcreate.status_code == 200:
        print("Check has been created.")
        exit(0)
    raise Exception('Unexpected error, Return code to create check is :{}'.format(reqcreate.status_code))

# -----------------------------------------------------------------------------

def update_check(auth, checkid, json_check):

    json_check.pop("type")

    headers = {
        'Authorization' : auth,
        'Content-type': 'application/json'
    }

    requpdate = requests.put(
        'https://api.pingdom.com/api/3.1/checks/'+str(checkid),
        headers = headers,
        data = json_check
    )

    if requpdate.status_code == 200:
        print("Check has been updated.")
        exit(0)

    raise Exception('Unexpected error, Return code to update check is :{}'.format(requpdate.status_code))

# -----------------------------------------------------------------------------

def delete_check(auth, checkid):
    
    headers = {
        'Authorization' : auth
    }

    reqdelete = requests.delete(
        'https://api.pingdom.com/api/3.1/checks/'+str(checkid),
        headers = headers
    )

    if reqdelete.status_code == 200:
        print("Check has been deleted")

# -----------------------------------------------------------------------------

def args2json(args):
    
    json_check = {
        "name" : args.name,
        "host" : args.fqdn,
        "type" : "http",
        "encryption" : "true"
    }

    return json_check

# CLI Args mapping functions:
# -----------------------------------------------------------------------------

def set_check(args):
    # Verify if check already exists

    check = get_check_by_name(args.auth, args.name)
    json_check = args2json(args)

    if check == None:
    
        # It doesn't then let's create it
        create_check(args.auth, json_check)

    elif check != None:

        if check['hostname'] != args.fqdn:
          update_check(args.auth, check['id'], json_check)

        else:
            print('Check already exists ({}) and no update is needed '.format(check['id']))

# -----------------------------------------------------------------------------

def del_check(args):
    check = get_check_by_name(args.auth, args.name)
    
    if check == None:
        print("No existent check with name "+args.name+". Nothing to delete")

    else:
        delete_check(args.auth, check['id']) 

# -----------------------------------------------------------------------------

def get_check(args):

    print(get_check_by_name(args.auth, args.name))

# Main
# -----------------------------------------------------------------------------

def main ():
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(help='sub-command help')

    parser_set = subparser.add_parser('set', help='create or update a check')
    parser_set.set_defaults(func=set_check)

    parser_set.add_argument("-n", "--name", required=True, help="Name of the check", dest='name')
    parser_set.add_argument("-f", "--fqdn", required=True, help="FQDN to check", dest='fqdn')
    parser_set.add_argument("-a", "--auth", required=True, help="Auth for API", dest='auth')
    parser_set.add_argument("-r", "--resolution", default=5, help="Resolution of check (default = 5)", dest='resolution')

    parser_del = subparser.add_parser('delete', help='delete a check')
    parser_del.set_defaults(func=del_check)

    parser_del.add_argument("-a", "--auth", required=True, help="Auth for API", dest='auth')
    parser_del.add_argument("-n", "--name", required=True, help="Name of the check")

    parser_get = subparser.add_parser('get', help='get check')
    parser_get.set_defaults(func=get_check)

    parser_get.add_argument("-a", "--auth", required=True, help="Auth for API", dest='auth')
    parser_get.add_argument("-n", "--name", default="all", help="Name of the check")

    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        args.func(args)

    else:
        print("No subcommand found. please, use "+__file__+" --help for more infromation")
    
if __name__ == '__main__':
    main()
