import rpc

def test_all_servers():
    response = rpc.all_servers()

    assert response.game_servers_address == []
    assert response.master_servers_address == [
        'master1.teeworlds.com:8300',
        'master2.teeworlds.com:8300',
        'master3.teeworlds.com:8300',
        'master4.teeworlds.com:8300'
    ]
