# Local setup

1. Create a `.env` file next to `app/` and include at least:
   ```env
   DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/ptobot
   YC_S3_BUCKET=ptobot-assets
   YC_S3_ACCESS_KEY_ID=your_key
   YC_S3_SECRET_ACCESS_KEY=your_secret
   ```

2. Install dependencies and set up the database schema:
   ```bash
   pip install -r requirements.txt
   alembic upgrade head
   ```

3. Start the API:
   ```bash
   uvicorn main:app --reload
   ```

`DATABASE_URL` is consumed by SQLAlchemy and Alembic; adjust it for your Postgres host/user/password.
