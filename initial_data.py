import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from random import randint

from fastapi import Depends
from sqlmodel import Field, Session, SQLModel, and_, col, func, or_, select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.sql.expression import SelectOfScalar

from app.core.config import settings
from app.core.database import sessionmanager
from app.core.security import generate_passwd_hash, verify_password
from app.models import (Hero, HeroCreate, HeroPublisher, Status, User,
                        UserProfile)
from app.repositories.base import BaseRepository

BASE_DIR = Path(__file__).resolve().parent.parent
# Get current directory
CUR_DIR = Path(__file__).parent.absolute()


async def populate_status_data():
    print("------ START POPULATE_STATUS_DATA ------")

    async with sessionmanager.session() as db_session:
        # check count data status
        stmt = select(Status)
        base_repo = BaseRepository(db_session)
        total = await base_repo.get_count(stmt)
        # print(total)
        if total <= 0:
            res_add_all = await base_repo.add_all([
                Status(**{"name": "Active"}),
                Status(**{"name": "In-Active"}),
                Status(**{"name": "Pending"}),
                Status(**{"name": "Suspended"}),
            ])

    print("------ END POPULATE_STATUS_DATA ------")


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


async def populate_admin_super_user():
    print("------ START POPULATE_ADMIN_SUPER_USER ------")

    async with sessionmanager.session() as db_session:
        # check count admin super user
        stmt = select(User).where(User.username == "admin")
        base_repo = BaseRepository(db_session)
        total = await base_repo.get_count(stmt)
        # print(total)
        password = "password"

        if total <= 0:
            # create User
            hashed_pasword = await generate_passwd_hash(password)
            res_user = await base_repo.add_one(
                User(**{
                    "first_name": "Admin",
                    "last_name": "System",
                    "username": "admin",
                    "email": "admin@admin.com",
                    "password": hashed_pasword,
                    "is_verified": True,
                    "is_superuser": True,
                    "is_staff": True,
                    "verified_at": datetime.now(),
                }),
            )

            # create UserProfile
            res_user_profile = await base_repo.add_one(
                UserProfile(**{
                    "role": "Admin",
                    "user_id": res_user.id,
                    "status_id": 1,  # Activce
                })
            )
    # verify_pass = await verify_password(password, "$2b$12$/fs0sJy3dQmfGCRaCTv3zeenB.kCWuIlpmW27zMu0AabwUrra7Nxq")
    # print(verify_pass)

    print("------ END POPULATE_ADMIN_SUPER_USER ------")

if __name__ == "__main__":
    asyncio.run(populate_hero_data())
    asyncio.run(populate_status_data())
    asyncio.run(populate_admin_super_user())
