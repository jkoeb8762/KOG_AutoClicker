from pymongo import MongoClient
from datetime import datetime

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client.ProductKeysDB

def get_hardware_id():
    """Get the hardware ID (MAC address) of the device."""
    mac = uuid.getnode()
    mac_address = ':'.join(('%012X' % mac)[i:i+2] for i in range(0, 12, 2))
    return mac_address

def activate_product_key(product_key, hardware_id):
    """Activate a product key with a hardware ID."""
    key_data = db.product_keys.find_one({ "product_key": product_key })

    if not key_data:
        return "Product key does not exist."
    if key_data['is_activated']:
        if key_data['user_info']['hardware_id'] == hardware_id:
            return "Product key is already activated on this device."
        else:
            return "Product key is already activated on another device."

    db.product_keys.update_one(
        { "product_key": product_key },
        { "$set": { "is_activated": True, "user_info.activation_date": datetime.now(), "user_info.hardware_id": hardware_id } }
    )
    return "Product key activated successfully."

def verify_product_key(product_key, hardware_id):
    """Verify a product key and hardware ID."""
    key_data = db.product_keys.find_one({ "product_key": product_key }, { "user_info.hardware_id": 1, "is_activated": 1 })

    if not key_data:
        return "Product key does not exist."
    if key_data['is_activated'] and key_data['user_info']['hardware_id'] == hardware_id:
        return "Product key is activated on this device."
    else:
        return "Product key is not activated or is activated on another device."

# Example usage
hardware_id = get_hardware_id()
print(activate_product_key("ABCD-1234-EFGH-5678", hardware_id))
print(verify_product_key("ABCD-1234-EFGH-5678", hardware_id))
