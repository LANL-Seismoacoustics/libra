"""
Brady Spears
8/17/25

Contains a global dictionary containing the NNSA KB Core schema.
"""

KBCORE_DICT = {
    'NNSA KB Core' : {
    'description' : 'National Nuclear Security Administration Knowledge Base Core',
    'columns' : {
        'algorithm' : {'sa_coltype' : 'String(15)', 'default' : '-', 'info' : "{'format' : '15.15s', 'max_length' : 15}"},
        'amp' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-1.', 'info' : "{'format' : '11.2f', 'gt' : 0.}"},
        'ampid' : {'sa_coltype' : 'Integer', 'default' : '-1', 'info' : "{'format' : '9d', 'gt' : 0}"},
        'amptime' : {'sa_coltype' : 'Float(precision=53)', 'default' : '-9999999999.999', 'info' : "{'format' : '17.5f', 'ge' : -9999999999.999}"},
        'amptype' : {'sa_coltype' : 'String(8)', 'default' : '-', 'info' : "{'format' : '8.8s', 'max_length' : 8}"},
        'arid' : {'sa_coltype' : 'Integer', 'default' : '-1', 'info' : "{'format' : '9d', 'gt' : 0}"},
        'auth' : {'sa_coltype' : 'String(20)', 'default' : '-', 'info' : "{'format' : '20.20s', 'max_length' : 20}"},
        'azdef' : {'sa_coltype' : 'String(1)', 'default' : '-', 'info' : "{'format' : '1.1s', 'max_length' : 1, 'options' : ['d','n']}"},
        'azimuth' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-1.', 'info' : "{'format' : '7.2f', 'range_in' : [0., 360.]}"},
        'azres' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-999.', 'info' : "{'format' : '7.1f', 'range_in' : [-180., 180.]}"},
        'band' : {'sa_coltype' : 'String(1)', 'default' : '-', 'info' : "{'format' : '1.1s', 'max_length' : 1, 'options' : ['s','m','i','l','b','h','v','e','r','u','w']}"},
        'belief' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-1.', 'info' : "{'format' : '4.2f', 'range_in' : [0., 1.]}"},
        'calib' : {'sa_coltype' : 'Float(precision=24)', 'default' : '1.', 'info' : "{'format' : '16.6f', 'gt' : 0}"},
        'calper' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-1.', 'info' : "{'format' : '16.6f', 'gt' : 0}"},
        'calratio' : {'sa_coltype' : 'Float(precision=24)', 'default' : '1.', 'info' : "{'format' : '16.6f', 'gt' : 0}"},
        'chan' : {'sa_coltype' : 'String(8)', 'default' : '-', 'info' : "{'format' : '8.8s', 'regex' : r'[\w\-\.\*]+$', 'max_length' : 8}"},
        'chanid' : {'sa_coltype' : 'Integer', 'default' : '-1', 'info' : "{'format' : '8d', 'gt' : 0}"},
        'clip' : {'sa_coltype' : 'String(1)', 'default' : '-', 'info' : "{'format' : '1.1s', 'max_length' : 1, 'options' : ['c','n']}"},
        'commid' : {'sa_coltype' : 'Integer', 'default' : '-1', 'info' : "{'format' : '9d', 'gt' : 0}"},
        'conf' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-1.', 'info' : "{'format' : '5.2f', 'range_in' : [0.5, 1.]}"},
        'ctype' : {'sa_coltype' : 'String(4)', 'default' : '-', 'info' : "{'format' : '4.4s', 'max_length' : 4, 'options' : ['n','b','i']}"},
        'datatype' : {'sa_coltype' : 'String(2)', 'default' : '-', 'info' : "{'format' : '2.2s', 'max_length' : 2, 'options' : ['a0','b0','c0','a#','b#','c#','t4','t8','s4','s2','s3','f4','f8','i4','i2','e1','e#','g2']}"},
        'deast' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-99999.', 'info' : "{'format' : '9.4f', 'range_in' : [-20000.,20000.]}"}, 
        'delaz' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-1.', 'info' : "{'format' : '7.2f', 'range_in' : [0.,180.]}"},
        'delslo' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-1.', 'info' : "{'format' : '7.2f', 'range_in' : [0.,400.]}"}, 
        'delta' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-1.', 'info' : "{'format' : '8.3f', 'range_in' : [0., 1800.]}"},
        'deltaf' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-1.', 'info' : "{'format' : '7.3f', 'gt' : 0.}"},
        'deltim' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-1.', 'info' : "{'format' : '6.3f', 'range_ex' : [0., 3600.]}"},
        'depdp' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-999.', 'info' : "{'format' : '9.4f', 'range_in' : [0., 750.]}"},
        'depth' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-999.', 'info' : "{'format' : '9.4f', 'range_in' : [-100., 750.]}"},
        'descrip' : {'sa_coltype' : 'String(50)', 'default' : '-', 'info' : "{'format' : '50.50s', 'max_length' : 50}"},
        'dfile' : {'sa_coltype' : 'String(32)', 'default' : '-', 'info' : "{'format' : '32.32s', 'max_length' : 32}"},
        'digital' : {'sa_coltype' : 'String(1)', 'default' : '-', 'info' : "{'format' : '1.1s', 'max_length' : 1, 'options' : ['d','a']}"},
        'dir' : {'sa_coltype' : 'String(64)', 'default' : '-', 'info' : "{'format' : '64.64s', 'max_length' : 64}"},
        'dnorth' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-99999.', 'info' : "{'format' : '9.4f', 'range_in' : [-20000.,20000.]}"},
        'dtype' : {'sa_coltype' : 'String(1)', 'default' : '-', 'info' : "{'format' : '1.1s', 'max_length' : 1, 'options' : ['A','D','F','N','L','P','G','Q','B','W','f','d','r','g','q','w','-']}"},
        'duration' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-1.', 'info' : "{'format' : '7.2f', 'gt' : 0.}"},
        'edepth' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-1.', 'info' : "{'format' : '9.4f', 'range_in' : [0., 10.]}"},
        'elev' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-999.', 'info' : "{'format' : '9.4f', 'range_in' : [-10.,10.]}"},
        'ema' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-1.', 'info' : "{'format' : '7.2f', 'range_in' : [0.,90.]}"},
        'emares' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-999.', 'info' : "{'format' : '7.1f', 'range_in' : [-90.,90.]}"},
        'endtime' : {'sa_coltype' : 'Float(precision=53)', 'default' : '9999999999.999', 'info' : "{'format' : '17.5f', 'range_ex' : [-9999999999.999,9999999999.999]}"},
        'esaz' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-1.', 'info' : "{'format' : '7.2f', 'range_in' : [0.,360.]}"},
        'etype' : {'sa_coltype' : 'String(7)', 'default' : '-', 'info' : "{'format' : '7.7s', 'max_length' : 7, 'options' : ['ex','ec','ep','en','mc','me','mp','mb','qt','qd','qp','qf','qm','qh','qv','q2','q4','qa','l','r','t','ge','xm','xl','xo','-']}"},
        'evid' : {'sa_coltype' : 'Integer', 'default' : '-1', 'info' : "{'format' : '9d', 'gt' : 0}"},
        'evname' : {'sa_coltype' : 'String(32)', 'default' : '-', 'info' : "{'format' : '32.32s', 'max_length' : 32}"},
        'fm' : {'sa_coltype' : 'String(2)', 'default' : '-', 'info' : "{'format' : '2.2s', 'max_length' : 2, 'options' : ['..','.r','.u','c.','cr','cu','d.','dr','du']}"},
        'foff' : {'sa_coltype' : 'Integer', 'default' : '-1', 'info' : "{'format' : '10d', 'range_in' : [0,100000000000]}"},
        'grn' : {'sa_coltype' : 'Integer', 'default' : '-1', 'info' : "{'format' : '8d', 'range_in' : [1,757]}"},
        'grname' : {'sa_coltype' : 'String(40)', 'default' : '-', 'info' : "{'format' : '40.40s', 'max_length' : 40}"},
        'hang' : {'sa_coltype' : 'Float(24)', 'default' : '-1.', 'info' : "{'format' : '6.1s', 'range_in' : [0.,360.]}"},
        'inarrival' : {'sa_coltype' : 'String(1)', 'default' : '-', 'info' : "{'format' : '1.1s', 'max_length' : 1, 'options' : ['y','n']}"},
        'inid' : {'sa_coltype' : 'Integer', 'default' : '-1', 'info' : "{'format' : '8d', 'gt' : 0}"},
        'insname' : {'sa_coltype' : 'String(50)', 'default' : '-', 'info' : "{'format' : '50.50s', 'max_length' : 50}"},
        'instant' : {'sa_coltype' : 'String(1)', 'default' : '-', 'info' : "{'format' : '1.1s', 'max_length' : 1, 'options' : ['y','n']}"},
        'instype' : {'sa_coltype' : 'String(6)', 'default' : '-', 'info' : "{'format' : '6.6s', 'max_length' : 6}"},
        'iphase' : {'sa_coltype' : 'String(8)', 'default' : '-', 'info' : "{'format' : '8.8s', 'max_length' : 8}"},
        'jdate' : {'sa_coltype' : 'Integer', 'default' : '-1', 'info' : "{'format' : '8d'}"},
        'keyname' : {'sa_coltype' : 'String(15)', 'default' : '-', 'info' : "{'format' : '15.15s'}"},
        'keyvalue' : {'sa_coltype' : 'Integer', 'default' : '-1', 'info' : "{'format' : '9d', 'gt' : 0}"},
        'lat' : {'sa_coltype' : 'Float(precision=53)', 'default' : '-999.', 'info' : "{'format' : '11.6f', 'range_in' : [-90.,90.]}"},
        'lddate' : {'sa_coltype' : 'DateTime', 'nullable' : 'False', 'onupdate' : 'datetime.now(timezone.utc)', 'default' : 'datetime.now(timezone.utc)', 'info' : "{'format' : '%Y-%m-%d %H:%M:%S'}"},
        'lineno' : {'sa_coltype' : 'Integer', 'default' : '-1', 'info' : "{'format' : '8d', 'range_ex' : [0, 1000]}"},
        'logat' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-999.', 'info' : "{'format' : '7.2f', 'gt' : -4}"},
        'lon' : {'sa_coltype' : 'Float(precision=53)', 'default' : '-999.', 'info' : "{'format' : '11.6f', 'range_in' : [-180.,180.]}"},
        'magdef' : {'sa_coltype' : 'String(1)', 'default' : '-', 'info' : "{'format' : '1.1s', 'max_length' : 1, 'options' : ['d','n']}"},
        'magid' : {'sa_coltype' : 'Integer', 'default' : '-1', 'info' : "{'format' : '9d', 'gt' : 0}"},
        'magnitude' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-999.', 'info' : "{'format' : '7.2f', 'range_ex' : [-5.,10.]}"},
        'magres' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-999.', 'info' : "{'format' : '7.2f', 'range_ex' : [-4.,4.]}"},
        'magtype' : {'sa_coltype' : 'String(6)', 'default' : '-', 'info' : "{'format' : '6.6s', 'max_length' : 6}"},
        'mb' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-999.', 'info' : "{'format' : '7.2f', 'range_ex' : [-5.,10.]}"},
        'mbid' : {'sa_coltype' : 'Integer', 'default' : '-1', 'info' : "{'format' : '9d', 'gt' : 0}"},
        'ml' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-999.', 'info' : "{'format' : '7.2f', 'range_ex' : [-5.,10.]}"},
        'mlid' : {'sa_coltype' : 'Integer', 'default' : '-1', 'info' : "{'format' : '9d', 'gt' : 0}"},
        'mmodel' : {'sa_coltype' : 'String(15)', 'default' : '-', 'info' : "{'format' : '15.15s', 'max_length' : 15}"},
        'ms' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-999.', 'info' : "{'format' : '7.2f', 'range_ex' : [-5.,10.]}"},
        'msid' : {'sa_coltype' : 'Integer', 'default' : '-1', 'info' : "{'format' : '9d', 'gt' : 0}"},
        'nass' : {'sa_coltype' : 'Integer', 'default' : '-1', 'info' : "{'format' : '4d', 'range_ex' : [0,10000]}"},
        'ncalib' : {'sa_coltype' : 'Float(precision=24)', 'default' : '1.', 'info' : "{'format' : '16.6f', 'nequal' : 0}"},
        'ncalper' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-1.', 'info' : "{'format' : '16.6f', 'range_ex' : [.000001,3600.]}"},
        'ndef' : {'sa_coltype' : 'Integer', 'default' : '-1', 'info' : "{'format' : '4d', 'range_ex' : [0,10000]}"}, 
        'ndp' : {'sa_coltype' : 'Integer', 'default' : '-1', 'info' : "{'format' : '4d', 'range_in' : [0,10000]}"},
        'net' : {'sa_coltype' : 'String(8)', 'default' : '-', 'info' : "{'format' : '8.8s', 'max_length' : 8, 'regex' : r'^[A-Z0-9][A-Z0-9:\-\+_]*$'}"},
        'netname' : {'sa_coltype' : 'String(80)', 'default' : '-', 'info' : "{'format' : '80.80s', 'max_length' : 80}"},
        'nettype' : {'sa_coltype' : 'String(4)', 'default' : '-', 'info' : "{'format' : '4.4s', 'max_length' : 4}"},
        'nsamp' : {'sa_coltype' : 'Integer', 'default' : '-1', 'info' : "{'format' : '8d', 'range_ex' : [0,100000000]}"},
        'nsta' : {'sa_coltype' : 'Integer', 'default' : '-1', 'info' : "{'format' : '8d', 'range_in' : [0, 10000]}"},
        'offdate' : {'sa_coltype' : 'Integer', 'default' : '2286324', 'info' : "{'format' : '8d'}"},
        'ondate' : {'sa_coltype' : 'Integer', 'default' : '-1', 'info' : "{'format' : '8d'}"},
        'orid' : {'sa_coltype' : 'Integer', 'default' : '-1', 'info' : "{'format' : '9d', 'gt' : 0}"},
        'parid' : {'sa_coltype' : 'Integer', 'default' : '-1', 'info' : "{'format' : '9d', 'gt' : 0}"},
        'per' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-1.', 'info' : "{'format' : '7.2f', 'range_ex' : [0.,3600.]}"},
        'phase' : {'sa_coltype' : 'String(8)', 'default' : '-', 'info' : "{'format' : '8.8s', 'max_length' : 8}"},
        'prefor' : {'sa_coltype' : 'Integer', 'default' : '-1', 'info' : "{'format' : '9d', 'gt' : 0}"},
        'qual' : {'sa_coltype' : 'String(1)', 'default' : '-', 'info' : "{'format' : '1.1s', 'options' : ['i','e','w','1','2','3','4','A','B','C','D','F','q']}"},
        'rect' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-1.', 'info' : "{'format' : '7.3f', 'range_in' : [0.,1.]}"},
        'refsta' : {'sa_coltype' : 'String(6)', 'default' : '-', 'info' : "{'format' : '6.6s', 'max_length' : 6, 'regex' : r'^[A-Z0-9\-][A-Z0-9x\-\*+]+$'}"},
        'remark' : {'sa_coltype' : 'String(80)', 'default' : '-', 'info' : "{'format' : '80.80s', 'max_length' : 80}"},
        'rsptype' : {'sa_coltype' : 'String(6)', 'default' : '-', 'info' : "{'format' : '6.6s', 'max_length' : 6}"},
        'samprate' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-1.', 'info' : "{'format' : '11.7f', 'range_in' : [.001,100000.]}"},
        'sdepth' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-1.', 'info' : "{'format' : '9.4f', 'range_in' : [0.,750.]}"},
        'sdobs' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-1.', 'info' : "{'format' : '9.4f', 'ge' : 0.}"},
        'seaz' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-1.', 'info' : "{'format' : '7.2f', 'range_in' : [0.,360.]}"},
        'segtype' : {'sa_coltype' : 'String(1)', 'default' : '-', 'info' : "{'format' : '1.1s', 'max_length' : 1, 'options' : ['o','v','s','d','c','f','g','A','V','D','n','t','u','x']}"},
        'slodef' : {'sa_coltype' : 'String(1)', 'default' : '-', 'info' : "{'format' : '1.1s', 'max_length' : 1, 'options' : ['d','n']}"},
        'slores' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-999.', 'info' : "{'format' : '7.2f', 'range_in' : [-400.,400.]}"},
        'slow' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-1.', 'info' : "{'format' : '7.2f', 'range_in' : [0.,400.]}"},
        'smajax' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-1.', 'info' : "{'format' : '9.4f', 'range_in' : [0.,20000.]}"},
        'sminax' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-1.', 'info' : "{'format' : '9.4f', 'range_in' : [0.,20000.]}"},
        'snr' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-1.', 'info' : "{'format' : '10.2f', 'gt' : 0}"},
        'srn' : {'sa_coltype' : 'Integer', 'default' : '-1', 'info' : "{'format' : '8d', 'range_in' : [1,50]}"},
        'srname' : {'sa_coltype' : 'String(40)', 'default' : '-', 'info' : "{'format' : '40.40s', 'max_length' : 40}"},
        'sta' : {'sa_coltype' : 'String(6)', 'default' : '-', 'info' : "{'format' : '6.6s', 'max_length' : 6, 'regex' : r'^[A-Z0-9\-][A-Z0-9x\-\*+]+$'}"},
        'staname' : {'sa_coltype' : 'String(50)', 'default' : '-', 'info' : "{'format' : '50.50s', 'max_length' : 50}"},
        'stassid' : {'sa_coltype' : 'Integer', 'default' : '-1', 'info' : "{'format' : '9d', 'gt' : 0}"},
        'statype' : {'sa_coltype' : 'String(4)', 'default' : '-', 'info' : "{'format' : '4.4s', 'max_length' : 4, 'options' : ['ss','ar']}"},
        'stime' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-1.', 'info' : "{'format' : '6.3f', 'range_in' : [0.,3600.]}"},
        'strike' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-1.', 'info' : "{'format' : '6.2f', 'range_in' : [0.,360.]}"},
        'stt' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-100000000.', 'info' : "{'format' : '15.4', 'ge' : 0}"},
        'stx' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-100000000.', 'info' : "{'format' : '15.4', 'ge' : -999.}"},
        'sty' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-100000000.', 'info' : "{'format' : '15.4', 'ge' : -999.}"},
        'stype' : {'sa_coltype' : 'String(1)', 'default' : '-', 'info' : "{'format' : '1.1s', 'max_length' : 1, 'options' : ['l','r','t','m','g','c']}"},
        'stz' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-100000000.', 'info' : "{'format' : '15.4', 'ge' : -999.}"},
        'sxx' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-100000000.', 'info' : "{'format' : '15.4', 'ge' : 0}"},
        'sxy' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-100000000.', 'info' : "{'format' : '15.4', 'ge' : -999.}"},
        'sxz' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-100000000.', 'info' : "{'format' : '15.4', 'ge' : -999.}"},
        'syy' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-100000000.', 'info' : "{'format' : '15.4', 'ge' : 0}"},
        'syz' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-100000000.', 'info' : "{'format' : '15.4', 'ge' : -999.}"},
        'szz' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-100000000.', 'info' : "{'format' : '15.4', 'ge' : 0}"},
        'tagid' : {'sa_coltype' : 'Integer', 'default' : '-1', 'info' : "{'format' : '9d', 'gt' : 0}"},
        'tagname' : {'sa_coltype' : 'String(8)', 'default' : '-', 'info' : "{'format' : '8.8s', 'max_length' : 8, 'options' : ['arid','evid','orid','stassid']}"},
        'time' : {'sa_coltype' : 'Float(precision=53)', 'default' : '-9999999999.999', 'info' : "{'format' : '17.5f', 'gt' : -9999999999.999}"},
        'timedef' : {'sa_coltype' : 'String(1)', 'default' : '-', 'info' : "{'format' : '1.1s', 'max_length' : 1, 'options' : ['n','d']}"},
        'timeres' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-999.', 'info' : "{'format' : '8.3f', 'gt' : -999.}"},
        'tshift' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-100000000.', 'info' : "{'format' : '16.2f', 'range_ex' : [-999.,999.]}"},
        'uncertainty' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-1.', 'info' : "{'format' : '7.2f', 'range_in' : [0.,2.]}"},
        'units' : {'sa_coltype' : 'String(15)', 'default' : '-', 'info' : "{'format' : '15.15s', 'max_length' : 15, 'options' : ['nm','nm/s']}"},
        'vang' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-1.', 'info' : "{'format' : '6.1f', 'range_in' : [0.,180.]}"},
        'vmodel' : {'sa_coltype' : 'String(15)', 'default' : '-', 'info' : "{'format' : '15.15s', 'max_length' : 15}"},
        'wfid' : {'sa_coltype' : 'Integer', 'default' : '-1', 'info' : "{'format' : '9d', 'gt' : 0}"},
        'wgt' : {'sa_coltype' : 'Float(precision=24)', 'default' : '-1.', 'info' : "{'format' : '6.3f', 'range_ex' : [0.,1000.]}"}
    },
    'models' : {
        'affiliation' : {
            'description' : 'The affiliation table groups stations into networks. It contains station-to-array mapping.',
            'columns' : ['net','sta','time','endtime','lddate'],
            'constraints' : [{'pk' : ['net','sta','time']}]
        },
        'amplitude' : {
            'description' : 'The amplitude table contains arrival-based and origin-based amplitude measurements.',
            'columns' : ['ampid','arid','parid','chan','amp','per','snr','amptime','time','duration','deltaf','amptype','units','clip','inarrival','auth','lddate'],
            'constraints' : [{'pk' : ['ampid'], 'uq' : ['amptime','amptype','arid','auth','chan','deltaf','duration','parid','per','time']}]
        },
        'arrival' : {
            'description' : 'The arrival table contains summary information about arrivals.',
            'columns' : ['sta','time','arid','jdate','stassid','chanid','chan','iphase','stype','deltim','azimuth','delaz','slow','delslo','ema','rect','amp','per','logat','clip','fm','snr','qual','auth','commid','lddate'],
            'constraints' : [{'pk' : ['arid'], 'uq' : ['auth','chan','iphase','sta','time']}]
        },
        'assoc' : {
            'description' : 'The assoc table contains information that connects arrives (entries in the arrival table) to a particular origin.',
            'columns' : ['arid','orid','sta','phase','belief','delta','seaz','esaz','timeres','timedef','azres','azdef','slores','slodef','emares','wgt','vmodel','commid','lddate'],
            'constraints' : [{'pk' : ['arid','orid']}]
        },
        'event' : {
            'description' : 'The event table contains a list of events. Multiple origins may be defined for any one event in the origin table. The column prefor points to the preferred origin.',
            'columns' : ['evid','evname','prefor','auth','commid','lddate'],
            'constraints' : [{'pk' : ['evid'], 'uq' : ['prefor']}]
        },
        'gregion' : {
            'description' : 'The gregion table contains geographic region numbers and their equivalent descriptions.',
            'columns' : ['grn','grname','lddate'],
            'constraints' : [{'pk' : ['grn']}]
        },
        'instrument' : {
            'description' : 'The instrument table contains ancillary calibration information. It holds nominal one frequence calibration factors for each instrument and pointers to nominal frequency-dependent calibration for an instrument. This table also holds pointers to the exact calibrations obained by direct measurmenet on a particular instrument (see sensor).',
            'columns' : ['inid','insname','instype','band','digital','samprate','ncalib','ncalper','dir','dfile','rsptype','lddate'],
            'constraints' : [{'pk' : ['inid'], 'uq' : ['dfile','dir','instype','ncalib','samprate']}]
        },
        'lastid' : {
            'description' : 'The lastid table contains counter values (the last value used for keys). This table is a reference table from which programs may retrieve the last sequential value of one of the numeric keys. Unique keys are required before inserting a record in numerous tables. The lastid table has exactly one row for each keyname.',
            'columns' : ['keyname','keyvalue','lddate'],
            'constraints' : [{'pk' : ['keyname']}]
        },
        'netmag' : {
            'description' : 'The netmag table contains estimates of network magnitudes of different types for a given event. Each network magnitude has a unique magid. Station magnitudes used to compute the network magnitude are in the stamag table.',
            'columns' : ['magid','net','orid','evid','magtype','nsta','magnitude','uncertainty','auth','commid','lddate'],
            'constraints' : [{'pk' : ['magid'], 'uq' : ['auth','magtype','orid']}]
        },
        'network' : {
            'description' : 'The network table contains general information about seismic networks (see affiliation).',
            'columns' : ['net','netname','nettype','auth','commid','lddate'],
            'constraints' : [{'pk' : ['net'], 'uq' : ['auth','netname']}]
        },
        'origerr' : {
            'description' : 'The origerr table contains summaries of confidence bounds in origin estimations. The measurement types are the elements of the location covariance matrix. The descriptive types give the uncertainties in location, depth, and origin time. The quantities are calculated from the covariance matrix, assuming gaussian errors and a confidence level conf.',
            'columns' : ['orid','sxx','syy','szz','stt','sxy','sxz','syz','stx','sty','stz','sdobs','smajax','sminax','strike','sdepth','stime','conf','commid','lddate'],
            'constraints' : [{'pk' : ['orid']}]
        },
        'origin' : {
            'description' : 'The origin table contains information describing a derived or reported origin for a particular event.',
            'columns' : ['lat','lon','depth','time','orid','evid','jdate','nass','ndef','ndp','grn','srn','etype','depdp','dtype','mb','mbid','ms','msid','ml','mlid','algorithm','auth','commid','lddate'],
            'constraints' : [{'pk' : ['orid'], 'uq' : ['auth','depth','lat','lon','time']}]
        },
        'remark' : {
            'description' : 'The remark table contains comments. This table may be used to store free-form comments that embellish records of other tables. The commid type in many tables refers to a record in the remark table. If commid is N/A (-1) in a record of any other table, no comments are stored for that record.',
            'columns' : ['commid','lineno','remark','lddate'],
            'constraints' : [{'pk' : ['commid','lineno']}]
        },
        'sensor' : {
            'description' : 'The sensor table stores calibration information specific sensor channels. This table provides a record of updates in the calibration factor or clock error of each instrument and links a sta/chan/time to a complete instrument response in the instrument table. Waveform data are converted into physical units through multiplication by the calib type located in wfdisc. The correct value of calib may not be accurately known when the wfdisc record is entered into the database. The sensor table provides the mechanism (calratio and calper) to update calib, without requiring possibly hundreds of wfdisc records to be updated. Through the foreign key inid, this table is linked to instrument, which has types pointing to flat files holding detailed calibration information in a variety of formats (see instrument).',
            'columns' : ['sta','chan','time','endtime','inid','chanid','jdate','calratio','calper','tshift','instant','lddate'],
            'constraints' : [{'pk' : ['chan','sta','time']}]
        },
        'site' : {
            'description' : 'The site table contains station location information. It names and describes a point on the earth where measurements are made (for example, the location of an instrument or array of instruments). This table contains information that normally changes infrequently, such as location. In addition, the site table contains types that describe the offset of a station relative to an array reference location. Global data integrity implies that the sta/ondate in site be consistent with the sta/chan/ondate in the sitechan table table.',
            'columns' : ['sta','ondate','offdate','lat','lon','elev','staname','statype','refsta','dnorth','deast','lddate'],
            'constraints' : [{'pk' : ['ondate','sta']}]
        },
        'sitechan' : {
            'description' : 'The sitchan table contains station-channel information. It describes the orientation of a recording channel at the site referenced by sta. The table provides information about the various channels that are available at a station and maintains a record of the physical channel configuration at a site.',
            'columns' : ['sta','chan','ondate','chanid','offdate','ctype','edepth','hang','vang','descrip','lddate'],
            'constraints' : [{'pk' : ['chanid'], 'uq' : ['chan','ondate','sta']}]
        },
        'sregion' : {
            'description' : 'The sregion table contains seismic region numbers and their equivalent descriptions.',
            'columns' : ['srn','srname','lddate'],
            'constraints' : [{'pk' : ['srn']}]
        },
        'stamag' : {
            'description' : 'The stamag table contains station magnitude estimates based upon measurements made on specific seismic phases. Values in the stamag table are used to calculate network magnitudes stored in the netmag table.',
            'columns' : ['magid','ampid','sta','arid','orid','evid','phase','delta','magtype','magnitude','uncertainty','magres','magdef','mmodel','auth','commid','lddate'],
            'constraints' : [{'pk' : ['ampid','arid','auth','magid','phase','sta']}]
        },
        'wfdisc' : {
            'description' : 'The wfdisc table contains a waveform header file and descriptive information. This table provides a pointer (or index) to waveforms stored on disk. The waveforms themselves are stored in ordinary disk files as a sequence of sample values (usually in binary representation).',
            'columns' : ['sta','chan','time','wfid','chanid','jdate','endtime','nsamp','samprate','calib','calper','instype','segtype','datatype','clip','dir','dfile','foff','commid','lddate'],
            'constraints' : [{'pk' : ['wfid'], 'uq' : ['chan','sta','time']}]
        },
        'wftag' : {
            'description' : 'The wftag table links various identifiers with specific waveforms, for example, orid, arid, and stassid to wfid. Linkages can also be determined indirectly using sta/chan/time table; however, it is more efficient to use the wftag table.',
            'columns' : ['tagname','tagid','wfid','lddate'],
            'constraints' : [{'pk' : ['tagid','tagname','wfid']}]
        }
    }
    }
}
