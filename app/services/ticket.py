from sqlalchemy import func,select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models import Ticket
from app.schemas.ticket import TicketCreate,TicketUpdate

def list_tickets(
        db: Session, 
        *, 
        page: int, 
        size: int, 
        status: str | None, 
        q: str | None
) -> tuple[list[Ticket], int]:
    stmt = select(Ticket)
    if status:
        stmt = stmt.where(Ticket.status == status)
    if q:
        stmt = stmt.where(Ticket.title.ilike(f"%{q}%"))

    #总数要带上同样的筛选条件，否则total永远是全表
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = db.scalars(
        stmt.order_by(Ticket.created_at.desc())
        .offset((page-1)*size)
        .limit(size)
    ).all()
    return list(rows),total
    
def get_ticket(db: Session, ticket_id: int) -> Ticket:
    ticket = db.get(Ticket,ticket_id)
    if ticket is None:
        raise NotFoundError(f"ticket {ticket_id} not found")
    return ticket

def create_ticket(db: Session, payload: TicketCreate, user_id: int) -> Ticket:
    ticket = Ticket(**payload.model_dump(),created_by=user_id)
    db.add(ticket)
    db.commit()
    db.refresh(ticket) # 拿到数据库生成的 id / created_at
    return ticket

def update_ticket(db: Session, ticket_id: int, payload: TicketUpdate) -> Ticket:
    ticket = get_ticket(db,ticket_id)
    for field,value in payload.model_dump(exclude_unset=True).items():
        setattr(ticket,field,value)
    db.commit()
    db.refresh(ticket)
    return ticket


def delete_ticket(db: Session, ticket_id: int) -> None:
    ticket = get_ticket(db,ticket_id)
    db.delete(ticket)
    db.commit()
