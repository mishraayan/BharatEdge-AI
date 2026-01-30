from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect data files for dependencies if needed (e.g. fast-api, uvicorn)
datas = collect_data_files('llama_cpp')
datas += collect_data_files('sentence_transformers')
datas += collect_data_files('chromadb')

# Manually add the chromadb source folder to be sure
import chromadb
datas += [(os.path.dirname(chromadb.__file__), 'chromadb')]

a = Analysis(
    ['src/main.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'fastapi',
        'src.rag_engine',
        'src.ingestion',
        'src.llm_engine',
        'src.vector_db',
        'src.models',
        'src.config',
        'chromadb.api.segment',
        'chromadb.telemetry.product.posthog',
        'chromadb.db.impl.sqlite',
        'chromadb.migrations',
        'chromadb.db.mixins.embeddings_queue',
        'chromadb.db.mixins.sysdb',
        'chromadb.ingest.impl.fastapi',
        'chromadb.segment.impl.vector.local_persistent_hnsw',
        'chromadb.segment.impl.metadata.sqlite',
        'chromadb.base',
        'chromadb.api.fastapi',
    ] + collect_submodules('chromadb') + collect_submodules('llama_cpp'),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='bharatedge-backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
