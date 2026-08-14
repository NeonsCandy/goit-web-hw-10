from mongoengine import connect, Document, StringField, ReferenceField, ListField, CASCADE

connect(host="mongodb+srv://neons:querty123456@neons.8ahf9id.mongodb.net/hw8?appName=neons")

class Author(Document):
    fullname = StringField(required=True, unique=True)
    born_date = StringField(max_length=50)
    born_location = StringField(max_length=150)
    description = StringField()

class Quote(Document):
    tags = ListField(StringField(max_length=50))
    author = ReferenceField(Author, reverse_delete_rule=CASCADE)
    quote = StringField()