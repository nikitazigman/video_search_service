from abc import ABC, abstractmethod

from psycopg import Connection, rows, sql

from cdn_worker.schemas import edge_nodes as edge_node_schemas


class IEdgeNodeRepository(ABC):
    @abstractmethod
    def get_all(self) -> None:
        raise NotImplementedError


class PostgresEdgeNodeRepository(IEdgeNodeRepository):
    def __init__(self, db_connection: Connection) -> None:
        self.conn = db_connection

        self.conn.row_factory = rows.dict_row

    def get_all(self) -> list[edge_node_schemas.EdgeNode]:
        query = sql.SQL("SELECT * FROM cdn_api.edge_nodes")

        with self.conn.cursor() as curs:
            curs.execute(query)
            data = curs.fetchall()

        return [edge_node_schemas.EdgeNode.model_validate(row) for row in data]
