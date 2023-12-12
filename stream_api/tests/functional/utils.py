import psycopg
import psycopg.rows
import psycopg.sql


async def truncate_db_tables(cursor: psycopg.AsyncCursor) -> None:
    schema = "cdn_api"

    async with cursor as curs:
        query = psycopg.sql.SQL(
            "SELECT table_name FROM information_schema.tables "
            f"WHERE table_schema = '{schema}'".format(
                schema=psycopg.sql.Identifier(schema)
            )
        )
        await curs.execute(query)
        result = await curs.fetchall()

        for row in result:
            table_name = row["table_name"]
            query = psycopg.sql.SQL(
                "TRUNCATE TABLE {schema}.{table} RESTART IDENTITY CASCADE"
            ).format(
                table=psycopg.sql.Identifier(table_name),
                schema=psycopg.sql.Identifier(schema),
            )
            await curs.execute(query)
            await curs.connection.commit()
