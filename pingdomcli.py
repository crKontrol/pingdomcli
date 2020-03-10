#!/usr/bin/env python3

import argparse
import requests
import json
import datetime

# -----------------------------------------------------------------------------

def get_check_by_name(auth, name):
    reqcheck = requests.get("https://api.pingdom.com/api/3.1/checks", 
        headers = {
            'Authorization': 'Bearer ' + auth
        }
    )

    if reqcheck.status_code != 200:
        raise Exception('Request check failed. Response code is :{}'.format(reqcheck.status_code))
        return False

    obj = json.loads(reqcheck.text)

    if (name != 'all'): 

        for check in obj["checks"]:
            if check["name"] == name:
                check_out = json.dumps(check, indent=4)
                return check_out
    
    else : 
        
        obj_out = json.dumps(obj, indent=4)
        return obj_out
        
    return None


# -----------------------------------------------------------------------------

def get_teams_by_name(auth, name, idt):
    reqteams = requests.get("https://api.pingdom.com/api/3.1/alerting/teams",
        headers = {
            'Authorization': 'Bearer ' + auth
        }
    )

    if reqteams.status_code != 200:
        raise Exception('Request check failed. Response code is :{}'.format(reqteams.status_code))
        return False

    obj = json.loads(reqteams.text)

    if (name != 'all'):

        for team in obj["teams"]:
            if team["name"] == name:
                team_out = json.dumps(team, indent=4)
                return team_out
    
    elif (idt == "True"):
        
        idtms_out = []
        for idtms in obj["teams"]:
            if idtms is not None:
                idtms_out.append(idtms["id"])
        return idtms_out

    else :

        obj_out = json.dumps(obj, indent=4)
        return obj_out

    return None

# -----------------------------------------------------------------------------

def get_teams_by_id(auth, name):
    reqteams = requests.get("https://api.pingdom.com/api/3.1/alerting/teams",
        headers = {
            'Authorization': 'Bearer ' + auth
        }
    )

    if reqteams.status_code != 200:
        raise Exception('Request check failed. Response code is :{}'.format(reqteams.status_code))
        return False

    obj = json.loads(reqteams.text)

    if (name != 'all'):

        for team in obj["teams"]:
            if team["name"] == name:
                team_out = json.dumps(team["id"], indent=4)
                return team_out
    else :

        obj_out = []
        for team in obj["teams"]:
            obj_out.append(team["id"])
        return obj_out

    return None

# -----------------------------------------------------------------------------


def get_maintenances(auth):
    reqmnt = requests.get("https://api.pingdom.com/api/3.1/maintenance",
        headers = {
            'Authorization' : 'Bearer ' + auth
        }
    )
    
    if reqmnt.status_code != 200:
        raise Exception('Request check failed. Response code is :{}'.format(reqmnt.status_code))
        return False

    obj = json.loads(reqmnt.text)
    obj_out = json.dumps(obj, indent=4)

    return obj_out

# -----------------------------------------------------------------------------

