# CREATE TABLES IN SUPABASE DATABASE 
# FOLLOWING DATA MODELS SPECIFIED IN database/models/data_models.py


import asyncio
from database import (Base, Task, TaskDistribution, TaskAssessment, WeeklyStatistics, get_engine)

engine = get_engine()
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init_db())
