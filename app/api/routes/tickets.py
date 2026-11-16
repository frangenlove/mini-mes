from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.schemas.ticket import TicketCreate,TicketRead,TicketUpdate
from app.db import get_db
from app.schemas.common import Page
from app.services import ticket as ticket_service
router = APIRouter(prefix="/tickets", tags=["tickets"])

@router.post("", response_model=TicketRead, status_code=201)
def create(payload: TicketCreate, db: Session = Depends(get_db)):
    return ticket_service.create_ticket(db, payload, user_id=1)   # D4 换成当前用户

@router.get("", response_model=Page[TicketRead])
def list_tickets(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),        # 上限必须卡死，否则有人传 size=1000000
    status: str | None = None,
    q: str | None = None,
    db: Session = Depends(get_db),
):
    items, total = ticket_service.list_tickets(db, page=page, size=size, status=status, q=q)
    return {"items": items, "total": total, "page": page, "size": size}

@router.get("/{ticket_id}", response_model=TicketRead)
def get_one(ticket_id: int,db: Session = Depends(get_db)):
    return ticket_service.get_ticket(db,ticket_id)

@router.patch("/{ticket_id}", response_model=TicketRead)
def patch(ticket_id: int,payload: TicketUpdate,db: Session = Depends(get_db)):
    return ticket_service.update_ticket(db,ticket_id,payload)

@router.delete("/{ticket_id}", status_code=204)
def delete(ticket_id: int,db: Session = Depends(get_db))-> None:
    ticket_service.delete_ticket(db,ticket_id)