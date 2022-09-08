import pandas as pd
import logging as l
import re

logger = l.getLogger('ct.conv')
logger.setLevel(l.DEBUG)

# create console handler and set level to debug
ch = l.StreamHandler()
ch.setLevel(l.DEBUG)

# create formatter
formatter = l.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

from functools import wraps
def logM(f):
    @wraps(f)
    def wrapper(*args, **kwargs):

        dd= locals()
        # print(dd['args'].keys())
        n = f.__code__.co_argcount
        ids1 = f.__code__.co_varnames[0:n]
        ids = f.__code__.co_varnames[0:n]
        print(n)
        print(len(dd))
        print(len(dd) == n)
        print(f'ids: {ids}')
        print(f'ids1: {ids1}')
        print(f'locals: {dd.keys()}')

        dat = ids[0:len(dd)]
        print(dat)


        logger.debug('calling %s%s' % (f.__name__, ids))
        for i in range(n):
            if len(f.__dict__) > 0:
                logger.debug('\t%s = %s' % (ids[i], f.__dict__[ids[i]]))
            else:
                logger.debug('\t%s = %s' % (ids[i], None))
        return f(*args, **kwargs)
    return wrapper


# read targeted ms data into file or python workspace
# ds=readTarMS(path, 'barw', 'collectedData.csv')
# def readTarMS(path, pattern=[], filename=None):
#     import os
#     import re
#     import pandas as pd
#     import io
#
#     def readMat(path, f):
#         fh = os.path.join(path, f)
#
#         cpds = {}
#         collect = False
#         with open(fh, 'r', encoding='utf-8', errors='ignore') as file:
#             data = file.readlines()
#             for l in data:
#                 if bool(re.search('Compound [0-9]', l)):
#                     cpd = re.sub('Compound [0-9]+:\s+', '', l.strip())
#                     cpds[cpd] = []
#                     collect = True
#                     continue
#                 if collect and l.strip() != '':
#                     cpds[cpd].append(l)
#
#         mets = []
#         for fid, d in cpds.items():
#             df = pd.read_table(io.StringIO(''.join(d)))
#             df['cpd'] = fid
#             df['path'] = fh
#             mets.append(df)
#
#         return pd.concat(mets)
#
#         ds = pd.read_table(io.StringIO(''.join(cpds['Compound 1:  tryptophan'])))
#         return ds
#
#     flist = [fn for fn in os.listdir(path) if any([bool(re.search(st.lower(), fn.lower())) for st in pattern])]
#
#     dfs=[]
#     for f in flist:
#         print(f)
#         dfs.append(readMat(path, f))
#
#     ds = pd.concat(dfs)
#     # remove QCs
#     ds=ds[ds.Type == 'Analyte']
#     ds= ds[~ ds.cpd.str.contains('^SIL')]
#
#     ds['id'] = ds['path']+ds['Name']+ds['Sample Text']
#     ds.set_index(['id'])
#     # ts=ds.pivot_table(index = 'id', columns='cpd', values='Conc.', aggfunc='mean')
#     ts=ds.pivot_table(index = 'id', columns='cpd', values='Conc.')
#
#     if filename is not None:
#         ts.to_csv(os.path.join(path, filename))
#     else:
#         return ts

@logM
def readMat(content, filename):
    import base64, re, io
    import pandas as pd
    data = base64.b64decode(content)

    cpds = {}
    collect = False
    for l in data.splitlines():
        l= l.decode('unicode_escape')
        if bool(re.search('Compound [0-9]', l)):
            cpd = re.sub('Compound [0-9]+:\s+', '', l.strip())
            cpds[cpd] = []
            collect = True
            continue
        if collect and l.strip() != '':
            cpds[cpd].append(l)

    mets = []
    for fid, d in cpds.items():
        df = pd.read_table(io.StringIO('\n'.join(d)))
        df['cpd'] = fid
        df['path'] = filename
        mets.append(df)
    # import pickle
    # pickle.dump(pd.concat(mets), open('/Users/TKimhofer/Downloads/RE__Trp_data_from_PAT01/Barwon_adult.p', 'wb'))
    return pd.concat(mets)

@logM
def readbin(contents, filenames, varType='Conc.', featureType='analyte|standard', sil=True):
    ''' converts base64 binary encoded string to desired output format
    filename is string, content is base64 encoded binary string
    varType is desired variable in data file (typically 'Conc.' or 'Response')
    featureType is desired feature information in regex with ignore case flag (e.g. 'analyte' or 'analyte|cal')
    '''

    dfs={'data': [], 'fn' : []}
    for c, f in zip(contents, filenames):
        try:
            imm = readMat(c, f)
            dfs['data'].append(imm)
        except:
            dfs['fn'].append(f)
            print(f'Import failed for {f}')
            continue
    try:
        ds = pd.concat(dfs['data'])
    except:
        print(filenames)
        print(f'Conversion failed: Could not combine data from all files.')
        return None

    # remove QCs and internal standards
    # print(ds['Sample Text'].value_counts())
    ds=ds[ds.Type.str.contains(featureType, regex=True, flags=re.IGNORECASE)]
    # print(ds.Type.str.contains(featureType, regex=True, flags=re.IGNORECASE).value_counts())
    # print(ds[ds.Type.str.contains(featureType, regex=True, flags=re.IGNORECASE)])
    # print(ds[ds.Type.str.contains(featureType, regex=True, flags=re.IGNORECASE)].iloc[0].T)
    if not sil:
        ds= ds[~ ds.cpd.str.contains('^SIL')]
    # print(ds.columns)
    # ds.Type.value_counts()
    # ds['id'] = ds['path']+ds['Name']+ds['Sample Text']
    # ds.set_index(['id'])
    # np.array([x[2] for x in tf.index])
    tf=ds.pivot_table(index = ['path','Name', 'Sample Text'], columns='cpd', values=varType)
    # print(tf[0:4])
    tf = tf.astype(float)
    tff = tf.reset_index()
    # tf.insert(loc=0, column='id', value=tf.index)
    return tff



# #
# # #
# # # #
# fh= '/Users/TKimhofer/Downloads/RE__Trp_data_from_PAT01/Barwon_adult_Plate9.TXT'
# import pandas as pd
# pd.read_csv(fh, encoding='latin1')
# import base64
# with open(fh, 'rb') as file:
#      dat = file.read()
# # import pickle
# # df=pickle.load(open('/Users/TKimhofer/Downloads/RE__Trp_data_from_PAT01/Barwon_adult.p', 'rb'))
# # ds=df
# # # #
# # # content=base64.b64encode(dat)
# # # # content=base64.decodebytes(r)
# # [x[2] for x in tf.index]
# # [x[2] for x in tf.index if 'Cal' in x]
# # df['Sample Text'].