import pytest
from fastapi.testclient import TestClient
from app.main import app, get_db
from app.database import Base, engine
from app.models import URL
from sqlalchemy.orm import sessionmaker

#new session for testing
TestSessionLocal = sessionmaker(autocommit = False,autoflush=False,bind=engine)

@pytest.fixture(autouse=True)
def clear_db():
    #clears the database before every test
    db = next(get_db())
    db.query(URL).delete()
    db.commit()

@pytest.fixture(scope="function")    
def test_db():
    #resets database befor eevery test
    Base.metadata.drop_all(bind=engine) # clear all tables
    Base.metadata.create_all(bind=engine) #recreates tables
    db = TestSessionLocal()
    yield db
    db.close()

client = TestClient(app)

def test_shorten_url():
    response = client.post("/shorten/",json={"long_url":"https://example.com","short_url":"exmpl"})
    print("Response Status Code:", response.status_code)
    print("Response JSON:",response.json())

    assert response.status_code==200
    assert "id" in response.json()
    assert response.json()["long_url"] == "https://example.com"
    assert response.json()["short_url"]  == "exmpl"
   

def test_redirect_url():
    # shortening the url
    shorten_response = client.post("/shorten/",json={"long_url":"https://example.com","short_url":"exmpl"})
    assert shorten_response.status_code == 200
    #retrieve of original url OR redirecting
    

    #Redirect
    redirect_response = client.get("/exmpl")
    assert redirect_response.status_code == 200
    assert redirect_response.json()["long_url"] == "https://example.com"

def test_delete_url():
    shorten_response = client.post("/shorten/",json={"long_url":"https://example.com","short_url":"exmpl"})
    assert shorten_response.status_code == 200

    delete_response = client.delete("/exmpl")
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Short URL deleted successfully"

    # trying to fetch deletd url resulting in 404 error
    fetch_response = client.get("/exmpl")
    assert fetch_response.status_code == 404