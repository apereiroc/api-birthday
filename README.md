# API-birthday

The name is probably only funny to those who speak Romance languages. Even so, it can help you store and receive notifications of your loved ones' birthdays.

## Start a development server

You'll first need to create an environment file and fill it in

```bash
cp env.sample .env
nvim .env
```

As a guide for non-sensitive information, I use the following

```
APP_ENV=development # or `production`
LOG_LEVEL=debug # or `info`, `warning`, `error`, `critical`
DATABASE_URL=sqlite:///database.db # or  `sqlite://` for in-memory DB
```

Then you can start the API with **uv**

```bash
uv run fastapi dev
```

### Running tests

Tests can be run with 

```bash
uv run pytest -q
```

## Start the bot 

**TODO**

## Start a production server

**TODO**
