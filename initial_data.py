import asyncio
import json
import os
from pathlib import Path
from random import randint

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.models.hero import Hero, HeroCreate

BASE_DIR = Path(__file__).resolve().parent.parent
# Get current directory
CUR_DIR = Path(__file__).parent.absolute()


async def populate_hero_data(session: AsyncSession = Depends(get_session)):
    # read json file
    json_file = CUR_DIR/'scripts/superheroes.json'

    with open(json_file) as json_data:
        d = json.load(json_data)
        json_data.close()
    # print(d)

    for i in d:
        print(i["superhero"])
        # model = HeroCreate(
        #     name=fake.name(),
        #     age=randint(20, 40),
        #     secret_name=fake.unique.first_name(),

        # )
        # db_hero = Hero.model_validate(model)
        # db_session.add(db_hero)


if __name__ == "__main__":
    asyncio.run(populate_hero_data())
