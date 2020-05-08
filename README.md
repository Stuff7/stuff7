# Stuff7 (WIP)

Django REST API portfolio.

It consists mainly of REST APIs for bots in streaming platforms supporting both Twitch and Mixer. Featuring an OAuth2 authentication system with these two providers.

### Installation

Install dependencies.
```
pip install -r requirements.txt
```

### Start local development server
```
python manage.py runserver
```

### Start local production server
```
daphne stuff7.asgi:application
```

## Built With
* [Django](https://www.djangoproject.com/)
* [DRF](https://www.django-rest-framework.org/)
* [Requests-OAuthlib](https://requests-oauthlib.readthedocs.io/en/latest/)

## Authors

* **Armando Muñoz** - [Stuff7](https://github.com/Stuff7)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
