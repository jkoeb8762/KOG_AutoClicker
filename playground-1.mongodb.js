// Use or create a database specifically for product keys.
use('ProductKeysDB');

// Create a collection called 'product_keys'.
db.createCollection('product_keys');

// Insert an example document into the product_keys collection.
db.getCollection('product_keys').insertOne({
  "product_key": "ABCD-1234-EFGH-5678",
  "is_activated": false,
  "user_info": {
      "activation_date": null,
      "hardware_id": null  // Field to store the hardware identifier
  }
});
  
// Function to activate a product key with a hardware ID
function activateProductKey(productKey, hardwareID) {
    const keyData = db.getCollection('product_keys').findOne({ "product_key": productKey });
  
    if (!keyData) {
      return "Product key does not exist.";
    }
    if (keyData.is_activated) {
      // Check if the current hardware ID matches the one stored
      if (keyData.user_info.hardware_id === hardwareID) {
        return "Product key is already activated on this device.";
      } else {
        return "Product key is already activated on another device.";
      }
    }
  
    // Activate the key
    db.getCollection('product_keys').updateOne(
      { "product_key": productKey },
      { $set: { "is_activated": true, "user_info.activation_date": new Date(), "user_info.hardware_id": hardwareID } }
    );
    return "Product key activated successfully.";
  }
  
// Example usage:
console.log(activateProductKey("ABCD-1234-EFGH-5678", "HardwareIDFromPythonScript"));
  
// Function to verify a product key and hardware ID
function verifyProductKey(productKey, hardwareID) {
    const keyData = db.getCollection('product_keys').findOne({ "product_key": productKey }, { "user_info.hardware_id": 1, "is_activated": 1 });
  
    if (!keyData) {
      return "Product key does not exist.";
    }
    if (keyData.is_activated && keyData.user_info.hardware_id === hardwareID) {
      return "Product key is activated on this device.";
    } else {
      return "Product key is not activated or is activated on another device.";
    }
  }
  
// Example usage:
console.log(verifyProductKey("ABCD-1234-EFGH-5678", "HardwareIDFromPythonScript"));

  