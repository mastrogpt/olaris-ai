import sys, os
from pymilvus import MilvusClient,  DataType

if len(sys.argv) < 2:
    print("Usage: python milvus.py (create|delete|list) [<user>] [<password>])")
    sys.exit(1)

host = os.getenv("MILVUS_HOST")
rootpasw = os.getenv("MILVUS_ROOT_PASSWORD")
client = MilvusClient(uri=host, token=f"root:{rootpasw}")

action = sys.argv[1]

if action == "list":
    print("Users:")
    for user in client.list_users():
        print(f"- {user}") 
    sys.exit(0)
 
try:
    user = sys.argv[2]
except:
    user = input(f"Enter user: ")

if action == "delete":
    name =  user
    role_name = f"{name}_role"
    client.drop_user(name)
    print(f"Deleted user {name}") 
    client.drop_collection(name)
    print(f"Deleted collection {name}") 
    try: 
        client.revoke_privilege_v2(role_name=role_name, db_name="default", collection_name=name, privilege="CollectionReadWrite", )
        client.drop_role(role_name)
    except Exception as e:
        print(e.message)
    sys.exit(0)
    
try:
    pasw = sys.argv[3]
except:
    pasw = input(f"Enter password for user {user}: ")
    
name = user
role_name = f"{user}_role"

if not name in client.list_users():
    try:
        client.create_user(name, pasw)
        print(f"Created user {name} with role {role_name}")
    except Exception as e:
        print(e.message)
        sys.exit(0)

if not client.has_collection(name):
    schema = client.create_schema()
    schema.add_field("id", DataType.INT64, is_primary=True)
    schema.add_field("embedding", DataType.FLOAT_VECTOR, dim=1024)
    schema.add_field("text", DataType.VARCHAR, max_length=1024)
    schema.add_field("source", DataType.VARCHAR, max_length=256)
    schema.add_field("group", DataType.VARCHAR, max_length=256)
    client.create_collection(collection_name=name, schema=schema)

    # Define index parameters     
    index_params = client.prepare_index_params()
    index_params.add_index(field_name="embedding", index_type="IVF_FLAT", metric_type="L2", params={"nlist": 128})
    client.create_index(collection_name=name, index_params=index_params)
    print(f"Created collection {name}")
else:
    print(f"Collection {name} already exists")
    

if not role_name in client.list_roles():
    client.create_role(role_name=role_name)
    client.grant_privilege_v2(role_name=role_name, db_name="default", collection_name=name, privilege="CollectionReadWrite")
    print(f"Granted role {role_name} to user {name} for collection {name}")
    client.grant_role(role_name=role_name, user_name=name)


