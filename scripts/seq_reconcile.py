#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xmlrpclib
import time
import xml.dom.minidom
import base64
import oerplib
import argparse

#############################
### Constants Declaration ###
#############################

parser = argparse.ArgumentParser() 
parser.add_argument("-d", "--db", help="DataBase Name", required=True)
parser.add_argument("-r", "--user", help="OpenERP User", required=True)
parser.add_argument("-w", "--passwd", help="OpenERP Password", required=True)
parser.add_argument("-p", "--port", type=int, help="Port, 8069 for default", default="8069")
parser.add_argument("-s", "--server", help="Server IP, 127.0.0.1 for default", default="127.0.0.1")
args = parser.parse_args()

if( args.db is None or args.user is None or args.passwd is None):
    print "Must be specified DataBase, User and Password"
    quit()
    
db_name = args.db
user = args.user
passwd = args.passwd
server = args.server
port = args.port

conect = oerplib.OERP(
            server = server,
            database = db_name,
            port = port,
            )  

conect.login(user, passwd)
conect.config['timeout'] = 1000000

for company_id in conect.search('res.company',):
    moves_company_ids = conect.search('account.move.line', [('company_id', '=', company_id), '|', ('reconcile_id', '!=', False), ('reconcile_partial_id', '!=', False)])
    reconcile_moves = []
    for move in conect.read('account.move.line', moves_company_ids):
        reconcile_moves.append(move.get('reconcile_id', []) and move.get('reconcile_id', [])[0] or move.get('reconcile_partial_id', []) and move.get('reconcile_partial_id', [])[0])
    reconcile_ids = conect.search('account.move.reconcile', [('name', '=', '/'), ('id', 'in', reconcile_moves)])
    sequence_id = conect.search('ir.sequence', [('code', '=', 'account.reconcile'), ('company_id', '=', company_id)])
    if sequence_id:
        for move in reconcile_ids:
            next_sequence = conect.execute('ir.sequence', 'next_by_id', sequence_id[0])
            conect.write('account.move.reconcile', move, {'name': next_sequence},)