def create_check(auth, json_check):
   
    headers = {
        'Authorization' : 'Bearer ' + auth,
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

def create_maintenance(auth, json_mnt):

    headers = {
        'Authorization' : 'Bearer ' + auth,
        'Content-type': 'application/json',
    }

    reqcreate = requests.post(
        'https://api.pingdom.com/api/3.1/maintenance',
        headers = headers,
        data = json.dumps(json_mnt)
    )

    if reqcreate.status_code == 200:
        print("Maintenance window has been created.")
        exit(0)
    raise Exception('Unexpected error, Return code to create maintenance window is :{}'.format(reqcreate.status_code))

# -----------------------------------------------------------------------------

def update_check(auth, checkid, json_check):

    json_check.pop("type")

    headers = {
        'Authorization' : 'Bearer ' + auth,
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
    print(requpdate)
    raise Exception('Unexpected error, Return code to update check is :{}'.format(requpdate.status_code))


# -----------------------------------------------------------------------------

def update_mnt(auth, mntid, json_mnt):

    headers = {
        'Authorization' : 'Bearer ' + auth,
        'Content-type': 'application/json'
    }

    requpdate = requests.put(
        'https://api.pingdom.com/api/3.1/maintenance/'+str(mntid),
        headers = headers,
        data = json_mnt
    )

    if requpdate.status_code == 200:
        print("Maintenance window has been updated.")
        exit(0)
    print(requpdate)
    raise Exception('Unexpected error, Return code to update maintenance window is :{}'.format(requpdate.status_code))


# -----------------------------------------------------------------------------

def delete_check(auth, checkid):
    
    headers = {
        'Authorization' : 'Bearer ' + auth
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
        "verify_certificate" : args.verify_certificate,
        "tags" : args.tags,
        "probe_filters" : "region: EU",
        "encryption" : "true"
    }

    return json_check


# -----------------------------------------------------------------------------

def args2json_mnt(args):

    json_mnt = {
        "desc" : args.desc,
        "from" : args.start,
        "to" : args.end,
        "uptimeids" : args.cid,
    }

    return json_mnt


# CLI Args mapping functions:
# -----------------------------------------------------------------------------

def set_check(args):
    # Verify if check already exists

    check = get_check_by_name(args.auth, args.name)
    json_check = args2json(args)

    if check is None:
    
        # It doesn't then let's create it
        create_check(args.auth, json_check)

    elif check is not None:

        checkout_json = json.loads(check)

        if checkout_json['hostname'] != args.fqdn:
            update_check(args.auth, checkout_json['id'], json_check)

        else:
            print('Check already exists ({}) and no update is needed '.format(checkout_json['id']))


# -----------------------------------------------------------------------------

def set_mnt(args):
    # Verify if check already exists

    mnt = get_maintenances(args.auth)
    json_check = args2json_mnt(args)

    if mnt is None:

        # It doesn't then let's create it
        create_maintenance(args.auth, json_check)

    elif mnt is not None:

        mnt_json = json.loads(mnt)

        if (mnt_json['from'] != args.start or mnt_json['to'] != args.end):
            update_mnt(args.auth, mnt_json['id'], json_mnt)

        else:
            print('Maintenance already exists ({}) and no update is needed '.format(mnt_json['id']))

# -----------------------------------------------------------------------------

def del_check(args):
    check = get_check_by_name(args.auth, args.name)
    checkout_json = json.loads(check)
    
    if check is None:
        print("No existent check with name "+args.name+". Nothing to delete")

    else:
        delete_check(args.auth, checkout_json['id']) 

# -----------------------------------------------------------------------------

def get_check(args):
    print(get_check_by_name(args.auth, args.name))

def get_teams(args):
    print(get_teams_by_name(args.auth, args.name, args.idt))

def get_maintenance(args):
    print(get_maintenances(args.auth))

def get_teams_id(args):
    print(get_teams_by_id(args.auth, args.name))


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
    parser_set.add_argument("-v", "--verify_certificate", default=True, help="Enable SSL certificate verification (default = True (yes))", dest='verify_certificate')
    parser_set.add_argument("-t", "--tags", required=True, help="Tags that must be set : env(prod, preprod, etc..), app(hybris, wp, etc...), site(intersport or rent)") 

    parser_del = subparser.add_parser('delete', help='delete a check')
    parser_del.set_defaults(func=del_check)
    parser_del.add_argument("-a", "--auth", required=True, help="Auth for API", dest='auth')
    parser_del.add_argument("-n", "--name", required=True, help="Name of the check")

    parser_get = subparser.add_parser('get', help='get check')
    parser_get.set_defaults(func=get_check)
    parser_get.add_argument("-a", "--auth", required=True, help="Auth for API", dest='auth')
    parser_get.add_argument("-n", "--name", default="all", help="Name of the check")
    
    parser_teams = subparser.add_parser('teams', help="get teams")
    parser_teams.add_argument("-a", "--auth", required=True, help="Auth for API", dest='auth')
    parser_teams.add_argument("-n", "--name", default="all", help="Name of the teams", dest='name')
    parser_teams.add_argument("-i", "--id", default=False, help="ID of the teams - None is nothing at the end of the list, ignore it!", dest='idt')
    parser_teams.set_defaults(func=get_teams)

    parser_id = subparser.add_parser('id_teams', help="get ID teams")
    parser_id.add_argument("-a", "--auth", required=True, help="Auth for API", dest='auth')
    parser_id.add_argument("-n", "--name", default="all", help="id of the teams by name", dest='name')
    parser_id.set_defaults(func=get_teams_id)

    parser_mnt = subparser.add_parser('maintenance', help="set/del maintenance windows")
    parser_mnt.add_argument("-a", "--auth", required=True, help="Auth for API", dest='auth')
    parser_mnt.add_argument("-d", "--desc", required=True, help="Description for maintenance windows", dest='desc')
    parser_mnt.add_argument("-s", "--start", required=True, default=1, help="Start time for maintenance - Beware, by default start time is NOW", dest='start')
    parser_mnt.add_argument("-e", "--end", required=True, help="End time for maintenance", dest='end')
    parser_mnt.add_argument("-i", "--id", help="Get maintenance by ID", dest="idm")
    parser_mnt.add_argument("-c", "--checks", help="ID of checks to put in maintenance", dest='cid')
    parser_mnt.add_argument("-r", "--remove", help="Delete maintenance windows - BE CAREFUL using IT - Can only delete future maintenance not current nor old ones", dest='del')
    parser_mnt.set_defaults(func=set_mnt)

    parser_get_mnt = subparser.add_parser('get_maintenance', help='get maintenance windows')
    parser_get_mnt.add_argument("-a", "--auth", required=True, help="Auth for API", dest='auth')
    parser_get_mnt.add_argument("-i", "--id", help="Get maintenance by ID", dest="idm")
    parser_get_mnt.set_defaults(func=get_maintenance)

    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        args.func(args)

    else:
        print("No subcommand found. please, use "+__file__+" --help for more infromation")
    
if __name__ == '__main__':
    main()
