# Simple demo to show publication usage logs


## File structure
```
    - package.json (for required node modules) + package-lock.json
    - index.js (node)
    - routes.js (node -- for defining api endpoints)
    - api (node, folder for files that define api routes, 1 file per route)
    - pgDB (for connecting to postgres DB with the data, -- pgConfig for credentials *remember to update with your own configs and save as pgConfig.js!)
    -public (front end files-- basic html and js for now)
```

## Running instructions:
1. save a copy of `pgConfig.example.js` as `pgConfig.js`, filling in the placeholder values with your database credentials
2. run `npm install` in root directory
3. run `node index.js` in root directory
4. at this point node server should be running on port 3000
5. navigate to `localhost:3000` on your browser and you should be good to go
6. please use a modern browser... (one that supports webgl)
