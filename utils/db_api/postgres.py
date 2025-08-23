from typing import Union

import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool

from data import config


class Database:

    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create(self):
        self.pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            database=config.DB_NAME
        )

    async def execute(self, command, *args,
                      fetch: bool = False,
                      fetchval: bool = False,
                      fetchrow: bool = False,
                      execute: bool = False
                      ):
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
            return result

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ${num}" for num, item in enumerate(parameters.keys(),
                                                          start=1)
        ])
        return sql, tuple(parameters.values())

    async def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Users (
            telegram_id BIGINT PRIMARY KEY,
            first_name VARCHAR(255) NOT NULL,
            last_name VARCHAR(255) NOT NULL,
            username VARCHAR(255) NULL,
            language_code VARCHAR(10) NULL DEFAULT 'uz',
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
        );
        """
        await self.execute(sql, execute=True)

    async def create_table_sessions(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Sessions (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL REFERENCES Users(telegram_id) 
                ON DELETE CASCADE ON UPDATE CASCADE,
            session_data TEXT NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
        );
        """
        await self.execute(sql, execute=True)

    async def create_table_payment(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Payment (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL REFERENCES Users(telegram_id) 
                ON DELETE CASCADE ON UPDATE CASCADE,
            start_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            end_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            is_paid BOOLEAN DEFAULT FALSE,
            accepted_username_or_first_name VARCHAR(255) NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
        );
        """
        await self.execute(sql, execute=True)

    async def create_table_message(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Message (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL REFERENCES Users(telegram_id) 
                ON DELETE CASCADE ON UPDATE CASCADE,
            message_id VARCHAR(255) NULL,
            message_text TEXT NULL,
            sending_interval INT NULL,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
        );
        """
        await self.execute(sql, execute=True)

    # ---------------- Messages ----------------
    async def add_message(self, user_id, message_text, sending_interval, message_id=None):
        sql = """
        INSERT INTO Message (user_id, message_id, message_text, sending_interval) 
        VALUES ($1, $2, $3, $4) 
        RETURNING *;
        """
        data = await self.execute(sql, user_id, message_id, message_text, sending_interval, fetchrow=True)
        return data[0] if data else None

    async def select_message(self, **kwargs):
        sql = "SELECT * FROM Message WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        data = await self.execute(sql, *parameters, fetchrow=True)
        return {
            "id": data[0],
            "user_id": data[1],
            "message_id": data[2],
            "message_text": data[3],
            "sending_interval": data[4],
            "created_at": data[5],
            "updated_at": data[6]
        } if data else None

    async def update_message(self, id, **kwargs):
        set_query = ", ".join(
            [f"{key} = ${i}" for i, key in enumerate(kwargs.keys(), start=2)])
        sql = f"UPDATE Message SET {set_query}, updated_at = NOW() WHERE id = $1 RETURNING *"
        return await self.execute(sql, id, *kwargs.values(), fetchrow=True)

    async def delete_message(self, id):
        sql = "DELETE FROM Message WHERE id=$1 RETURNING *"
        return await self.execute(sql, id, fetchrow=True)

    # ---------------- Users ----------------
    async def add_user(self, telegram_id, first_name, last_name, username=None, language_code="uz"):
        sql = """
        INSERT INTO Users (telegram_id, first_name, last_name, username, language_code) 
        VALUES ($1, $2, $3, $4, $5) 
        RETURNING *;
        """
        user = await self.execute(sql, telegram_id, first_name, last_name, username, language_code, fetchrow=True)
        return user

    async def select_user(self, **kwargs):
        sql = "SELECT * FROM Users WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def update_user(self, telegram_id, **kwargs):
        # kwargs orqali (first_name, last_name, username, language_code, updated_at) o‘zgartiriladi
        set_query = ", ".join(
            [f"{key} = ${i}" for i, key in enumerate(kwargs.keys(), start=2)])
        sql = f"UPDATE Users SET {set_query}, updated_at = NOW() WHERE telegram_id = $1 RETURNING *"
        return await self.execute(sql, telegram_id, *kwargs.values(), fetchrow=True)

    async def delete_user(self, telegram_id):
        sql = "DELETE FROM Users WHERE telegram_id=$1 RETURNING *"
        return await self.execute(sql, telegram_id, fetchrow=True)

    async def select_all_users(self):
        sql = "SELECT * FROM Users"
        return await self.execute(sql, fetch=True)

    # ---------------- Sessions ----------------
    async def add_session(self, user_id, session_data):
        sql = """
        INSERT INTO Sessions (user_id, session_data) 
        VALUES ($1, $2) 
        RETURNING *;
        """
        return await self.execute(sql, user_id, session_data, fetchrow=True)

    async def select_session(self, **kwargs):
        sql = "SELECT * FROM Sessions WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        data = await self.execute(sql, *parameters, fetchrow=True)
        return None if not data else {
            "id": data[0],
            "user_id": data[1],
            "session_data": data[2],
            "created_at": data[3],
            "updated_at": data[4]
        }

    async def select_only_session_data(self, **kwargs):
        sql = "SELECT * FROM Sessions WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        data = await self.execute(sql, *parameters, fetchrow=True)
        return None if not data else data[2]

    async def update_session(self, session_id, **kwargs):
        set_query = ", ".join(
            [f"{key} = ${i}" for i, key in enumerate(kwargs.keys(), start=2)])
        sql = f"UPDATE Sessions SET {set_query}, updated_at = NOW() WHERE id = $1 RETURNING *"
        return await self.execute(sql, session_id, *kwargs.values(), fetchrow=True)

    async def delete_session(self, session_id):
        sql = "DELETE FROM Sessions WHERE id=$1 RETURNING *"
        return await self.execute(sql, session_id, fetchrow=True)

    async def select_all_sessions(self):
        sql = "SELECT * FROM Sessions"
        return await self.execute(sql, fetch=True)

    # ---------------- Payment ----------------
    async def add_payment(self, user_id, start_date, end_date, is_paid=False, accepted_username_or_first_name=""):
        sql = """
        INSERT INTO Payment (user_id, start_date, end_date, is_paid, accepted_username_or_first_name) 
        VALUES ($1, $2, $3, $4, $5) 
        RETURNING *;
        """
        return await self.execute(sql, user_id, start_date, end_date, is_paid, accepted_username_or_first_name, fetchrow=True)

    async def select_payment(self, **kwargs):
        sql = "SELECT * FROM Payment WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def update_payment(self, payment_id, **kwargs):
        set_query = ", ".join(
            [f"{key} = ${i}" for i, key in enumerate(kwargs.keys(), start=2)])
        sql = f"UPDATE Payment SET {set_query}, updated_at = NOW() WHERE id = $1 RETURNING *"
        return await self.execute(sql, payment_id, *kwargs.values(), fetchrow=True)

    async def delete_payment(self, payment_id):
        sql = "DELETE FROM Payment WHERE id=$1 RETURNING *"
        return await self.execute(sql, payment_id, fetchrow=True)

    async def select_all_payments(self):
        sql = "SELECT * FROM Payment"
        return await self.execute(sql, fetch=True)

    # Eski codelar
    # async def create_table_users(self):
    #     sql = """
    #     CREATE TABLE IF NOT EXISTS Users (
    #     id SERIAL PRIMARY KEY,
    #     full_name VARCHAR(255) NOT NULL,
    #     username varchar(255) NULL,
    #     telegram_id BIGINT NOT NULL UNIQUE,
    #     phone_number VARCHAR(20) NOT NULL,
    #     created_at timestamp with time zone NOT NULL DEFAULT NOW()
    #     );
    #     """
    #     await self.execute(sql, execute=True)

    # async def create_table_departmants(self):
    #     sql = """
    #     CREATE TABLE IF NOT EXISTS Departmants (
    #     id SERIAL PRIMARY KEY,
    #     name VARCHAR(255) NOT NULL,
    #     description VARCHAR(255) NULL,
    #     created_at timestamp with time zone NOT NULL DEFAULT NOW()
    #     );
    #     """
    #     await self.execute(sql, execute=True)

    # async def create_table_tests(self):
    #     sql = """
    #     CREATE TABLE IF NOT EXISTS Tests (
    #     id SERIAL PRIMARY KEY,
    #     departmant BIGINT REFERENCES Departmants(id) ON DELETE CASCADE ON UPDATE CASCADE,
    #     file_address VARCHAR(255) NULL,
    #     test_count INT NOT NULL,
    #     answers VARCHAR(255) NOT NULL,
    #     created_user BIGINT REFERENCES Users(telegram_id) ON DELETE CASCADE ON UPDATE CASCADE,
    #     created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
    #     )
    #     """
    #     await self.execute(sql, execute=True)

    # async def create_table_results(self):
    #     sql = """
    #     CREATE TABLE IF NOT EXISTS Results (
    #     id SERIAL PRIMARY KEY,
    #     test BIGINT REFERENCES Tests(id) ON DELETE CASCADE ON UPDATE CASCADE,
    #     telegram_user BIGINT REFERENCES Users(telegram_id) ON DELETE CASCADE ON UPDATE CASCADE,
    #     user_answers VARCHAR(255) NOT NULL,
    #     true_count INT NOT NULL,
    #     created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
    #     )
    #     """
    #     await self.execute(sql, execute=True)

    # # users

    # async def add_user(self, full_name, username, telegram_id, phone_number, created_at):
    #     sql = "INSERT INTO Users (full_name, username, telegram_id, phone_number, created_at) VALUES($1, $2, $3, $4, $5) returning *"
    #     return await self.execute(sql, full_name, username, telegram_id, phone_number, created_at, fetchrow=True)

    # async def select_user(self, **kwargs):
    #     sql = "SELECT * FROM Users WHERE "
    #     sql, parameters = self.format_args(sql, parameters=kwargs)
    #     user = await self.execute(sql, *parameters, fetchrow=True)
    #     return {
    #         "id": user[0],
    #         "full_name": user[1],
    #         "username": user[2],
    #         "telegram_id": user[3],
    #         "phone_number": user[4],
    #     } if user else None

    # # tests
    # async def add_test(self, dept_id, file_address, test_count, answers, created_user, created_at):
    #     sql = "INSERT INTO Tests (departmant, file_address, test_count, answers, created_user, created_at) VALUES($1, $2, $3, $4, $5, $6) returning *"
    #     test = await self.execute(sql, dept_id, file_address, test_count, answers, created_user, created_at, fetchrow=True)
    #     print(f"keyin: {test}")
    #     return {
    #         "id": test[0],
    #         "dept_id": [1],
    #         "file_address": [2],
    #         "test_count": test[3],
    #         "answers": test[4],
    #         "created_user": test[5],
    #         "created_at": test[6]
    #     } if test else None

    # async def select_test(self, **kwargs):
    #     sql = "SELECT * FROM Tests WHERE "
    #     sql, parameters = self.format_args(sql, parameters=kwargs)
    #     test = await self.execute(sql, *parameters, fetchrow=True)
    #     return {
    #         "id": test[0],
    #         "dept_id": test[1],
    #         "file_address": test[2],
    #         "test_count": test[3],
    #         "answers": test[4],
    #         "created_user": test[5],
    #         "created_at": test[6]
    #     } if test else None

    # async def select_tests_from_dept(self, dept_id):
    #     sql = f"SELECT * FROM Tests WHERE departmant={dept_id}"
    #     tests = await self.execute(sql, fetch=True)
    #     return [{
    #         "id": test[0],
    #         "test_count": test[1],
    #         "answers": test[2],
    #         "created_user": test[3],
    #         "created_at": test[4]
    #     } for test in tests
    #     ] if tests else None

    # # add departmant
    # async def add_departmant(self, name, description, created_at):
    #     sql = "INSERT INTO Departmants (name, description, created_at) VALUES($1, $2, $3) returning *"
    #     test = await self.execute(sql, name, description, created_at, fetchrow=True)
    #     return {
    #         "id": test[0],
    #         "name": test[1],
    #         "description": test[2],
    #         "created_at": test[3]
    #     } if test else None

    # async def select_departmant(self, **kwargs):
    #     sql = "SELECT * FROM Departmants WHERE "
    #     sql, parameters = self.format_args(sql, parameters=kwargs)
    #     test = await self.execute(sql, *parameters, fetchrow=True)
    #     return {
    #         "id": test[0],
    #         "name": test[1],
    #         "description": test[2],
    #         "created_at": test[3]
    #     } if test else None

    # async def select_all_departmants(self):
    #     sql = "SELECT * FROM Departmants"
    #     depts = await self.execute(sql, fetch=True)
    #     return [
    #         {
    #             "id": item[0],
    #             "name": item[1],
    #         } for item in depts
    #     ] if depts else None

    # # results
    # async def add_result(self, test, telegram_user, user_answers, true_count, created_at):
    #     sql = "INSERT INTO Results (test, telegram_user, user_answers, true_count, created_at) VALUES($1, $2, $3, $4, $5) returning *"
    #     result = await self.execute(sql, test, telegram_user, user_answers, true_count, created_at, fetchrow=True)
    #     return {
    #         "id": result[0],
    #         "test": result[1],
    #         "user": result[2],
    #         "user_answers": result[3],
    #         "true_answers": result[4],
    #         "created_at": result[5],
    #     } if result else None

    # async def get_result_by_user(self, telegram_id, test_id):
    #     sql = f"SELECT * FROM Results where telegram_user={telegram_id} and test={test_id} Order by created_at DESC LIMIT 1"
    #     result = await self.execute(sql, fetchrow=True)
    #     return {
    #         "id": result[0],
    #         "test": result[1],
    #         "user": result[2],
    #         "user_answers": result[3],
    #         "true_answers": result[4],
    #         "created_at": result[5],
    #     } if result else None

    # async def select_all_users(self):
    #     sql = "SELECT * FROM Users"
    #     return await self.execute(sql, fetch=True)

    # async def select_user(self, **kwargs):
    #     sql = "SELECT * FROM Users WHERE "
    #     sql, parameters = self.format_args(sql, parameters=kwargs)
    #     user = await self.execute(sql, *parameters, fetchrow=True)
    #     return user

    # async def count_users(self):
    #     sql = "SELECT COUNT(*) FROM Users"
    #     return await self.execute(sql, fetchval=True)

    # async def update_user_username(self, username, telegram_id):
    #     sql = "UPDATE Users SET username=$1 WHERE telegram_id=$2"
    #     return await self.execute(sql, username, telegram_id, execute=True)

    # async def delete_users(self):
    #     await self.execute("DELETE FROM Users WHERE TRUE", execute=True)

    # async def drop_users(self):
    #     await self.execute("DROP TABLE Users", execute=True)
