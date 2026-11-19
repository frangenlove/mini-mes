import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine,text,select
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.security import hash_password,decode_access_token
from app.db import Base,get_db
from app.main import app
from app.models import User
from app.models.ticket import Ticket

engine = create_engine(settings.test_database_url,pool_pre_ping=True)
TestingSessionLocal = sessionmaker(bind=engine,autoflush=False,expire_on_commit=False)

@pytest.fixture(scope="session",autouse=True)
def setup_schema():
    """整个测试会话开始前建表，结束后清空"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def clean_tables():
    """每个用例前后清理数据，保证互不污染"""
    with engine.begin() as conn:
        # 连同自增id一起重置，这样断言就 id == 1。cascade用于处理外键
        conn.execute(text("TRUNCATE TABLE tickets,users RESTART IDENTITY CASCADE"))
    yield

@pytest.fixture
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def client(db):
    """把应用里的get_db换成测试库的session"""
    # dependency_overrides是fastapi官方测试hook
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def create_user(db):
    def _create(username="admin",password="admin123",role="admin") -> User:
        user = User(username=username,hashed_password=hash_password(password),role=role)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    return _create

@pytest.fixture
def admin_user(create_user):
    return create_user("admin","admin123","admin")

@pytest.fixture
def operator_user(create_user):
    return create_user("operator","operator123","operator")

@pytest.fixture
def auth_headers(client,admin_user):
    resp = client.post("/api/v1/auth/login",data={"username":"admin","password":"admin123"})
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()["access_token"]}"}

@pytest.fixture
def operator_headers(client,operator_user):
    resp = client.post("/api/v1/auth/login",data={"username":"operator","password":"operator123"})
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()["access_token"]}"}

@pytest.fixture
def create_ticket(client,auth_headers):
    """工厂 fixture：create_ticket(title=..., status=...) -> dict"""
    def _advance(ticket_id: int,status: str) -> dict:
        resp = client.patch(f"/api/v1/tickets/{ticket_id}",json={"status": status},headers=auth_headers)
        assert resp.status_code == 200, resp.text
        return resp.json()
    """创建单条工单"""
    def _create(title: str = "test ticket",priority: int = 3,status: str = "pending") -> dict:
        resp = client.post(
            "/api/v1/tickets",json={"title":title,"priority":priority},headers=auth_headers
        )
        assert resp.status_code == 201, resp.text
        ticket = resp.json()
        # status 不能直接指定，必须走状态机 —— 这本身就是在验证业务规则
        if status in ("processing","done"):
            ticket = _advance(ticket["id"],"processing")
        if status == "done":
            ticket = _advance(ticket["id"],"done")
        return ticket
    return _create