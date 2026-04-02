from decoraters import skip,parameter

@parameter("product_id,quantity",[("p1", 6),("p2", 5)])
def test_add_item(product_id,quantity):
    assert True

@parameter("product_id",[("p1"),("p2")])
def test_remove_item(product_id):
    assert True

@parameter("product_id,quantity",[("p1", 6),("p2", 5)])
def test_update_item(product_id,quantity):
    assert True

def test_clear_cart():
    assert True

def test_checkout():
    assert True

@skip("Not implemented")
def test_payment():
    assert False