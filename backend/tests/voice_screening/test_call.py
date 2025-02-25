from twilio.rest import Client

# Your Account SID and Auth Token from twilio.com/console
account_sid = 'AC2dd7a301619d0ae449ada741a35ed235'
auth_token = 'fb4643331618e56c7be9a32aedbc252b'
client = Client(account_sid, auth_token)

call = client.calls.create(
    to='+919007696846',
    from_='+19034005920',
    twiml='<Response><Say>Hello, this is a test call from Twilio.</Say></Response>'
)

print(f"Call SID: {call.sid}")