# Avatair Web

## Structure

The project is structured into the ui-backend server (sveltekit) in ./web-app

And the api-backend server (nestjs) in ./nestjs

The root folder (.) containes helper scripts

## Helpers

- `npm run install` installs dependencies for both (ui & backend).
- `npm run build` build the project for both (ui & backend). Needs to be installed first.
- `npm run docker-build` build docker container for both (ui & backend). Needs to be build first.
- `npm run docker-deploy` deploys the docker-compose file (`compose up -d`).
- `npm run deploy` runs all commands above in sequence.

To deploy the system on localhost
move and edit example.env to .env.

then, just run

```bash
npm run deploy
```

Open http://localhost:5555

## Caution!

Keep in mind

```bash
npm run deploy
```

does not create any secure secrets.

**You must change everything flagged as
`changeme` and
`changemetobethesame`
in the .env file.**

In production, set:

`PUBLIC_BACKEND_API_URL` var to your public api-server url (e.g., https://myserver.website/api/)
and

`PUBLIC_FRONTEND_URL` to your public frontend url (e.g., https://myserver.website/)

## Dependencies

The project uses the following frameworks:

- [NestJS](https://nestjs.com/)
- [SvelteKit](https://kit.svelte.dev/)
- [MongoDB](https://www.mongodb.com/)

A mongo-express instance is running automatically when run with docker compose.

## Development

Backend:

```bash

# Change directory
cd nestjs

# run the dev database and mongo-express
docker compose up -d 

# Install package dependencies
npm install

# Run
npm run dev
```

Frontend:

```bash
# Change directory
cd web-app
# Install package dependencies
npm install
# Run
npm run dev
```

Once both the frontend and backend are running, visit http://localhost:5555 to view the website.

For API documentation, visit http://localhost:3000.

## Development Database

The database has no persistence in this configuration.
When compose down the database, all data is lost.
To prevent this, mount the mongodb drive:

```
volumes:
 - ./dbdata:/data/db
```

in ./nestjs/docker-compose.yaml
