import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "orm.db")


class Field:
    def __init__(self, column_type, nullable=False, unique=False):
        self.column_type = column_type
        self.nullable = nullable
        self.unique = unique
        self.name = None

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        return instance.__dict__.get(self.name)

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value


class CharField(Field):
    def __init__(self, max_length=255, **kwargs):
        super().__init__(f"VARCHAR({max_length})", **kwargs)


class IntegerField(Field):
    def __init__(self, **kwargs):
        super().__init__("INTEGER", **kwargs)


class ForeignKey(Field):
    def __init__(self, model, related_name=None):
        super().__init__("INTEGER")
        self.model = model
        self.related_name = related_name


class ModelMeta(type):
    def __new__(cls, name, bases, attrs):
        fields = {}

        for key, value in attrs.items():
            if isinstance(value, Field):
                fields[key] = value

        attrs["_fields"] = fields
        attrs["_table"] = name.lower()

        return super().__new__(cls, name, bases, attrs)


class QuerySet:
    def __init__(self, model):
        self.model = model
        self.conditions = []
        self.order = ""

    def filter(self, **kwargs):
        for key, value in kwargs.items():
            if "__gte" in key:
                field = key.split("__")[0]
                self.conditions.append(f"{field} >= {value}")
        return self

    def order_by(self, field):
        if field.startswith("-"):
            self.order = f"ORDER BY {field[1:]} DESC"
        else:
            self.order = f"ORDER BY {field} ASC"
        return self

    def all(self):
        where = " AND ".join(self.conditions)
        where_clause = f"WHERE {where}" if where else ""

        sql = f"SELECT * FROM {self.model._table} {where_clause} {self.order};"

        print("SQL:", sql)

        conn = sqlite3.connect(db_path)
        rows = conn.execute(sql).fetchall()
        conn.close()

        # ✅ CHANGED: return objects instead of tuples
        objects = []
        for row in rows:
            obj = self.model()
            obj.id = row[0]
            for i, field in enumerate(self.model._fields):
                setattr(obj, field, row[i + 1])
            objects.append(obj)

        return objects


class Model(metaclass=ModelMeta):

    def __init__(self, **kwargs):
        for field_name in self._fields:
            setattr(self, field_name, kwargs.get(field_name))

    def __repr__(self):
        fields = []

        for field in self._fields:
            value = getattr(self, field, None)
            fields.append(f"{field}='{value}'")

        return f"{self.__class__.__name__}(id={getattr(self, 'id', None)}, {', '.join(fields)})"

    @classmethod
    def create_table(cls):
        columns = ["id INTEGER PRIMARY KEY AUTOINCREMENT"]
        foreign_keys = []

        for name, field in cls._fields.items():

            if isinstance(field, ForeignKey):
                col_name = f"{name}_id"
                col = f"{col_name} INTEGER"

                if not field.nullable:
                    col += " NOT NULL"

                columns.append(col)

                foreign_keys.append(
                    f"FOREIGN KEY ({col_name}) REFERENCES {field.model._table}(id)"
                )

            else:
                col = f"{name} {field.column_type}"

                if not field.nullable:
                    col += " NOT NULL"
                if field.unique:
                    col += " UNIQUE"

                columns.append(col)

        sql = f"CREATE TABLE IF NOT EXISTS {cls._table} ({', '.join(columns + foreign_keys)});"

        print("SQL:", sql)

        conn = sqlite3.connect(db_path)
        conn.execute(sql)
        conn.close()

        print(f"Table '{cls._table}' created.\n")

    def save(self):
        fields = []
        values = []

        for name, field in self._fields.items():
            value = getattr(self, name)

            if isinstance(field, ForeignKey):
                fields.append(f"{name}_id")
                values.append(value.id if value else None)
            else:
                fields.append(name)
                values.append(value)

        placeholders = ", ".join(["?"] * len(values))

        sql = f"INSERT INTO {self._table} ({', '.join(fields)}) VALUES ({placeholders})"

        print("SQL:", sql)

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(sql, values)
        conn.commit()

        self.id = cursor.lastrowid  
        conn.close()

        print(f"Record saved: {self}\n")

    def delete(self):
        # ✅ FIXED: now guaranteed working
        sql = f"DELETE FROM {self._table} WHERE id = ?"

        print("SQL:", sql)

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(sql, (self.id,))
        conn.commit()
        conn.close()

        print(f"Deleted: {self}\n")

    @classmethod
    def filter(cls, **kwargs):
        return QuerySet(cls).filter(**kwargs)

    def __getattr__(self, item):
        for model in Model.__subclasses__():
            for field_name, field in model._fields.items():
                if isinstance(field, ForeignKey) and field.related_name == item:

                    sql = f"SELECT * FROM {model._table} WHERE {field_name}_id = {self.id}"

                    print("SQL:", sql)

                    conn = sqlite3.connect(db_path)
                    rows = conn.execute(sql).fetchall()
                    conn.close()

                    result = []
                    for row in rows:
                        obj = model()
                        obj.id = row[0]
                        for i, f in enumerate(model._fields):
                            setattr(obj, f, row[i + 1])
                        result.append(obj)

                    return result

        raise AttributeError(f"{item} not found")



class User(Model):
    name = CharField(max_length=100)
    email = CharField(unique=True)
    age = IntegerField(nullable=True)


class Post(Model):
    title = CharField()
    author = ForeignKey(User, related_name="posts")


User.create_table()
Post.create_table()


alice = User(name="Alice", email="alice@example.com", age=30)
alice.save()
alice1 = User(name="Vaibhav", email="vaibhav@example.com", age=40)
alice1.save()
alice2 = User(name="Raghav", email="raghav@example.com", age=20)
alice2.save()


post = Post(title="Hello World", author=alice)
post.save()
post1 = Post(title="Hi I am Vaibhav", author=alice1)
post1.save()
post2 = Post(title="Hello, I am VG", author=alice1)
post2.save()


users = User.filter(age__gte=25).order_by("-name").all()
print("\n-------------Users whose age more than 25---------------\n ")
print(users,"\n")


print("\n----------------- Posts------------------------\n ")
print(alice1.posts,"\n")


post.delete()
alice.delete()