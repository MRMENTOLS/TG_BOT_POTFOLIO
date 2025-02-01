import sqlite3

DATABASE = 'projects.db'

class DB_Manager:
    def __init__(self, database):
        self.database = database
        self.__connect()

    def __connect(self):
        self.conn = sqlite3.connect(self.database)
        self.cursor = self.conn.cursor()

    def __execute(self, sql, data = None):
        if data:
            self.cursor.execute(sql, data)
        else:
            self.cursor.execute(sql)
        self.conn.commit()
        

    def __executemany(self, sql, data):
        self.cursor.executemany(sql, data)
        self.conn.commit()

    def __select_data(self, sql, data=None):
       if data:
         self.cursor.execute(sql, data)
       else:
        self.cursor.execute(sql)
       res = self.cursor.fetchall()
       return res
    
    def default_insert(self):
        try:
            self.__execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT NOT NULL,
                password TEXT NOT NULL
            )
        """)
            self.__execute("""
            CREATE TABLE IF NOT EXISTS status (
                status_id INTEGER PRIMARY KEY AUTOINCREMENT,
                status_name TEXT NOT NULL
            )
        """)
            self.__execute("""
            CREATE TABLE IF NOT EXISTS projects (
                project_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                project_name TEXT NOT NULL,
                description TEXT,
                url TEXT,
                status_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (status_id) REFERENCES status (status_id)
            )
        """)
            self.__execute("""
            CREATE TABLE IF NOT EXISTS skills (
                skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
                skill_name TEXT NOT NULL
            )
        """)
            self.__execute("""
            CREATE TABLE IF NOT EXISTS project_skills (
                project_id INTEGER NOT NULL,
                skill_id INTEGER NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects (project_id),
                FOREIGN KEY (skill_id) REFERENCES skills (skill_id),
                PRIMARY KEY (project_id, skill_id)
            )
        """)
            self.__executemany("INSERT INTO status (status_name) VALUES (?)", [('in progress',), ('completed',)])
        except:
           return 
    
    def create_user(self, username, email, password):
       sql = "INSERT INTO users (username, email, password) VALUES (?,?,?)"
       self.__execute(sql=sql, data=(username,email, password))

    def get_user(self, email):
        sql = "SELECT user_id, username, email, password FROM users WHERE email = ?"
        return self.__select_data(sql=sql, data=(email,))
    
    def create_project(self, user_id, project_name, description, url, status_id):
       sql = """
       INSERT INTO projects (user_id, project_name, description, url, status_id)
       VALUES (?,?,?,?,?)
       """
       self.__execute(sql=sql, data=(user_id, project_name, description, url, status_id))

    def create_skill(self, skill_name):
        sql = "INSERT INTO skills (skill_name) VALUES (?)"
        self.__execute(sql=sql, data=(skill_name,))

    def add_skill_to_project(self, project_id, skill_id):
        sql = "INSERT INTO project_skills (project_id, skill_id) VALUES (?,?)"
        self.__execute(sql, (project_id, skill_id))

    def get_skills_project(self, project_id):
        sql = """
        SELECT skills.skill_name FROM skills
        JOIN project_skills ON project_skills.skill_id = skills.skill_id
        WHERE project_skills.project_id = ?
        """
        return [x[0] for x in self.__select_data(sql=sql, data=(project_id,))]
    
    def get_projects(self, user_id):
        sql = """
SELECT project_name, description, url, status_name FROM projects 
JOIN status ON
status.status_id = projects.status_id
WHERE user_id=?
"""
        res = self.__select_data(sql=sql, data = (user_id,))
        return [', '.join([str(y) for y in x]) for x in res]
    
    def get_project_info(self, user_id, project_name):
        sql = """
SELECT project_name, description, url, status_name FROM projects 
JOIN status ON
status.status_id = projects.status_id
WHERE project_name=? AND user_id=?
"""
        return self.__select_data(sql=sql, data = (project_name, user_id))


    def update_projects(self, param, data):
        sql = f"UPDATE projects SET {param} = ? WHERE project_name = ? AND user_id = ?" # Запиши сюда правильный SQL запрос
        self.__executemany(sql, [data]) 


    def delete_project(self, user_id, project_id):
        sql = "DELETE FROM projects WHERE user_id = ? AND project_id = ?" # Запиши сюда правильный SQL запрос
        self.__executemany(sql, [(user_id, project_id)])
    
    def delete_skill(self, project_id, skill_id):
        sql = "DELETE FROM project_skills WHERE skill_id = ? AND project_id = ?" # Запиши сюда правильный SQL запрос
        self.__executemany(sql, [(skill_id, project_id)])


if __name__ == '__main__':
    manager = DB_Manager(DATABASE)
    manager.default_insert()
