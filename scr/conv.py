import base64
import pandas as pd
import logging
import re
import io
from functools import wraps

# ---------------- Logging Setup ----------------
logger = logging.getLogger('ct.conv')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# ---------------- Logging Decorator ----------------
def log_call(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        logger.debug(f"Calling {f.__name__} with args={args} kwargs={kwargs}")
        return f(*args, **kwargs)
    return wrapper

# ---------------- Data Reading Functions ----------------
@log_call
def readMat(content, filename):
    data = base64.b64decode(content)
    cpds = {}
    collect = False

    for line in data.splitlines():
        line = line.decode('unicode_escape')
        if re.search(r'Compound \d+', line):
            cpd = re.sub(r'Compound \d+:\s+', '', line.strip())
            cpds[cpd] = []
            collect = True
            continue
        if collect and line.strip():
            cpds[cpd].append(line)

    mets = []
    for fid, entries in cpds.items():
        df = pd.read_table(io.StringIO('\n'.join(entries)))
        df['cpd'] = fid
        df['path'] = filename
        mets.append(df)

    return pd.concat(mets)

@log_call
def readbin(contents, filenames, varType='Conc.', featureType='analyte|standard', sil=True):
    """
    Converts base64 binary encoded strings into structured data.
    Filters by analyte type and optionally removes SIL compounds.
    """
    collected_data = {'data': [], 'failed': []}

    for content, fname in zip(contents, filenames):
        try:
            df = readMat(content, fname)
            collected_data['data'].append(df)
        except Exception as e:
            logger.warning(f"Import failed for {fname}: {e}")
            collected_data['failed'].append(fname)

    if not collected_data['data']:
        logger.error("No data could be loaded from provided files.")
        return None

    try:
        ds = pd.concat(collected_data['data'])
    except Exception as e:
        logger.error(f"Failed to concatenate data: {e}")
        return None

    try:
        ds = ds[ds.Type.str.contains(featureType, regex=True, flags=re.IGNORECASE)]
    except Exception as e:
        logger.warning(f"Feature filtering failed: {e}")

    if not sil:
        ds = ds[~ds.cpd.str.contains('^SIL')]

    tf = ds.pivot_table(index=['path', 'Name'], columns='cpd', values=varType)
    tf = tf.astype(float)
    return tf.reset_index()
