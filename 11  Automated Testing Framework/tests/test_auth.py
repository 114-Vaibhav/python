from decoraters import parameter

@parameter("user,passwd",[("user1", "pass1"),("user2", "pass2")])
def test_login_valid_credentials(user,passwd):
    # print("user: ",user)
    # print(" pass: ",passwd)
    assert True


@parameter("user,passwd",[("user1", "pass1"),("user2", "pass2")])
def test_login_invalid_credentials(user,passwd):
    assert True


@parameter("user,passwd",[("user1", "pass1"),("user2", "pass2")])
def test_login_expired_token(user,passwd):
    assert True

