from pymongo.mongo_client import MongoClient
import urllib.parse
import os

User = os.environ['DB_User']
Pswd = os.environ['DB_Pswd']

username = urllib.parse.quote_plus(User)
password = urllib.parse.quote_plus(Pswd)

uri = 'mongodb+srv://%s:%s@atlascluster.y97yrgj.mongodb.net/?retryWrites=true&w=majority&appName=AtlasCluster'

# Create a new client and connect to the server
client = MongoClient(uri % (username, password))

db = client['telegram_bot']
collection = db['data_collection']

class database():
    def __init__(self):
        pass

    def store_data(self,key, data):
        query = {'key': key}
        document = collection.find_one(query)

        if document:
            # 键存在，执行 update_one，覆盖原key防止重复插入
            update_query = {'$set': {'value': data}}
            collection.update_one(query, update_query)
            # print(f"Updated document with key: {key}")
        else:
            # 键不存在，执行 insert_one
            document = {'key': key, 'value': data}
            collection.insert_one(document)
            # print(f"Inserted document with key: {key}")

        return None

    def get_data(self,key):
        retrieved_document = collection.find_one({'key': key})
        if retrieved_document:
            value = retrieved_document['value']
            return value
        else:
            print('No document found with that key.')
            return None

    def delete_data(self,key):
        collection.delete_one({'key': key})
        return None

if __name__ == '__main__':
    test = database()
    test.store_data('user1','Hong Kong')
    value = test.get_data('user1')
    print(value)
    # test.delete_data('user1')


# # 存储键值对，这里的键值对以文档形式存储
# key_value_data = {'key': 'user1', 'value': 'yuxin'}
# result = collection.insert_one(key_value_data)
# print(f'Inserted document with id: {result.inserted_id}')
#
# # 检索键值对
# retrieved_document = collection.find_one({'key': 'user1'})
# if retrieved_document:
#     value = retrieved_document['value']
#     print(f'get value: {value}')
# else:
#     print('No document found with that key.')

# # 删除整个文档
# collection.delete_one({'key': 'user1'})
#
# # 验证文档是否被删除
# retrieved_document = collection.find_one({'key': 'user1'})
# if retrieved_document:
#     print('Document still exists.')
# else:
#     print('Document successfully deleted.')