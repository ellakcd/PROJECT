from twilio.rest import Client

account_sid = "ACa0c97022f5a3d53d9555f38a47f5c284"
auth_token = "4ed09cb43a89a88c2bf23fc36faae94d"
client = Client(account_sid, auth_token)

# call = client.calls.create(
#     to="+18579981799",
#     from_="+18573203110",
#     url="http://demo.twilio.com/docs/voice.xml"
# )

message = client.api.account.messages.create(
    to="+18579981799",
    from_="+18573203110",
    body="Testing!")

