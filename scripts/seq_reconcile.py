#!/usr/bin/env python
# -*- coding: utf-8 -*-
import oerplib
from vauxootools.vauxootools import VauxooToolsServers

class UpdateSeqReconcile(object):
    
    def update_name_reconcile(sale, args):
    
        hostname = args.get_hostname()
        dbname = args.get_db()
        port = args.get_port()
        user = args.get_user()
        pwd = args.get_pwd()

        conect = oerplib.OERP(
                    hostname,
                    port=port,
                    )  

        conect.login(user, pwd, dbname)
        conect.config['timeout'] = 1000000

        for company_id in conect.search('res.company',[]):
            moves_company_ids = conect.search('account.move.line', 
                    [('company_id', '=', company_id), '|',
                    ('reconcile_id', '!=', False),
                    ('reconcile_partial_id', '!=', False)])
            reconcile_moves = []
            
            sequence_id = conect.search('ir.sequence',
                    [('code', '=', 'account.reconcile'),
                    ('company_id', '=', company_id)])
                     
            if sequence_id:
                for move in conect.browse('account.move.line', moves_company_ids):
                    reconcile_moves.append(move.reconcile_id and\
                    move.reconcile_id.id or\
                    move.reconcile_partial_id and\
                    move.reconcile_partial_id.id)
                        
                reconcile_ids = conect.search('account.move.reconcile',
                        [('name', '=', '/'), ('id', 'in', reconcile_moves)])
                        
                for move in reconcile_ids:
                    next_sequence = conect.execute('ir.sequence', 'next_by_id', sequence_id[0])
                    conect.write('account.move.reconcile', move, {'name': next_sequence},)
        return True

if __name__ == '__main__':

    configuration = VauxooToolsServers(app_name='seq_reconcile_move',
                                       usage_message="Created by VauxooTools",
                                       options=['dbname', 'hostname',
                                                'password', 'port',
                                                'username',],
                                       log=True)
    
    seq_req = UpdateSeqReconcile()
    seq_req.update_name_reconcile(configuration)
