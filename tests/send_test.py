from titansemail import SendEmails


def test():
    SendEmails(
        subject='Test email',
        body='Test body',
    )


if __name__ == '__main__':
    test()
