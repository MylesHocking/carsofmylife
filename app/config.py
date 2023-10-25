import os

SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
else:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:J4sp3rw00@localhost/carsofmylife'

GCP_CREDENTIALS_JSON_STRING = os.environ.get('GCP_CREDENTIALS_JSON_STRING', '''{
  "type": "service_account",
  "project_id": "dynamic-chiller-392810",
  "private_key_id": "262393cbacb3d7867a8b9c7b83070c61c2c19204",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCWYDFFOSPGFNTt\nJtdik5j+w8bZVesRihHIH7fZJLzVzV5jqZGsdJtIbJ0+FH/w2R27kqIF9oMP0h0E\nHDJK23G1wf3hvhAMgiJW7EDsNIhjI7mWWLR/v7pBIQl4AQP10N3ESTZ8AYhjMnuV\nDQH6RLc8z6NSPGmFAVc2chMwPwCAvgkA4bNrtWN5/6d9gz8R7l+PndOgeSj/j/xI\nJnVuBRLgFgvXFZfL0ojWLNy7jym5IhSVSNzB/OUJaKquG569nWkYBCeNayIq3mcf\n7BpaQvEcIOySwXgafAxYyQbAaxTa4i0X0PjP3AfE2bo0EKUsZO/sPHQJq05Cab9J\n2VhBb8QBAgMBAAECggEAA6lSRHZGwxnFFT1f7Nl5uZOhiMv1lwNZVguYG40+gArb\nlI3BXRqoLtJs3mEmZslf5QN3ts3JuJpIe834LKD85aH/EulSamHGVmJ6XRe/6iti\nWQvcbwT5PZ2BXpJfUEHfY5Msj0a9Kq5900bc3BNNeN6/Zcfs5ZYbmpHTtwCg0XNp\nE/XJ7YJXVDB2sRPz7DmXPIpfX9puPzvrUaY6YK8GNITX7p8IbdlyFm/WVSDeQgtd\nD4M/R0ljrVceq6oIsXRGqAawcnPdsArv6wYMFsqKqAjpmo30xaQ9+DOYONduuLqR\nhYMZy54sICxHoogvMvq3ArAd0VLjW2BJ5su04zzT7wKBgQDQCfSNIEz6XZ/0eaHo\nDmoyDp4YAojC2JhlDTuoCYmMRQ05G2KM4VY5FPLW5Y9HGNjOeh9M7m4nJov4q1se\nS3va4CPja+pdd/oaYDoX5IhgEDIvA4+Q1galYh8xOmqU7PM9g5J2FC0tsdlYHkvj\nSC5e7Z4Kzry0OSYhx/iTjAWQ4wKBgQC5CxKZ2oeattHoedNmebuBUySy2uymBWSc\njIhG3DtRjyDQrhYbvD1hSYFX/W7QN7Gds8v3nAyKqeFIneqTJ9AX6C0yM9Svko3j\nbLJf8c756QmChtxgxtKaPRBHu3ruuWrqihT2twSWulE5v+EEqDe1dpTYyE7mwAgd\nLWmjaSigywKBgGGxyx3a5UtNXCg6VkXbPxNyudsclYyqmiYaKMGoeOdeJe+DZKwz\nxYHYzJEODFKe4HFV+AzwitnnyCNmlMuNNwR57WCG9PAfv1tThPRjZYd3E5nwWiLx\n3v0bLvq3LAXzn+ZrOwQoRW8H7cDruUdqRhxeCbGZlBQuIjIK7jibsKFxAoGBAIg3\ncnX3vKNTuaodJFXnfvRwtC9FobeFeM8VVKx1KuWbK1jzDitUowqfBaw0UALPPN0O\nojOgmErrS4AdX7T8Nd+jdsHiDctBY1nrhlPCuc6Wkf2YMVq8ggQwt29Wv+REckQ9\nablEeQhMF8cfTRIUkw3uQRxkOFD9Q/vWllFI9DOJAoGAEBgD+b3lEWFpBqrrmAJd\nnQpoTA0EwyT9CxAVcL3SPTE4ZDiBOZnzih9K4180GtDbiM2CbOCjN2ANVRscD+Sw\nQsnGLoLhamUi9V8mzdP30oCBsxCRu/pKO96KUeOB7VLmc2lSGTAUabPldoLXgekc\nIJDFNCbtLga4IaIzEKXMnPA=\n-----END PRIVATE KEY-----\n",
  "client_email": "1003699094925-compute@developer.gserviceaccount.com",
  "client_id": "100423050056499126493",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/1003699094925-compute%40developer.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}''')

ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', 'http://localhost:3000')

UPLOAD_FOLDER = 'user_images'