import jwt

token = jwt.encode(
    {'user': 'Alex1', ''},
    algorithm='HS512',
    key='Jopa1',
)


print(token)

data = jwt.decode(token, algorithms='HS512', key='Jopa1')

print(data)