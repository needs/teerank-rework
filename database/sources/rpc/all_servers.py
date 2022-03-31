import database_pb2

def all_servers() -> database_pb2.AllServersResponse:
    return database_pb2.AllServersResponse(game_servers_address=[
    ], master_servers_address=[
        'master1.teeworlds.com:8300',
        'master2.teeworlds.com:8300',
        'master3.teeworlds.com:8300',
        'master4.teeworlds.com:8300'
    ])
