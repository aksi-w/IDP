import os
import sys

os.environ.setdefault('PGCLIENTENCODING', 'UTF8')
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

if sys.platform == 'win32':
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except:
            pass
    if hasattr(sys.stderr, 'reconfigure'):
        try:
            sys.stderr.reconfigure(encoding='utf-8')
        except:
            pass

try:
    from dotenv import load_dotenv
    try:
        load_dotenv(encoding='utf-8')
    except:
        try:
            load_dotenv(encoding='cp1251')
        except:
            load_dotenv()
except:
    pass

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/idp_db")

if sys.platform == 'win32':
    parsed = urlparse(DATABASE_URL)
    DATABASE_URL = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        '',
        '',
        ''
    ))
else:
    try:
        parsed = urlparse(DATABASE_URL)
        query_params = parse_qs(parsed.query)
        query_params['client_encoding'] = ['utf8']
        new_query = urlencode(query_params, doseq=True)
        DATABASE_URL = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment
        ))
    except Exception:
        separator = '&' if '?' in DATABASE_URL else '?'
        DATABASE_URL = f"{DATABASE_URL}{separator}client_encoding=utf8"

connect_args = {
    "options": "-c client_encoding=utf8",
}

if sys.platform == 'win32':
    connect_args['sslmode'] = 'disable'
    connect_args['client_encoding'] = 'utf8'

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)


