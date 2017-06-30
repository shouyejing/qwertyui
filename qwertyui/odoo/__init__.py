import datetime
import os
import requests
import tempfile

from qwertyui import urlparse


def download_backup(host, db, master_pwd, backup_dir=None, backup_format='zip', chunk_size=16384):
    """
    Downloads a full backup of an ODOO database and all data files.
    """

    if not backup_dir:
        backup_dir = tempfile.mkdtemp()

    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    session = requests.Session()

    session.get(
        '%s/web' % host,
        params={'db': db},
        verify=True
    )
    resp = session.post(
        '%s/web/database/backup' % host,
        {'master_pwd': master_pwd, 'name': db, 'backup_format': backup_format},
        stream=True,
        verify=True
    )
    if 'application/octet-stream' not in resp.headers['Content-Type']:
        raise Exception('Content-type is not application/octet-stream, no zipfile received!')

    now = datetime.datetime.now()
    parsed = urlparse(host)
    file_name = 'backup-%s-%s-%s.%s' % (
        parsed.hostname,
        db,
        now.strftime('%Y%m%d-%H%M%S'),
        backup_format
    )
    file_path = os.path.join(backup_dir, file_name)

    with open(file_path, 'wb') as f:
        size = 0
        for chunk in resp.iter_content(chunk_size):
            f.write(chunk)
            size += len(chunk)

    return file_path, size