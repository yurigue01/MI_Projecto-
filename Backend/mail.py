import smtplib

sender = "Private Person <from@example.com>"
receiver = "A Test User  ccc <to@example.com>"



server = smtplib.SMTP("sandbox.smtp.mailtrap.io", 2525)
server.login("92463ddfaf41ea", "7a3617bc2177ef")


def send(username,email):
        message = f"""\
        Subject: Hi Mailtrap
        To: {receiver}
        From: {sender}
        usename: {username}
        email: {email}

        This is a test e-mail message."""
        server.sendmail(sender, receiver,message)
        