from app.infrastructure.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    rows = db.execute(text("select id, name, is_active, parent_id from work_types order by sort_order, id")).fetchall()
    print(rows)
finally:
    db.close()
