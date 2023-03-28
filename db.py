import psycopg2

conn = psycopg2.connect(dbname='csbot', user='postgres', password='popmenlal', host='127.0.0.1')
cursor = conn.cursor()


'''USERS'''
class users():
    # Создает запись о пользователе, если таковой нет
    def create(message):
        try:
            cursor.execute(f"SELECT user_id FROM users WHERE user_id = {message.chat.id}")
        except:
            conn.rollback()
            return
        
        users_id = cursor.fetchone()
        if users_id == None:
            cursor.execute(f"""INSERT INTO users VALUES({message.chat.id})""")
            conn.commit()


'''OPERATIONS'''
class operations():
    # Создает новое действие
    def new(operation):
        cursor.execute(f"""INSERT INTO operations(user_id, name, quantity, item_id, price, currency_id)
                        VALUES({operation.user_id}, '{operation.name}', {operation.quantity}, {operation.item_id}, {operation.price}, {operation.currency_id});""")
        conn.commit()
        a_quantity = inventories.get.available_quantity(operation.user_id, operation.item_id)

        if a_quantity == None:
            cursor.execute( f"""INSERT INTO inventories(user_id, item_id, quantity)
                                VALUES({operation.user_id}, {operation.item_id}, {operation.quantity});""")
        else:
            inventories.edit(operation.user_id, operation.name, operation.quantity, operation.item_id)

    def edit(oper_id, to_edit, value):
        if type(value) == str:
            cursor.execute(f"UPDATE operations SET {to_edit} = '{value}' WHERE operation_id = {oper_id}")
        else:
            cursor.execute(f"UPDATE operations SET {to_edit} = {value} WHERE operation_id = {oper_id}")
        conn.commit()
    
    class get():
        # Возвращает список всех транзакций пользователя
        def list(message):
            cursor.execute( f"""SELECT operations.name, operations.quantity, operations.price, currencies.name, items.name, operations.operation_id
                                FROM operations
                                LEFT JOIN items USING(item_id)
                                LEFT JOIN currencies USING(currency_id)
                                WHERE user_id = {message.chat.id}""")
            operations = cursor.fetchall()
            return operations

        def operation(operation_id):
            cursor.execute(f"""SELECT * FROM operations WHERE operation_id = {operation_id}""")
            operation = cursor.fetchone()
            return operation

        def selection(user_id):
            cursor.execute(f"""SELECT selection FROM users WHERE user_id = {user_id}""")
            selection = cursor.fetchone()[0]
            return selection
        
        def action(user_id):
            cursor.execute(f"""SELECT action FROM users WHERE user_id = {user_id}""")
            action = cursor.fetchone()[0]
            return action
    
    class add():
        def selection(message, selection):
            cursor.execute (f"""UPDATE users SET selection = {selection} WHERE user_id = {message.chat.id}""")
            conn.commit()
        
        def action(action, user_id):
            cursor.execute(f"""UPDATE users SET action = '{action}' WHERE user_id = {user_id}""")
            conn.commit()

    class delete():
        def operation(operation_id):
            cursor.execute(f"""DELETE FROM operations WHERE operation_id = {operation_id}""")
            conn.commit()

        def selection(user_id):
            cursor.execute(f"UPDATE users SET selection = NULL WHERE user_id = {user_id}")
            conn.commit()

        def action(user_id):
            cursor.execute(f"UPDATE users SET action = NULL WHERE user_id = {user_id}")
            conn.commit()
    

'''CURRENCIES'''
class currencies():
    class get():
        # Получает 2 аргумента. input_data - информация по которой происходит поиск айди валюты
        #                       data_type - тип данных по котором происходит поиск
        def id(input_data, data_type):
            if data_type == 'currency_name':
                cursor.execute(f"SELECT currency_id FROM currencies WHERE name = '{input_data}'")
            else:
                cursor.execute(f"SELECT currency_id FROM users WHERE user_id = {input_data}")
            currencies_id = cursor.fetchone()
            return None if currencies_id == None else currencies_id[0]

        # Принимает аргумент айдишника валюты и возварщает название этой валюты
        def name(cur_id):
            cursor.execute(f"SELECT name FROM currencies WHERE currency_id = {cur_id}")
            currencies_name = cursor.fetchone()[0]
            return currencies_name


'''INVENTORY'''
class inventories():
    def edit(user_id, operation_name, quantity, item_id):
        a_quantity = inventories.get.available_quantity(user_id, item_id)
        if a_quantity == None:
            cursor.execute( f"""INSERT INTO inventories(user_id, item_id, quantity)
                                VALUES({user_id}, {item_id}, {quantity});""")
        else:
            if operation_name == 'sell':
                cursor.execute( f"""UPDATE inventories
                                    SET quantity = (quantity - {quantity})
                                    WHERE user_id = {user_id} AND item_id = {item_id}""")
            else:
                cursor.execute( f"""UPDATE inventories
                                    SET quantity = (quantity + {quantity})
                                    WHERE user_id = {user_id} AND item_id = {item_id}""")
        conn.commit()
    
    class get():
        # Принимает айди пользователя и айди предмета. Возвращает допустимое количество предметов на продажу
        def available_quantity(user_id, item_id):
            try:
                cursor.execute(f"SELECT quantity FROM inventories WHERE user_id = {user_id} AND item_id = {item_id}")
                quantity = cursor.fetchone()
                return None if quantity == None else quantity[0]
            except:
                return None


'''ITEMS'''
class items():
    class get():
        # Принимает аргумент названия предмета и возвращает его id
        def id(item_name):
            cursor.execute(f"""SELECT item_id FROM items WHERE NAME = '{item_name}'""")
            item_id = cursor.fetchone()
            return None if item_id == None else item_id[0]
