#!/usr/bin/env python3
"""Start the handoff workspace, restoring saved data only on first use."""
from __future__ import annotations
import importlib.util
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
APP = ROOT / '文案助手' / 'wechat-writer'


def main() -> int:
    if sys.version_info < (3, 11):
        print('请安装 Python 3.11 或更高版本。')
        return 1
    data = Path(os.environ.get('WECHAT_WRITER_DATA', str(APP / 'data'))).expanduser().resolve()
    if not (data / 'workspace.sqlite3').exists():
        spec = importlib.util.spec_from_file_location('handoff_restore', ROOT / 'restore-data.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.restore(data)
        print('首启已恢复 {articles} 条素材、{cards} 张写法卡、{drafts} 篇草稿。'.format(**result['records']), flush=True)
    os.environ['WECHAT_WRITER_DATA'] = str(data)
    os.chdir(APP)
    os.execv(sys.executable, [sys.executable, str(APP / 'app.py'), *sys.argv[1:]])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
