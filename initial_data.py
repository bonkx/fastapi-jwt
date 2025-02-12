import asyncio
import json
import os
from pathlib import Path
from random import randint

from fastapi import Depends
from sqlmodel import Field, Session, SQLModel, and_, col, func, or_, select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.sql.expression import SelectOfScalar

from app.core.config import settings
from app.core.database import sessionmanager
from app.models import Hero, HeroCreate, HeroPublisher, HeroPublisherCreate
from app.repositories.base import BaseRepository

BASE_DIR = Path(__file__).resolve().parent.parent
# Get current directory
CUR_DIR = Path(__file__).parent.absolute()


async def populate_hero_data():
    print("------ START POPULATE_HERO_DATA ------")
    total_superhero = 0
    ###################################
    # HERO PUBLISHER SECTION
    ###################################

    async with sessionmanager.session() as db_session:
        # check count data hero_publisher
        stmt = select(HeroPublisher)
        base_repo = BaseRepository(db_session)
        total = await base_repo.get_count(stmt)
        total_superhero = await base_repo.get_count(select(Hero))
        # print(total)
        if total <= 0:
            res_publisher = await base_repo.add_all([
                HeroPublisher(**{"name": "Marvel Comics"}),
                HeroPublisher(**{"name": "DC Comics"}),
            ])
        else:
            result = await db_session.exec(stmt)
            res_publisher = result.all()

        # print(res_publisher)

    ###################################
    # HERO SECTION
    ###################################

    if total_superhero <= 0:
        # read json file
        json_file = CUR_DIR/'tests/data/superheroes.json'

        with open(json_file) as json_data:
            d = json.load(json_data)
            json_data.close()
        # print(d)

        for i in d:
            # print(i["superhero"])
            publisher_id = 1
            for u in res_publisher:
                if i["publisher"] in u.name:
                    publisher_id = u.id

            model = HeroCreate(
                name=i["alter_ego"],
                age=randint(20, 40),
                secret_name=i["superhero"],
                hero_publisher_id=publisher_id

            )
            db_hero = Hero.model_validate(model)
            # print(db_hero)
            db_session.add(db_hero)

        await db_session.commit()

    print("------ END POPULATE_HERO_DATA ------")

if __name__ == "__main__":
    asyncio.run(populate_hero_data())
