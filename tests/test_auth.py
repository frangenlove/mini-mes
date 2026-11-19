

def test_login_success(client,create_user):
    create_user("admin","admin123","admin")
    resp = client.post("/api/v1/auth/login",data={"username":"admin","password":"admin123"})
    assert resp.status_code == 200
    assert resp.json()["token_type"] == "bearer"
    assert resp.json()["access_token"]

def test_login_wrong_password(client,create_user):
    create_user("admin","admin123","admin")
    resp = client.post("/api/v1/auth/login",data={"username":"admin","password":"nope"})
    assert resp.status_code == 401

