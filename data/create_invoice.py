# https://doc.cryptomus.com/getting-started/request-format
# headers = {
# merchant: The merchant's uuid, which you can find in the merchant's personal account in the settings section.
# sign: MD5 hash of the body of the POST request encoded in base64 and combined with your API key.
# }

# CREATE INVOICE
# endpoint
# method = "post"
# url = "https://api.cryptomus.com/v1/payment"
# params = {
# 'amount' : "7.99",
# 'currency' : "USDT",
# 'order_id' : str(uuid.uuid4()),
# 'url_success' : "https://t.me/cryptocurrencies_alert_bot",
# 'subtract' : 100  ,# user pay 100% of fees
# 'url_callback' : "my webhook"   ,
# }
#

# # CREATE QR CODE FOR INVOICE
# url = "https://api.cryptomus.com/v1/payment/qr"
# merchant_invoice_uuid = result["result"]["uuid"]
