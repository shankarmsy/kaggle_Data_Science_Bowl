"run vw with various bits settings, save reported losses to a csv file"
"subprocess.check_output() version"

import re, os
import csv
import subprocess
import collections
import sys

algo=raw_input('algo: ')
loss_function='logistic'
passes=raw_input('passes: ')
interactions = '-q ::' if raw_input('interactions: ')=='y' else ''
cv=raw_input('cv: ')

sys.stdout = open("hypsearch_log_cvday30{}".format(algo), "w")

# path_to_cache = 'data/vw/train.vw.cache'
trainfile='train.vw'
cvalfile=cv
predfile='vwpred{}.dat'.format(algo)
logfile='tmplogfile{}'.format(algo)
tunefile='vwhyper{}'.format(algo)
final_model='vw{}-cv30.vw'.format(algo)
final_trainfile='trainfinal.vw'
algo_parm='--ftrl' if algo=='ftrl' else ''

def define_params(algo):

    if algo=='nn':
        vw_params = {'-nn':10, 'l':10^10, '-l2':10^10,'-l1':10^10}
        ranges={'-nn':'5 20', 'l':'1e-10 20', '-l2':'1e-10 20',
                '-l1':'1e-10 10'}
        param_seq =['-nn','l', '-l2', '-l1']
        return vw_params, ranges, param_seq

    if algo=='logi':
        vw_params = {'l':10^10, '-l2':10^10,'-l1':10^10}
        ranges={'l':'1e-10 20', '-l2':'1e-10 20','-l1':'1e-10 10'}
        param_seq =['l', '-l2', '-l1']
        return vw_params, ranges, param_seq

    if algo=='ftrl':
        vw_params = {'-ftrl_alpha':10^10, '-ftrl_beta':10^10, '-l2':10^10,'-l1':10^10}
        ranges={'-ftrl_alpha':'-L 1e-10 10', '-ftrl_beta':'-L 1e-10 10','-l2':'1e-10 20',
                '-l1':'1e-10 10'}
        param_seq =['-ftrl_alpha','-ftrl_beta', '-l2', '-l1']
        return vw_params, ranges, param_seq

vw_params,ranges,param_seq=define_params(algo)

cmd_vw='''vw --loss_function {} --link logistic {} -b 24 -c {} --quiet --passes {} {}'''
cmd_vwh='vw-hypersearch -t {} '.format(cvalfile)

# o_f = open( output_file, 'wb' )
# writer=csv.writer(o_f)
# writer.writerow(['param', 'best_value', 'best_loss'])

print "CTR Prediction for Avazu\n"
print "Crossval on day 30, Train on rest"
print '-'*75

for iter,key in enumerate(param_seq):

    cmd=cmd_vw.format(loss_function, algo_parm, trainfile, passes, interactions)
    params=''

    for i,key in enumerate(param_seq):
        if vw_params[key] == 10^10:
            cmd=cmd_vwh + '{} '.format(ranges[key]) + cmd
            params=params + ' -{} %'.format(str(key))
            curkey = key
            break

        params+= ' -{} {}'.format(str(key),str(vw_params[key]))

    if '%' not in params:
        break

    cmd+=params+' -f {}{}'.format(tunefile,str(iter+1))

    print "Trying to optimize %s"%curkey
    print "Executing Command\n"
    print cmd

    os.system('{} 2>&1 | tee {}'.format(cmd, logfile))
    output=subprocess.check_output('tail -n 1 {}'.format(logfile),shell=True)
    vw_params[curkey], best_loss  = output.split('\t')
    best_loss = best_loss.split('\n')

    # writer.writerow([curkey, vw_params[curkey], best_loss])
    # o_f.flush()

    # print "\nFinished optimizing %s. best value %s, best loss %s\n" %(curkey, vw_params[curkey],  best_loss)

###Proceeding to Train Final Model
print "Best Parameters found with vw-hypersearch"
print '-'*75
print vw_params
print "\nReady to Train Final Model %s" %final_model
print '-'*75

cmd=cmd_vw.format(loss_function,  algo_parm, final_trainfile, passes, interactions)
params=''

for i,key in enumerate(vw_params):
    params+=' -{} {}'.format(str(key), str(vw_params[key]))

cmd+=params+' -f {}'.format(final_model)
os.system('{} 2>&1 | tee {}'.format(cmd, logfile))
print cmd
print "\nGenerating Predictions"
print '-'*75
cmd='vw test.vw -t -i {} -p {}'.format(final_model, predfile)
os.system('{} 2>&1 | tee {}'.format(cmd, logfile))
print cmd

print "\nModel Development Complete\n"
print "Final Trained Model with the Best Parameters at: %s" %final_model
print "Predictions on Test at: %s" %predfile
print 'Individual Trained models for each iteration at ' \
      '{}1,2...\n'.format(tunefile)

