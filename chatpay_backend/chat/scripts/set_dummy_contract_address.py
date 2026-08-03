from chat.models import Room

def set_dummy_contract_address():
    dummy_address = 'bitcoincash:dummyaddress'
    rooms = Room.objects.all()
    for room in rooms:
        room.contract_address = dummy_address
        room.save()
        print(f"Set contract_address for Room {room.id} ({room.name}) to {dummy_address}")

if __name__ == '__main__':
    set_dummy_contract_address() 