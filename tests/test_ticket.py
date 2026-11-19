
def test_create_ticket(client,auth_headers,admin_user):
   resp = client.post(
       "/api/v1/tickets",json={"title":"3号线贴片机报警","priority":1},headers=auth_headers
   )
   assert resp.status_code == 201
   body = resp.json()
   assert body["title"] == "3号线贴片机报警"
   assert body["status"] == "pending"
   assert body["created_by"] == admin_user.id

def test_list_pagination(client,auth_headers,create_ticket):
    for i in range(5):
        create_ticket(title=f"ticket-{i}")

    body = client.get("/api/v1/tickets",params={"page":1,"size":2},headers=auth_headers).json()
    assert body["total"] == 5
    assert len(body["items"]) == 2 #第一页2条
    assert body["items"][0]["title"] == "ticket-4"   # 按 created_at 倒序，最新的在前

    last = client.get("/api/v1/tickets",params={"page":3,"size":2},headers=auth_headers).json()
    assert len(last["items"]) == 1

def test_list_filter_by_status(client,auth_headers,create_ticket):
    create_ticket(title="pending-one")
    create_ticket(title="processing-one",status="processing")

    body = client.get("/api/v1/tickets", params={"status": "pending"}, headers=auth_headers).json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "pending-one"


def test_get_missing_ticket(client,auth_headers):
    resp = client.get("/api/v1/tickets/10086",headers=auth_headers)
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "NOT_FOUND"

def test_invalid_transition(client,auth_headers,create_ticket):
    ticket = create_ticket() #pending
    resp = client.patch(
        f"/api/v1/tickets/{ticket['id']}",json={"status":"done"},headers=auth_headers
    )
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "CONFLICT"

def test_operator_cannot_delete(client,create_ticket,operator_headers):
    ticket = create_ticket()
    resp = client.delete(f"/api/v1/tickets/{ticket['id']}",headers=operator_headers)
    assert resp.status_code == 403

def test_list_require_auth(client):
    assert client.get("/api/v1/tickets").status_code == 401