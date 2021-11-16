import * as dotenv from "dotenv";

let path;

switch (process.env.NODE_ENV) {
  case "development":
    console.log("Loaded development enviroment configs");
    path = `${__dirname}/../.env.development`;
    break;
  case "production":
    console.log("Loaded production enviroment configs");
    path = `${__dirname}/../.env`;
    break;
  default:
    console.log("Loaded default enviroment configs");
    path = `${__dirname}/../.env.development`;
}

dotenv.config({ path });
