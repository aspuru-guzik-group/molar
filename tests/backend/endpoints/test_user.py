def add_user(client, user, password, )
    

def test_get_users(client, username = None, password = None, database = 'molar_main'):
    if username if None:
        username = os.getenv("MOLAR_SUPERUSER") or "test@molar.tooth"
    if password is None:
        password = os.getenv('MOLAR_PASSWORD') or 'tooth'

    out = client.get('/api/v1/usets/get-users/', )
    pass
