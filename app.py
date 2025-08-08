import sqlite3
import os


class BankClientAnalysis:
    def __init__(self, db_file='bank_clients.db'):
        self.db_file = db_file
        self.conn = None

        # Удаляем старую БД если существует
        if os.path.exists(db_file):
            os.remove(db_file)

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_file)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()

    def initialize_database(self):
        """Создание структуры базы данных"""
        with self.conn:
            cursor = self.conn.cursor()

            # Создание таблиц
            cursor.execute('''
                CREATE TABLE clients (
                    client_id INTEGER PRIMARY KEY,
                    active INTEGER NOT NULL,
                    balance REAL NOT NULL
                )
            ''')

            cursor.execute('''
                CREATE TABLE client_details (
                    client_id INTEGER PRIMARY KEY,
                    country TEXT NOT NULL,
                    credit_rating INTEGER NOT NULL,
                    salary REAL NOT NULL,
                    gender TEXT NOT NULL,
                    FOREIGN KEY(client_id) REFERENCES clients(client_id)
                )
            ''')

            cursor.execute('''
                CREATE TABLE cards (
                    card_id INTEGER PRIMARY KEY,
                    client_id INTEGER NOT NULL,
                    card_type TEXT NOT NULL,
                    FOREIGN KEY(client_id) REFERENCES clients(client_id)
                )
            ''')

    def seed_test_data(self):
        """Заполнение базы тестовыми данными"""
        with self.conn:
            cursor = self.conn.cursor()

            # Добавление клиентов
            clients = [
                (1, 0, 150000),  # Неактивный, баланс > 100000
                (2, 1, 200000),  # Активный
                (3, 0, 50000),  # Неактивный, баланс < 100000
                (4, 0, 300000),  # Неактивный, баланс > 100000
                (5, 1, 120000),  # Активный
                (6, 0, 250000),  # Неактивный, баланс > 100000
                (7, 1, 80000),  # Активный
            ]
            cursor.executemany('INSERT INTO clients VALUES (?, ?, ?)', clients)

            # Добавление деталей клиентов
            client_details = [
                (1, 'USA', 700, 60000, 'M'),
                (2, 'Canada', 750, 75000, 'F'),
                (3, 'USA', 650, 50000, 'F'),
                (4, 'Germany', 800, 90000, 'M'),
                (5, 'Canada', 720, 65000, 'F'),
                (6, 'Germany', 780, 85000, 'F'),
                (7, 'France', 710, 70000, 'M'),
            ]
            cursor.executemany('INSERT INTO client_details VALUES (?, ?, ?, ?, ?)', client_details)

            # Добавление карт
            cards = [
                (101, 1, 'Visa'),
                (102, 1, 'MasterCard'),
                (103, 2, 'Visa'),
                (104, 3, 'Amex'),
                (105, 4, 'Visa'),
                (106, 5, 'MasterCard'),
                (107, 6, 'Visa'),
                (108, 6, 'Amex'),
                (109, 7, 'MasterCard'),
            ]
            cursor.executemany('INSERT INTO cards VALUES (?, ?, ?)', cards)

    def execute_query(self, query, title, has_results=True):
        """Выполнение SQL-запроса и вывод результатов"""
        print(f"\n{title}:")
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)

            if not has_results:
                result = cursor.fetchone()
                print(result[0] if result else "Нет данных")
                return

            # Получаем названия столбцов
            columns = [desc[0] for desc in cursor.description]
            results = cursor.fetchall()

            if not results:
                print("Нет данных")
                return

            # Выводим заголовки
            header = " | ".join(columns)
            print(header)
            print("-" * len(header))

            # Выводим данные
            for row in results:
                print(" | ".join(str(item) for item in row))

        except sqlite3.Error as e:
            print(f"Ошибка при выполнении запроса: {e}")

    def run_analysis(self):
        """Выполнение всех аналитических запросов"""
        # 1. Количество неактивных клиентов с балансом > 100000
        self.execute_query(
            "SELECT COUNT(*) FROM clients WHERE active = 0 AND balance > 100000",
            "1. Количество неактивных клиентов с балансом > 100000",
            has_results=False
        )

        # 2. Средний кредитный рейтинг по странам
        self.execute_query(
            "SELECT country, AVG(credit_rating) AS avg_credit_rating "
            "FROM client_details GROUP BY country",
            "2. Средний кредитный рейтинг по странам"
        )

        # 3. Процент ушедших клиентов по типам карт
        self.execute_query(
            '''
            WITH card_clients AS (
                SELECT 
                    c.card_type,
                    COUNT(DISTINCT cl.client_id) AS total_clients,
                    SUM(CASE WHEN cl.active = 0 THEN 1 ELSE 0 END) AS inactive_clients
                FROM cards c
                JOIN clients cl ON c.client_id = cl.client_id
                GROUP BY c.card_type
            )
            SELECT
                card_type,
                (inactive_clients * 100.0 / total_clients) AS churn_percentage
            FROM card_clients
            ''',
            "3. Процент ушедших клиентов по типам карт"
        )

        # 4. Сравнение зарплаты клиента со средней по стране
        self.execute_query(
            '''
            SELECT 
                cd.client_id,
                cd.salary,
                cd.country,
                cd.salary - country_avg.avg_salary AS salary_diff
            FROM client_details cd
            JOIN (
                SELECT 
                    country, 
                    AVG(salary) AS avg_salary
                FROM client_details
                GROUP BY country
            ) AS country_avg ON cd.country = country_avg.country
            ''',
            "4. Сравнение зарплаты клиента со средней по стране"
        )

        # 5. Страны, где в топ-10 зарплат женщин больше, чем мужчин
        self.execute_query(
            '''
            WITH top_salaries AS (
                SELECT 
                    country,
                    gender,
                    ROW_NUMBER() OVER (PARTITION BY country ORDER BY salary DESC) AS salary_rank
                FROM client_details
            )
            SELECT 
                country
            FROM (
                SELECT 
                    country,
                    SUM(CASE WHEN gender = 'F' THEN 1 ELSE 0 END) AS women_count,
                    SUM(CASE WHEN gender = 'M' THEN 1 ELSE 0 END) AS men_count
                FROM top_salaries
                WHERE salary_rank <= 10
                GROUP BY country
            ) AS gender_counts
            WHERE women_count > men_count
            ''',
            "5. Страны, где в топ-10 зарплат женщин больше, чем мужчин"
        )

        # 6. Страны, где используются не все возможные типы карт
        self.execute_query(
            '''
            WITH all_card_types AS (
                SELECT DISTINCT card_type FROM cards
            ),
            country_card_usage AS (
                SELECT 
                    cd.country,
                    c.card_type
                FROM client_details cd
                JOIN cards c ON cd.client_id = c.client_id
                GROUP BY cd.country, c.card_type
            )
            SELECT 
                country
            FROM (
                SELECT 
                    a.country,
                    COUNT(DISTINCT u.card_type) AS used_types,
                    (SELECT COUNT(*) FROM all_card_types) AS total_types
                FROM (SELECT DISTINCT country FROM client_details) a
                LEFT JOIN country_card_usage u ON a.country = u.country
                GROUP BY a.country
            ) AS usage_summary
            WHERE used_types < total_types
            ''',
            "6. Страны, где используются не все возможные типы карт"
        )


if __name__ == "__main__":
    print("Анализ клиентов банка\n" + "=" * 30)

    with BankClientAnalysis() as analyzer:
        # Инициализация базы данных
        analyzer.initialize_database()
        print("База данных создана")

        # Заполнение тестовыми данными
        analyzer.seed_test_data()
        print("Тестовые данные добавлены")

        # Выполнение аналитических запросов
        analyzer.run_analysis()