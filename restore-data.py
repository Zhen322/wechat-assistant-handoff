#!/usr/bin/env python3
"""Restore the handoff snapshot once; never overwrite an existing database."""
from __future__ import annotations
import argparse
from contextlib import closing
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import tempfile

ROOT = Path(__file__).resolve().parent
APP = ROOT / '文案助手' / 'wechat-writer'
SNAPSHOT = ROOT / 'handoff-data'


def restore(target: Path) -> dict:
    target = target.expanduser().resolve()
    database = target / 'workspace.sqlite3'
    if database.exists() or database.is_symlink():
        raise FileExistsError('目标已有 workspace.sqlite3，未覆盖。继续使用现有数据，或通过 --target 指定全新目录。')
    manifest = json.loads((SNAPSHOT / 'snapshot-manifest.json').read_text(encoding='utf-8'))
    source = SNAPSHOT / manifest['database']
    if hashlib.sha256(source.read_bytes()).hexdigest() != manifest['database_sha256']:
        raise ValueError('交接数据库校验不一致，请重新下载仓库，未恢复。')
    target.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix='.handoff-restore-', suffix='.sqlite3', dir=target)
    os.close(handle)
    pending = Path(temporary)
    copied = preserved = 0
    try:
        with closing(sqlite3.connect(source.as_uri() + '?mode=ro&immutable=1', uri=True)) as src:
            with closing(sqlite3.connect(pending)) as dst:
                src.backup(dst)
                dst.execute("PRAGMA journal_mode=DELETE")
                if dst.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                    raise ValueError('数据库完整性检查失败，未恢复。')
                for table, count in manifest['records'].items():
                    actual = dst.execute('SELECT COUNT(*) FROM "' + table + '"').fetchone()[0]
                    if actual != count:
                        raise ValueError('交接数据数量不一致：' + table)
                # Rebase only machine-local output paths; keep all content/history intact.
                for table in ('cards', 'drafts'):
                    for item_id, raw in dst.execute('SELECT id,data FROM ' + table).fetchall():
                        item = json.loads(raw)
                        item['file_path'] = str(target / table / (item_id + '.md'))
                        dst.execute('UPDATE ' + table + ' SET data=? WHERE id=?',
                                    (json.dumps(item, ensure_ascii=False, separators=(',', ':')), item_id))
                dst.commit()
        # Exclusive file creation preserves any existing notes/settings/sidecars.
        for original in sorted((SNAPSHOT / 'data').rglob('*')):
            if not original.is_file() or original.name.startswith('workspace.sqlite3'):
                continue
            relative = original.relative_to(SNAPSHOT / 'data')
            output = target / relative
            output.parent.mkdir(parents=True, exist_ok=True)
            try:
                with output.open('xb') as writer, original.open('rb') as reader:
                    shutil.copyfileobj(reader, writer)
                if output.name == 'settings.json':
                    output.chmod(0o600)
                copied += 1
            except FileExistsError:
                preserved += 1
        # Hard-link publication is atomic and refuses to replace a racing database.
        os.link(pending, database)
        database.chmod(0o600)
        return {'records': manifest['records'], 'copied': copied, 'preserved': preserved,
                'database': str(database)}
    finally:
        pending.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', type=Path,
                        default=Path(os.environ.get('WECHAT_WRITER_DATA', str(APP / 'data'))),
                        help='恢复目录；默认使用工作台 data（已有数据库时拒绝覆盖）')
    args = parser.parse_args()
    try:
        result = restore(args.target)
    except (FileExistsError, ValueError, OSError, sqlite3.Error) as exc:
        print('恢复未执行：' + str(exc))
        return 1
    print('交接数据已恢复：' + result['database'])
    print('素材 {articles}、写法卡 {cards}、草稿 {drafts}；已有文件保留 {preserved} 个。'.format(
        **result['records'], preserved=result['preserved']))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
