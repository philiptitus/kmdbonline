import africastalking

africastalking.initialize(username="joe2022", api_key="aab3047eb9ccfb3973f928d4ebdead9e60beb936b4d2838f7725c9cc165f0c8a")
sms = africastalking.SMS

def send_sms(phone,message):
    recepients = [phone]
    sender = "SOKOGARDEN"
    try:
        response = sms.send(message,recepients)
        print(response)
    except Exception as error:
        print("The error was", error)