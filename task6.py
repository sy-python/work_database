import psycopg2
import time
import threading


def get_connection():
    return psycopg2.connect(
        dbname="tasks",
        user="postgres",
        password="postgres",
        host="localhost",
        port=5432,
    )


def initialize():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            task_name TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            worker_id INTEGER DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    conn.commit()
    cursor.close()
    conn.close()


def add_task(task_name: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (task_name) VALUES (%s)", (task_name,))
    conn.commit()
    cursor.close()
    conn.close()


def fetch_task(worker_id: int):
    conn = get_connection()
    conn.autocommit = False
    cursor = conn.cursor()
    try:
        cursor.execute("BEGIN")
        cursor.execute(
            """SELECT id, task_name
               FROM tasks
               WHERE status = 'pending'
               ORDER BY created_at ASC
               LIMIT 1
               FOR UPDATE SKIP LOCKED"""
        )
        task = cursor.fetchone()
        if task:
            cursor.execute(
                """UPDATE tasks
                   SET status = 'processing', worker_id = %s, updated_at = CURRENT_TIMESTAMP 
                   WHERE id = %s
                """,
                (worker_id, task[0]),
            )
            conn.commit()
            return task
        else:
            conn.commit()
            return None
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def process_task(worker_id):
    task = fetch_task(worker_id)
    if task is None:
        return None

    print(f"Worker {worker_id} is processing task {task[1]}")
    time.sleep(5)

    conn = get_connection()
    conn.autocommit = False
    cursor = conn.cursor()
    try:
        cursor.execute("BEGIN")
        cursor.execute(
            """UPDATE tasks
               SET status = 'completed', worker_id = NULL, updated_at = CURRENT_TIMESTAMP 
               WHERE id = %s
            """,
            (task[0],),
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()
