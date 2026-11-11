from datetime import datetime
from pydantic import BaseModel,ConfigDict,Field

"""
入参DTO
"""
class TicketCreate(BaseModel):
    title : str = Field(min_length=1,max_length=200)
    description : str | None = None
    priority : int = Field(default=3,ge=1,le=5)

"""
出参VO
"""
class TicketRead(BaseModel):
    # 设置为True可以让pydantic直接读ORM对象的属性
    model_config = ConfigDict(from_attributes=True)

    id : int
    title: str
    description : str | None
    status : str
    priority : int
    created_by : int
    created_at : datetime