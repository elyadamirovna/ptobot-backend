# Local setup

1. Export the required environment variables before running the app:
   ```bash
   export DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/ptobot
   export YC_S3_BUCKET=ptobot-assets
   export YC_S3_ACCESS_KEY_ID=your_key
   export YC_S3_SECRET_ACCESS_KEY=your_secret
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
