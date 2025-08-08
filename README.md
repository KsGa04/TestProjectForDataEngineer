# Анализ клиентов банка - Решение аналитических задач

## Описание проекта

Проект включает реализацию 6 аналитических задач для банковских клиентов с использованием:

- SQL-запросов
- Реализации на Python
- Автоматического создания тестовой БД

## Структура базы данных

```sql
-- Таблица клиентов
CREATE TABLE clients (
    client_id INTEGER PRIMARY KEY,
    active INTEGER NOT NULL,  -- 0/1
    balance REAL NOT NULL
);

-- Детали клиентов
CREATE TABLE client_details (
    client_id INTEGER PRIMARY KEY,
    country TEXT NOT NULL,
    credit_rating INTEGER NOT NULL,
    salary REAL NOT NULL,
    gender TEXT NOT NULL,  -- 'M'/'F'
    FOREIGN KEY(client_id) REFERENCES clients(client_id)
);

-- Банковские карты
CREATE TABLE cards (
    card_id INTEGER PRIMARY KEY,
    client_id INTEGER NOT NULL,
    card_type TEXT NOT NULL,  -- 'Visa', 'MasterCard', 'Amex'
    FOREIGN KEY(client_id) REFERENCES clients(client_id)
);
```
## Аналитические запросы
1. Количество неактивных клиентов с балансом > 100 000
```sql
SELECT COUNT(*) 
FROM clients 
WHERE active = 0 AND balance > 100000
```
2. Средний кредитный рейтинг по странам
```sql
SELECT country, AVG(credit_rating) 
FROM client_details 
GROUP BY country
```
3. Процент ушедших клиентов по типам карт
```sql
WITH card_clients AS (...)
SELECT card_type, (inactive_clients * 100.0 / total_clients) 
FROM card_clients
```
4. Сравнение зарплаты клиента со средней по стране
```sql
SELECT cd.client_id, cd.salary, cd.country, 
       cd.salary - country_avg.avg_salary 
FROM client_details cd
JOIN (...) country_avg ON cd.country = country_avg.country
```
5. Страны, где в топ-10 зарплат женщин больше, чем мужчин
```sql
WITH top_salaries AS (...)
SELECT country 
FROM (...) 
WHERE women_count > men_count
```
6. Страны, где используются не все возможные типы карт
```sql
WITH all_card_types AS (...)
SELECT country 
FROM (...) 
WHERE used_types < total_types
```
## Инструкции по запуску
Решение на C#
Требования: .NET Core 3.1+

### Установите зависимости:

```bash
dotnet add package System.Data.SQLite
```
### Запустите программу:

```bash
dotnet run
```
Решение на Python
Требования: Python 3.6+

### Установите зависимости:
```bash
pip install sqlite3
```
### Запустите программу:
```bash
python bank_analysis.py
```
### Примеры вывода программы
```text
1. Количество неактивных клиентов с балансом > 100000:
3

2. Средний кредитный рейтинг по странам:
country | avg_credit_rating
----------------------------
Canada  | 735.0
USA     | 675.0

3. Процент ушедших клиентов по типам карт:
card_type   | churn_percentage
------------------------------
Visa        | 66.67%
MasterCard  | 50.00%

4. Сравнение зарплаты клиента со средней по стране:
client_id | salary  | country | difference
------------------------------------------
1         | 60000.0 | USA     | 5000.0
2         | 75000.0 | Canada  | 10000.0

5. Страны, где в топ-10 зарплат женщин больше, чем мужчин:
Germany

6. Страны, где используются не все возможные типы карт:
Canada
France
```